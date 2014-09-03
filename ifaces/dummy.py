"""Dummy interface, for testing

When it runs code it sleeps for  returns an exact copy with the following replacements:
%replace => The string "replaced"
%seed => The seed
"""
PROMPT = "[d] >"
LINE_END = ""

def run(data):
    """"Executes" the given code"""
    output = {}
    output["out"] = data["commands"].replace("\r", "")\
        .replace("%replace", u"replaced")\
        .replace("%seed", str(data["seed"])) # This is done for testing
    output["err"] = ""
    output["is_error"] = False
    
    return output

def is_equivalent(a, b):
    """Checks if two strings are equivalent
    
    This only does a == b, and will not replace anything. For testing.
    """
    return a == b

def generic_print(expr):
    """Returns expr surrounded by newlines"""
    return "\n"+expr+"\n"
