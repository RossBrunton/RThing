# R interface

import subprocess
import os
import settings
import shlex

PROMPT = ">"

_command = []
_nsindex = 0
_wdindex = 0
_argindex = 0

def exec(data):
    output = {}
    
    # Set the namespace and working directory
    _command[_nsindex] = "-b {}:/{}".format(
        os.path.join(settings.NAMESPACE_DIR, str(data["namespace"])),
        str(data["namespace"]),
    )
    _command[_wdindex] = "-w /{}".format(str(data["namespace"]))
    
    
    # Set the command argument
    _command[_argindex] = data["commands"].replace("\n", ";").replace("\r", "").replace(";;", ";")
    
    print(" ".join(_command))
    
    # Create the process
    stdout, stderr = "", ""
    try:
        stdout, stderr = subprocess.Popen(
            _command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        ).communicate(timeout=500/1000)
    except subprocess.TimeoutExpired:
        stderr = "Timeout expired; check to see if you have any infinite loops"
    
    output["out"] = stdout
    output["err"] = stderr.replace("Execution halted\n", "")
    
    output["is_error"] = output["err"] != ""
    
    return output

def is_equivalent(a, b):
    return a == b

def generic_print(expr):
    return "print(\"{}\");".format(expr)

# Generate command
_command.append("proot")

for f in settings.R_BOUND:
    _command.append("-b {}".format(f))

_nsindex = len(_command)
_command.append("")
_wdindex = len(_command)
_command.append("")

_command.append("-r {}".format(os.path.join(settings.SANDBOX_DIR, "r")))
_command.append("/rwrap")

_argindex = len(_command)
_command.append("")
