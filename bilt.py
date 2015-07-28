import time
import json
import collections
import socket

class SocketObj:
    def __init__(self, address, port):
        self.__connect(address, port)
        self.has_errored = False

    def __connect(self, address, port):
        s = socket.socket()
        s.connect((str(address), port))
        self.s = s
        self.port = port
        self.address = address

    def __socket_call(self, func, args):
        retVal = None
        try:
            retVal = func(args)
        except IOError as e:
            # reraise if it's happened before
            if self.has_errored: raise e
            # otherwise try a reconnect
            self.has_errored = True
            self.__connect(self.address, self.port)
            retVal = self.__socket_call(func, args)
        self.has_errored = False
        return retVal

    def __send(self, args):
        return self.__socket_call(self.s.send, args)

    def __recv(self, args):
        return self.__socket_call(self.s.recv, args)

    def ask(self, cmd):
        astr = ""
        self.__send(cmd + "\n")
        while 1:
            r = self.__recv(4096)
            if not r: break
            astr += r
            if r.find('\n') != -1: break
        return astr.rstrip()

    def write(self, cmd):
        self.__send(cmd + "\n")
        time.sleep(0.2)


class Bilt():
    def __init__(self, conf = "sources.dict"):
        """ Constructor.

        Keyword argument:
        conf -- file containing a json dictionary to read configuration from (default: sources.dict)
        """
        self.sources = self.readconfig(conf)
        self.look_up = dict([(self.sources[k]["CoilName"],k) for k in self.sources])
        self.initComm()

    def initComm(self, ip="currentsource.1.nedm1"):
        """ Initalizes communication with device via visa.

        Keyword argument:
        ip -- IP adress of the source, defaults to 192.168.1.251
        """
        self.s = SocketObj(str(ip), 5025)

    def _get_adress(self, cn):
        """ Get source address from nr or coilname. """
        try:
            if isinstance(cn, int):
                adr = self.sources[str(cn)]["Name"]
                nr = cn
            else:
                adr = self.sources[self.look_up[cn]]["Name"]
                nr = self.look_up[cn]
        except KeyError as e:
            raise e
        return adr, int(nr)

    def on(self, cn):
        """ Switch on source nr."""
        adr, nr = self._get_adress(cn)
        self.setvoltrange(nr, self.sources[str(nr)]["SetVoltRange"])
        self.setvoltage(nr, self.sources[str(nr)]["SetVolt"])
        self.s.write(adr + " outp on")

    def off(self, cn):
        """ Switch off source nr."""
        adr, nr = self._get_adress(cn)
        self.s.write(adr + " outp off")

    def setvoltage(self, cn, volt=0.0):
        """ Set voltage for source nr to volt."""
        adr, nr = self._get_adress(cn)
        if volt <= self.sources[str(nr)]["SetVoltRange"]:
            self.s.write(adr + " volt " + str(volt))
            self.sources[str(nr)]["SetVolt"] = volt
        else:
            raise Exception("Voltage out of range, setvoltrange first, set: %s, available ranges: %s" % (str(self.sources[str(nr)]["SetVoltRange"]), str(self.sources[str(nr)]["VoltRanges"])))

    def setcurrent(self, cn, curr=0.0):
        """ Set current for source nr to curr."""
        adr, nr = self._get_adress(cn)
        if curr <= self.sources[str(nr)]["SetCurrRange"]:
            self.s.write(adr + " curr " + str(curr))
            self.sources[str(nr)]["SetCurr"] = curr
        else:
            raise Exception("Current out of range, setcurrrange first, set: %s, available ranges: %s" % (str(self.sources[str(nr)]["SetCurrRange"]), str(self.sources[str(nr)]["CurrRanges"])))

    def setvoltrange(self, cn, ran):
        """ Set voltage range for source nr to ran."""
        adr, nr = self._get_adress(cn)
        if ran in self.sources[str(nr)]["VoltRanges"]:
            self.s.write(adr + " volt:rang:auto off")
            self.s.write(adr + " volt:rang" + str(ran))
            self.sources[str(nr)]["SetVoltRange"] = ran
        else:
            raise Exception("range not available, possible are %s" % str(self.sources[str(nr)]["VoltRanges"]))

    def setcurrentrange(self, cn, ran):
        """ Set current range for source nr to ran."""
        adr, nr = self._get_adress(cn)
        if ran in self.sources[str(nr)]["CurrRanges"]:
            self.s.write(adr + " curr:rang:auto off")
            self.s.write(adr + " curr:rang" + str(ran))
            self.sources[str(nr)]["SetCurrRange"] = ran
        else:
            raise Exception("range not available, possible are %s" % str(self.sources[str(nr)]["CurrRanges"]))

    def getvoltage(self, cn):
        """ Returns currently set voltage for source nr."""
        return self.userask(cn, " meas:volt ?")

    def getcurrent(self, cn):
        """ Returns currently set current for source nr."""
        return self.userask(cn, " meas:curr ?")

    def getvoltrange(self, cn):
        """ Returns currently set voltage range for source nr."""
        return self.userask(cn, "volt:range ?")

    def getcurrentrange(self, cn):
        """ Returns currently set current range for source nr."""
        return self.userask(cn, "curr:range ?")

    def clearstatus(self, cn):
        self.userwrite(cn, "stat:clear")

    def userask(self, cn, cmd):
        adr, nr = self._get_adress(cn)
        return self.s.ask(adr + cmd)

    def userwrite(self, cn, cmd):
        adr, nr = self._get_adress(cn)
        self.s.write(adr + cmd)

    def readconfig(self, conf):
        """ Reads configurations from file conf and return dictionary."""
        with open(str(conf), "r") as f:
            sources = json.loads(f.read())
        return sources

    def saveconfig(self, fil):
        """ Saves configuration to file fil."""
        with open(str(fil), "w") as f:
            f.write(json.dumps(self.sources, indent=4, separators = (',', ' : ')))

    def readallerrors(self):
        ret_array = []
        while 1:
            rbck = self.s.ask("syst:err?")
            if rbck[:4] == '+000': break
            ret_array.append(rbck)
        if len(ret_array) == 0: ret_array = ["No errors"]
        return ret_array
    def setup_ramp(self, adict):
        time_length = float(adict.get("time_length", 1.))
        all_keys = adict.get("channels", {})
        scpi_cmds = ["", "", ""]
        total_steps = int(10*time_length)
        i = 0
        for v in all_keys:
            v['addr'] = self.sources[str(v['nr'])]["Name"]
            for l in ['min', 'max']:
                v[l] = float(v[l])
            v['step_size'] = (v['max'] - v['min'])/float(total_steps)
            if i < 10:
                v["var_name"] = "0"
            v["var_name"] += str(i)
            i += 1
            scpi_cmds[0] += "var%(var_name)s,%(min)g;" % v
            scpi_cmds[1] += "%(addr)s:%(type)s #%(var_name)s#;:" % v
            v["comp"] = "ifge"
            if v['step_size'] < 0:
               v["comp"] = "ifle"
            v['max'] -= v['step_size']/2.
        for v in all_keys:
            scpi_cmds[1] += "var%(var_name)s:add %(step_size)g;:" % v
        for v in all_keys:
            scpi_cmds[1] += "var%(var_name)s:%(comp)s %(max)s;:p:stat off;:" % v

        ar = """var:ar off
p1; p:stat off; p:def
p:mac0,1,0,0,"%s"
p:mac1,1,0,1,"%s"
p:mac2,0,0,0,""
p:mac:atrestart2 ; reinit""" % (scpi_cmds[0][:-1], scpi_cmds[1][:-2])
        map(self.s.write, ar.split('\n'))
        return True

    def read_macro_data(self):
        return_list = []
        self.s.write("p1")
        query_str = "p:mac:set?"
        while 1:
            anstr = self.s.ask(query_str)
            query_str = "p:mac:set:next?"
            if anstr == 'END':
                break
            return_list.append(anstr)
        return return_list

    def stop_macro(self):
        self.s.write("p1; p:stat off")

    def run_ramp(self):
        self.stop_macro()
        self.s.write("p1; p:stat on")

    def read_macro_state(self):
        return self.s.ask("p1; p:stat?")

    def getstatus(self, cn):
        """ Returns status of source nr."""
        adr, nr = self._get_adress(cn)
        retr = self.s.ask(adr + "state ?")
        states = {'0' : 'Off', '1' : 'On', '2' : 'Warning', '3' : 'Alarm'}
        return states[str(retr)]
