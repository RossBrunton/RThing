# Dummy interface

import time

PROMPT = "[d] >"

def run(data):
    output = {}
    output["out"] = data["commands"].replace("\r", "")\
        .replace("replace_me", "replaced") # This is done for testing
    output["err"] = ""
    output["is_error"] = False
    
    time.sleep(10/1000)
    
    return output

def is_equivalent(a, b):
    return a == b

def generic_print(expr):
    return expr
