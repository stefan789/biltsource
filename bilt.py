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
        self.initComm()

    def initComm(self, ip="192.168.1.251"):
        """ Initalizes communication with device via visa.
        
        Keyword argument:
        ip -- IP adress of the source, defaults to 192.168.1.251
        """
        self.s = SocketObj(str(ip), 5025)

    def on(self, nr):
        """ Switch on source nr."""
        adr = self.sources[str(nr)]["Name"]
        self.setvoltrange(nr, self.sources[str(nr)]["SetVoltRange"])
        self.setvoltage(nr, self.sources[str(nr)]["SetVolt"])
        self.s.write(adr + " outp on")

    def off(self, nr):
        """ Switch off source nr."""
        adr = self.sources[str(nr)]["Name"]
        self.s.write(adr + " outp off")

    def setvoltage(self, nr, volt=0.0):
        """ Set voltage for source nr to volt."""
        adr = self.sources[str(nr)]["Name"]
        if volt <= self.sources[str(nr)]["SetVoltRange"]:
            self.s.write(adr + " volt " + str(volt))
            self.sources[str(nr)]["SetVolt"] = volt
        else:
            print "Voltage out of range, setvoltrange first, set: %s, available ranges: %s" % (str(self.sources[str(nr)]["SetVoltRange"]), str(self.sources[str(nr)]["VoltRanges"]))

    def setcurrent(self, nr, curr=0.0):
        """ Set current for source nr to curr."""
        adr = self.sources[str(nr)]["Name"]
        if cur <= self.sources[str(nr)]["SetCurrRange"]:
            self.s.write(adr + " curr " + str(volt))
            self.sources[str(nr)]["SetCurr"] = curr
        else:
            print "Current out of range, setcurrrange first, set: %s, available ranges: %s" % (str(self.sources[str(nr)]["SetCurrRange"]), str(self.sources[str(nr)]["CurrRanges"]))
    
    def setvoltrange(self, nr, ran):
        """ Set voltage range for source nr to ran."""
        if ran in self.sources[str(nr)]["VoltRanges"]:
            adr = self.sources[str(nr)]["Name"]
            self.s.write(adr + " volt:rang:auto off")
            self.s.write(adr + " volt:rang" + str(ran))
            self.sources[str(nr)]["SetVoltRange"] = ran
        else:
            print "range not available, possible are %s" % str(self.sources[str(nr)]["VoltRanges"])

    def setcurrentrange(self, nr, ran):
        """ Set current range for source nr to ran."""
        if ran in self.sources[str(nr)]["CurrRanges"]:
            adr = self.sources[str(nr)]["Name"]
            self.s.write(adr + " curr:rang:auto off")
            self.s.write(adr + " curr:rang" + str(ran))
            self.sources[str(nr)]["SetCurrRange"] = ran
        else:
            print "range not available, possible are %s" % str(self.sources[str(nr)]["CurrRanges"])

    def getvoltage(self, nr):
        """ Returns currently set voltage for source nr."""
        cmd = self.sources[str(nr)]["Name"] + " meas:volt ?"
        return self.s.ask(cmd)

    def getcurrent(self, nr):
        """ Returns currently set current for source nr."""
        return self.s.ask(self.sources[str(nr)]["Name"] + " meas:curr ?")

    def getvoltrange(self, nr):
        """ Returns currently set voltage range for source nr."""
        adr = self.sources[str(nr)]["Name"]
        return self.s.ask(adr + "volt:range ?")        

    def getcurrentrange(self, nr):
        """ Returns currently set current range for source nr."""
        adr = self.sources[str(nr)]["Name"]
        return self.s.ask(adr + "curr:range ?")        

    def readconfig(self, conf):
        """ Reads configurations from file conf and return dictionary."""
        with open(str(conf), "r") as f:
            sources = json.loads(f.read(), object_pairs_hook=collections.OrderedDict)
        return sources

    def saveconfig(self, fil):
        """ Saves configuration to file fil."""
        with open(str(fil), "w") as f:
            f.write(json.dumps(self.sources, indent=4, separators = (',', ' : ')))

    def getstatus(self, nr):
        """ Returns status of source nr."""
        adr = self.sources[str(nr)]["Name"]
        retr = self.s.ask(adr + "state ?")
        states = {'0' : 'Off', '1' : 'On', '2' : 'Warning', '3' : 'Alarm'}
        return states[str(retr)]
