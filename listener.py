import bilt

def main():
    _built_source_objs = {}
    o = bilt.Bilt()
    def _wrapper_function(func, *args):
        return getattr(o, func)(*args)

    def _make_lambda(func):
        def f(*args):
            return _wrapper_function(func, *args)
        return f
    import inspect
    import pynedm
    import time
    all_methods = inspect.getmembers(bilt.Bilt(), inspect.ismethod)
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

    print(adict)

    pyl = pynedm.listen(adict, "nedm%2Finternal_coils",
                  username="usrname",
                  password="password",
                  uri="http://db.nedm1:5984")

    pyl.wait()

if __name__ == '__main__':
     main()
