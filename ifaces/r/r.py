# R interface

import subprocess
import os
import settings
import shlex
import shutil
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
    
    try:
        # Create and bind a tmp directory
        os.mkdir(os.path.join(settings.SANDBOX_DIR, "tmps", str(data.get("user", 0))), 0o770)
        _command[_tmpindex] = u"-b {}:/tmp".format(os.path.join(settings.SANDBOX_DIR, "tmps", str(data.get("user", 0))))
        
        # Seed the RNG if needed
        if data.get("uses_random", False):
            data["commands"] = "set.seed({});".format(data["seed"]) + data["commands"]
        
        # And also the image
        if data.get("uses_image", False):
            data["commands"] = ('postscript(file="/tmp/plot.ps", '
                'width={}, height={}'
                ', paper="special", horizontal=FALSE);'
            ).format(width, height) + data["commands"]
        
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
        
        # Timeout sets return to 124 on timeout
        if proc.returncode == 124:
            stderr = "Timeout expired; check to see if you have any infinite loops"
        
        output["out"] = stdout
        output["err"] = stderr.replace("Execution halted\n", "")
        
        output["is_error"] = output["err"] != ""
        
        if data.get("uses_image", False):
            # Read the image to media URL
            path = os.path.join(settings.BASE_DIR, "sandboxes", "tmps", str(data.get("user", 0)), "plot.ps")
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
    
    finally:
        # Remove tmp dir
        shutil.rmtree(os.path.join(settings.BASE_DIR, "sandboxes", "tmps", str(data.get("user", 0))))
    
    return output


def _is_a_number(str, p):
    """Takes a string and a pointer and returns whether the current pointer is just after the e+ part of 1e+10"""
    if str[p-1] in "-+" and str[p-2] in "eE":
        return True
    
    if str[p-1] in "eE":
        return True
    
    return False

# These characters must not have whitespace between them. Called "alphanumeric" because I forgot about .
_an = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789."
# Whitespace
_ws = " \t\n"
# Quotes
_quotes = "\"'`"
# And escape codes
_esc = "\\"
def is_equivalent(a, b):
    # String pointers
    ap = 0
    bp = 0
    ps = 0
    
    an_comp = False
    while ap < len(a) and bp < len(b):
        # If none of the current chars are alphanumeric or the last character match is not alphanumeric then skip
        # whitespace forward
        if (a[ap] not in _an and b[bp] not in _an) or not an_comp:
            while ap < len(a) and a[ap] in _ws and not _is_a_number(a, ap):
                ap += 1
            while bp < len(b) and b[bp] in _ws and not _is_a_number(b, bp):
                bp += 1
        
        if ap >= len(a) or bp >= len(b):
            # Reached end of string
            break
        
        an_comp = False
        
        if a[ap] != b[bp]:
            # They must be equal
            # print("Failed {}:{} / {}:{}".format(a, ap, b, bp))
            return False
        
        if a[ap] in _an:
            # This is comparing two alphanumeric values
            an_comp = True
        
        if a[ap] in _quotes:
            opener = a[ap]
            # String; must match exactly
            ap += 1
            bp += 1
            while ap < len(a) and bp < len(b) and a[ap] == b[bp]:
                if a[ap] == opener and a[ap-1] not in _esc:
                    break
                ap += 1
                bp += 1
            else:
                # print("Failed {}:{} / {}:{} in string".format(a, ap, b, bp))
                return False
        
        ap += 1
        bp += 1
    
    # Clean up ending whitespace
    while ap < len(a) and a[ap] in _ws:
        ap += 1
    while bp < len(b) and b[bp] in _ws:
        bp += 1
    
    if ap >= len(a) and bp >= len(b):
        return True
    else:
        return False

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
_tmpindex = len(_command)
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
