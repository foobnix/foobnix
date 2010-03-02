import sys

""" Defined debug levels"""
NONE, MEDIUM, STRONG = 0, 1, 2

DEBUG_LEVEL = STRONG


def accepts(*types, **kw):
    """ Function decorator. Checks that inputs given to decorated function
    are of the expected type.    
    """
    if not kw:
        # default level: MEDIUM
        debug = DEBUG_LEVEL
    else:
        debug = kw['debug']
    try:
        def decorator(f):
            def newf(*args):
                if debug == 0:
                    return f(*args)
                assert len(args) == len(types)
                argtypes = tuple(map(type, args))
                if argtypes != types:
                    msg = info(f.__name__, types, argtypes, 0)
                    if debug == 1:
                        print >> sys.stderr, 'TypeWarning: ', msg
                    elif debug == 2:
                        raise TypeError, msg
                return f(*args)
            newf.__name__ = f.__name__
            return newf
        return decorator
    except KeyError, key:
        raise KeyError, key + "is not a valid keyword argument"
    except TypeError, msg:
        raise TypeError, msg

def returns(ret_type, **kw):
    """ Function decorator. Checks that return value of decorated function
    is of the expected type.   
    """
    try:
        if not kw:
            # default level: MEDIUM
            debug = DEBUG_LEVEL
        else:
            debug = kw['debug']
        def decorator(f):
            def newf(*args):
                result = f(*args)
                if debug == 0:
                    return result
                res_type = type(result)
                if res_type != ret_type:
                    msg = info(f.__name__, (ret_type,), (res_type,), 1)
                    if debug == 1:
                        print >> sys.stderr, 'TypeWarning: ', msg
                    elif debug == 2:
                        raise TypeError, msg
                return result
            newf.__name__ = f.__name__
            return newf
        return decorator
    except KeyError, key:
        raise KeyError, key + "is not a valid keyword argument"
    except TypeError, msg:
        raise TypeError, msg
    
    

def info(fname, expected, actual, flag):
    """ Convenience function returns nicely formatted error/warning msg. """
    format = lambda types: ', '.join([str(t).split("'")[1] for t in types])
    expected, actual = format(expected), format(actual)
    msg = "'%s' method " % fname \
    + ("accepts", "returns")[flag] + " (%s), but " % expected\
    + ("was given", "result is")[flag] + " (%s)" % actual
    return msg
