# Dummy interface

import time

PROMPT = "[d] >"

def exec(data):
    output = {}
    output["out"] = data["commands"]
    output["err"] = ""
    output["is_error"] = False
    
    time.sleep(10/1000)
    
    return output

def is_equivalent(a, b):
    return a == b

def generic_print(expr):
    return expr
