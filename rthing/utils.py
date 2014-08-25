import six

def py2_str(c):
    """Wraps around a class, if running under Python 2 then convert the __str__ method and add __unicode__"""
    if six.PY2:
        old_str = c.__str__
        def py2_str_wrap(self):
            return old_str(self).encode("ascii", "ignore")
        
        c.__unicode__ = old_str
        c.__str__ = py2_str_wrap
    
    return c
