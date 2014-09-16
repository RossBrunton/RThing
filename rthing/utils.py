"""General utility functions"""
import six
from random import choice

def py2_str(c):
    """Wraps around a class, adding python2 support to __str__
    
    If running under Python 2 then __str__ will discard non-ascii characters and __unicode__ will be added.
    """
    if six.PY2:
        old_str = c.__str__
        def py2_str_wrap(self):
            return old_str(self).encode("ascii", "ignore")
        
        c.__unicode__ = old_str
        c.__str__ = py2_str_wrap
    
    return c


def rand_str(length):
    """Generates a random string of the given length containing only lowercase letters"""
    return "".join([choice("abcdefghijklmnopqrstuvwxyz") for x in range(length)])
