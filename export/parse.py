import six

def from_dict(obj):
    outs = ""
    
    for key, value in six.iteritems(obj):
        if isinstance(value, six.string_types) and "\n" in value:
            print(key)
    
    return outs
