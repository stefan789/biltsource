import bilt

class BiltSource(object):
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

def main():
    _built_source_objs = {}
    def _wrapper_function(func, chan, *args):
         if chan not in _built_source_objs:
             _built_source_objs[chan] = BiltSource(chan)
         b = _built_source_objs[chan]
         return getattr(b, func)(*args)

    def _make_lambda(func):
        def f(*args):
            return _wrapper_function(func, *args)
        return f
    import inspect
    import pynedm
    import time
    all_methods = inspect.getmembers(BiltSource(0), inspect.ismethod)
    def _create_function(aname):
        def _f(*args):
            o = bilt.Bilt()
            return getattr(o, aname)(*args)
        return _f

    def run_ramp():
        def f():
            _stop_run = False
            o = bilt.Bilt()
            pynedm.write_document_to_db({ "type" : "data", "value" : { "ramp_running" : 1 } })
            o.run_ramp()
            while (int(o.read_macro_state()) == 2):
              time.sleep(1.)
            pynedm.write_document_to_db({ "type" : "data", "value" : { "ramp_running" : 0 } })
        pynedm.start_process(f)

    alist = ['setup_ramp', 'read_macro_data', 'readallerrors', 'stop_macro']
    adict = dict([(k, _create_function(k)) for k in alist])
    adict['run_ramp'] = run_ramp

    for name, _ in all_methods:
        if name[:2] == '__': continue
        adict[name] = _make_lambda(name)

    pynedm.listen(adict, "nedm%2Finternal_coils",
                  username="internal_coils_writer",
                  password="clu$terXz",
                  uri="http://raid.nedm1:5984")

    pynedm.wait()

if __name__ == '__main__':
     main()
