"""R interface

For this to work, `manage.py rsandbox` must have been ran.

On first import it builds a command like the following:
/path/to/timeoutwrap 1s proot -b bound_file... -r /path/to/sandbox -w /path/to/namespace /usr/bin/R --slave --vanilla
--no-readline -e code

In order:
- Invoke timeoutwrap: a wrapper around /usr/bin/timeout, drop privileges and restrict memory usage
- Set the timeout to 1 second
- Invoke proot to chroot to the sandbox
- Bind all the files (given by settings.R_BOUND) into the chroot
- Set the root directory to the sandbox
- Set the working directory to the right namespace in settings.NAMESPACE_DIR so it can see files folders in
NAMESPACE_DIR are named with the primary key of the lesson they are associated with.
- Invoke R with the appropriate arguments (--slave --vanilla --no-readline)
- Execute a single command and exit
- This is the code which will be ran

It creates four variables, _toindex, _nsindex, _wdindex, _tmpindex and _argindex. These are locations in the command
list that the timeout, namespace binding, working dictionary, tmp dir binding and code to run are. This is so that the
run function can directly change them without having to rebuild it.

It also uses the run function to generat a blank plot which it stores in _empty_plot.

When it executes code, it does the following:
- Sets the command so the namespace is bound and set to the working directory.
- Create a /tmp directory in the sandbox for the user executing the command.
- If needed, add code to seed the RNG before the code.
- If needed, set up R so that it outputs the image to /tmp/plot.ps.
- Set the code argument.
- Create the process with the command, run it and get stderr and stdout.
- If the process had the return code 124, it timed out, so set stderr to a suitable message.
- Remove "Execution halted" from stderr, which isn't really usefull.
- Add stderr and stdout to the object to return as "err" and "out".
- If stderr is not an empty string, set "is_error" to true on the object to be returned.
- If media is expected, invoke ghostscript to convert R's outputed file to a png file and collect it in a Python 
variable via stdout.
- base64 encode the plot so it's suitable for displaying in a browser.
- If the plot is equal to _empty_plot, remove it since there was no plot drawn this time (R outputs an empty image).
- Remove the /tmp directory using rmwrap (files are created by nobody, which the webuser can't remove).
"""
import subprocess
import os
from django.conf import settings
import shlex
import shutil
import six
import stat
from base64 import b64encode

PROMPT = u">"
LINE_END = u";"

# The command to run
_command = []
# The index in the command where the namespace is bound
_nsindex = 0
# The index in the command where the namespace is set to the current directory
_wdindex = 0
# The index in the command where /tmp is bound
_tmpindex = 0
# The index in the command where the argument (code to run) is stored
_argindex = 0

"""The width in inches of plots"""
width = 13
"""The height in inches of plots"""
height = 5

def run(data):
    """Runs the code
    
    See doc/adding_languages.md for the interface
    """
    output = {}
    
    # Check if namespace exists (it should)
    if "namespace" not in data:
        raise RuntimeError("'namespace' not in provided data: {}".format(str(data)))
    
    # Now check to see if the namespace folder exists, and if it doesn't, create it
    if not os.path.isdir(os.path.join(settings.NAMESPACE_DIR, str(data["namespace"]))):
        os.mkdir(os.path.join(settings.NAMESPACE_DIR, str(data["namespace"])), 0o750)
    
    # Set the namespace and working directory
    _command[_nsindex] = u"-b {}:/{}".format(
        os.path.join(settings.NAMESPACE_DIR, str(data["namespace"])),
        str(data["namespace"]),
    )
    _command[_wdindex] = u"-w /{}".format(str(data["namespace"]))
    
    try:
        # Create and bind a tmp directory if it doesn't exist
        tmp_path = os.path.join(settings.SANDBOX_DIR, "tmps", str(data.get("user", 0)))
        if not os.path.isdir(tmp_path):
            os.mkdir(tmp_path, 0o770)
        # My server seems to ignore the mode set by os.mkdir
        os.chmod(tmp_path, 0o770)
        
        # Set timeout
        _command[_toindex] = "{}s".format(data.get("timeout", 3))
        
        # Set tmp location
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
        
        # Check if the error is likley due to plotting when use_image is false
        if "cannot open file 'Rplots.pdf'" in output["err"]:
            output["err"] = "[Maybe this task has uses image turned off?]\n" + output["err"]
        
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
                
                output["media"] = "data:image/png;base64,{}".format(b64encode(image).decode("ascii"))
                if output["media"] == _empty_plot:
                    output["media"] = None
    
    finally:
        # Remove tmp dir
        tmp_dir = os.path.join(settings.BASE_DIR, "sandboxes", "tmps", str(data.get("user", 0)))
        
        # First use rmwrap to empty it
        # Piping to null device because otherwise it'll complain that it can't delete the actual folder
        subprocess.call(
            [
                os.path.join(os.path.dirname(__file__), "rmwrap"), "-rf", "--preserve-root", tmp_dir
            ],
            stderr=open(os.devnull)
        )
        
        # And then delete the actual tmp dir
        if os.path.isdir(tmp_dir):
            shutil.rmtree(tmp_dir)
    
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
    """Compares two strings and returns whether they are the same R code
    
    This is unable to determine if a and b are different code, however. If this returns True you may assume that they
    are the same, but if this returns False you must not assume that they are different.
    
    is_equivalent("0 + 1", "1") is False, for example, even though those two commands do the same thing.
    """
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
    """Returns an R print statement for expr
    
    print("expr");
    """
    return "print(\"{}\");".format(expr)


# Generate command

# Timeoutwrap
_command.append(os.path.join(os.path.dirname(__file__), "timeoutwrap"))

# Timeout
_toindex = len(_command)
_command.append("")

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

# R
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
    "commands":"", "namespace":"Plot", "uses_random":False, "uses_image":True, "automark":False, "seed":0, "user":0
}).get("media", "")
