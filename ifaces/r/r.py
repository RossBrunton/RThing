# R interface

import subprocess
import os
import settings
import shlex
import six

PROMPT = ">"

_command = []
_nsindex = 0
_wdindex = 0
_argindex = 0

def run(data):
    output = {}
    
    # Set the namespace and working directory
    _command[_nsindex] = "-b {}:/{}".format(
        os.path.join(settings.NAMESPACE_DIR, str(data["namespace"])),
        str(data["namespace"]),
    )
    _command[_wdindex] = "-w /{}".format(str(data["namespace"]))
    
    # Seed the RNG if needed
    if data.get("uses_random", False):
        data["commands"] = "set.seed({});".format(data["seed"]) + data["commands"]
    
    # Set the command argument
    _command[_argindex] = data["commands"].replace("\n", ";").replace("\r", "").replace(";;", ";")
    
    print(" ".join(_command))
    
    # Create the process
    stdout, stderr = "", ""
    
    proc = subprocess.Popen(
        _command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    try:
        stdout, stderr = proc.communicate()
    except None:
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

# Prootwrap
_command.append(os.path.join(os.path.dirname(__file__), "prootwrap"))

# Timeout
_command.append("1s")

# Proot
_command.append(os.path.join(os.path.dirname(__file__), "proot"))

for f in settings.R_BOUND:
    _command.append("-b {}".format(f))

_nsindex = len(_command)
_command.append("")
_wdindex = len(_command)
_command.append("")

_command.append("-r {}".format(os.path.join(settings.SANDBOX_DIR, "r")))

# Rscript
_command.append("/usr/bin/Rscript")
_command.append("-e")

_argindex = len(_command)
_command.append("")
