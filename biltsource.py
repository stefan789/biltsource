import bilt

class BiltSource(bilt.Bilt):
    def __init__(self, nr):
        self.b = bilt.Bilt()
        self.nr = nr

    def on(self):
        self.b.on(self.nr)

    def off(self):
        self.b.off(self.nr)

    def getstatus(self):
        return self.b.getstatus(self.nr)

    def setvoltage(self, volt=0.0):
        self.b.setvoltage(self.nr, volt)

    def setcurrent(self, curr=0.0):
        self.b.setcurrent(self.nr, curr)

    def setvoltrange(self, ran):
        self.b.setvoltrange(self.nr, ran)
    
    def setcurrentrange(self, ran):
        self.b.setcurrentrange(self.nr, ran)

    def getvoltage(self):
        return self.b.getvoltage(self.nr)

    def getcurrent(self):
        return self.b.getcurrent(self.nr)

    def getvoltrange(self):
        return self.b.getvoltrange(self.nr)

    def getcurrentrange(self):
        return self.b.getcurrentrange(self.nr)
