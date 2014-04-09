"""
With this class the BILT power supplies can be controlled from python.
"""

import visa
import time
import json
import collections

def blubb(st):
    print st

def blubber(st):
    print st

class BiltSource():
    def __init__(self, conf = "sources.dict"):
        """ Constructor.

        Keyword argument:
        conf -- file containing a json dictionary to read configuration from (default: sources.dict)
        """
        self.sources = self.readconfig(conf)
        self.initComm()

    def initComm(self, ip="192.168.1.111"):
        """ Initalizes communication with device via visa.
        
        Keyword argument:
        ip -- IP adress of the source, defaults to 192.168.1.111
        """
        self.s = visa.instrument("TCPIP::192.168.1.251::5025::SOCKET", term_chars = "\n")

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
        if ran in self.sources[str(nr)]["VoltRanges"]:
            adr = self.sources[str(nr)]["Name"]
            self.s.write(adr + " curr:rang:auto off")
            self.s.write(adr + " curr:rang" + self.sources[str(nr)]["Range"])
            self.sources[str(nr)]["SetCurrRange"] = ran
        else:
            print "range not available, possible are %s" % str(self.sources[str(nr)]["CurrRanges"])

    def getvoltage(self, nr):
        """ Returns currently set voltage for source nr."""
        return self.s.ask(self.sources[str(nr)]["Name"] + " meas:volt ?")

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
        return self.s.ask(adr + "volt:curr ?")        

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
        self.s.ask(adr + "state ?")
        states = {'0' : 'Off', '1' : 'On', '2' : 'Warning', '3' : 'Alarm'}
        return states[str(0)]
