# R interface

import subprocess
import os
import settings
import shlex
import six
from base64 import b64encode

PROMPT = u">"
LINE_END = u";"

_command = []
_nsindex = 0
_wdindex = 0
_argindex = 0

width = 13
height = 5

def run(data):
    output = {}
    
    # Set the namespace and working directory
    _command[_nsindex] = u"-b {}:/{}".format(
        os.path.join(settings.NAMESPACE_DIR, str(data["namespace"])),
        str(data["namespace"]),
    )
    _command[_wdindex] = u"-w /{}".format(str(data["namespace"]))
    
    # Seed the RNG if needed
    if data.get("uses_random", False):
        data["commands"] = "set.seed({});".format(data["seed"]) + data["commands"]
    
    # And also the image
    if data.get("uses_image", False):
        data["commands"] = ('postscript(file="/tmp/plot_{}.ps", '
            'width={}, height={}'
            ', paper="special", horizontal=FALSE);'
        ).format(data.get("user", 0), width, height) + data["commands"]
    
    # Set the command argument
    cmd_arg = data["commands"].replace("\n", u"").replace("\r", u"")
    
    _command[_argindex] = cmd_arg
    
    # Create the process
    stdout, stderr = "", ""
    
    proc = subprocess.Popen(
        _command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )
    
    # print(" ".join(_command))
    
    stdout, stderr = proc.communicate()
    
    if proc.returncode == 124:
        stderr = "Timeout expired; check to see if you have any infinite loops"
    
    output["out"] = stdout
    output["err"] = stderr.replace("Execution halted\n", "")
    
    output["is_error"] = output["err"] != ""
    
    if data.get("uses_image", False):
        # Read the image to media
        path = os.path.join(settings.BASE_DIR, "sandboxes", "r", "tmp", "plot_{}.ps".format(data.get("user", 0)))
        if os.path.isfile(path):
            image = subprocess.Popen(
                [
                    "gs", "-q", "-sDEVICE=png16", "-sOutputFile=-", "-DPARANOIDSAFER", "-dBATCH", "-dQUIET",
                    "-dNOPROMPT", "-dNOPAUSE", "-dDEVICEWIDTHPOINTS={}".format(width*72),
                    "-dDEVICEHEIGHTPOINTS={}".format(height*72), path
                ],
                stdout=subprocess.PIPE,
            ).communicate()[0]
            
            output["media"] = "data:image/png;base64,{}".format(b64encode(image))
            if output["media"] == _empty_plot:
                output["media"] = None
            
            os.remove(path)
    
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
_command.append("/usr/bin/R")
_command.append("--slave")
_command.append("--vanilla")
_command.append("--no-readline")
_command.append("-e")

_argindex = len(_command)
_command.append("")


# Now generate the empty image so we can check if the plot is empty
_empty_plot = None
_empty_plot = run({
    "commands":"", "namespace":None, "uses_random":False, "uses_image":True, "automark":False, "seed":0, "user":0
}).get("media", "")
