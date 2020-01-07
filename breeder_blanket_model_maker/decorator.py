import time

def time_function(time_log):
    def timeit(method):
        def timed(*args, **kw):
            ts = time.time()
            result = method(*args, **kw)
            te = time.time()

            time_log.append((method.__name__,int((te - ts)*1000 )))
            print('%r  %2.2f ms' % (method.__name__, (te - ts) *1000))
            return result

        return timed
    return timeit