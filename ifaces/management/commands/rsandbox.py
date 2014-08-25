from django.core.management.base import BaseCommand, CommandError

from optparse import make_option
import os
import shutil
from os import path
import stat
import re
import subprocess
from distutils.spawn import find_executable
from six.moves import input

import settings

class Command(BaseCommand):
    help = 'Sets up the sandbox for R'
    option_list = BaseCommand.option_list + (
        make_option('--replace',
            action='store_true',
            dest='replace',
            default=False,
            help='Replace the sandbox if it exists',
        ),
        
        make_option('--no-replace',
            action='store_true',
            dest='no-replace',
            default=False,
            help='Do not replace the sandbox if it exists',
        ),
        
        make_option('--suid',
            action='store_true',
            dest='suid',
            default=False,
            help='Suid the prootwrap binary, which requires sudo',
        ),
        
        make_option('--no-suid',
            action='store_true',
            dest='no-suid',
            default=False,
            help='Do not suid the prootwrap binary. Using this flag is a security issue',
        ),
        
        make_option('--no-download',
            action='store_true',
            dest='no-download',
            default=False,
            help='Do not download proot',
        )
    )

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        if options["replace"] and options["no-replace"]:
            raise CommandError("--replace and --no-replace given")
        
        if options["suid"] and options["no-suid"]:
            raise CommandError("--replace and --no-replace given")
        
        self.stdout.write("Creating sandbox for R")
        
        basedir = path.join(settings.SANDBOX_DIR, "r");
        
        # Check if it already exists
        if path.isdir(basedir):
            i = ""
            if options["no-replace"]:
                return
            
            while not options["replace"] and i not in ["y", "n", "yes", "no"]:
                i = input("Sandbox exists, replace it? [Y/N] ")
                
                if i in ["n", "no"]:
                    return
            
            self.stdout.write("Erasing existing sandbox")
            shutil.rmtree(basedir)
        
        os.mkdir(basedir, 0o750)
        
        self.stdout.write("Making /tmp")
        os.mkdir(path.join(basedir, "tmp"), 0o770)
        
        # Library list
        llist = settings.R_FILES[:]
        
        # Get libraries for R
        def addLib(lib):
            ldd = subprocess.Popen(
                "ldd {}".format(lib),
                stdout=subprocess.PIPE,
                universal_newlines=True,
                shell=True
            ).communicate()[0]
            
            for l in ldd.split("\n"):
                search = re.search(r"(\/[^\s]+)\s\(", l)
                if search and search.group(1) not in llist:
                    llist.append(search.group(1))
                    addLib(search.group(1))
        
        for lib in settings.R_LDD + settings.R_FILES:
            self.stdout.write("Calculating libraries for {}".format(lib))
            addLib(lib)
        
        # Copy files
        llist.sort()
        for f in llist:
            self.stdout.write("Copying {}".format(f))
            
            if path.isdir(f):
                shutil.copytree(f, path.join(basedir, f[1:]))
            else:
                if not path.isdir(path.join(basedir, path.dirname(f[1:]))):
                    os.makedirs(path.join(basedir, path.dirname(f[1:])), 0o750)
                shutil.copy(f, path.join(basedir, f[1:]))
                os.chmod(path.join(basedir, f[1:]), 0o750)
        
        
        bindir = path.join(settings.BASE_DIR, "ifaces", "r")
        
        # Make binaries
        self.stdout.write("Compiling prootwrap")
        os.system("gcc -o {bin} {bin}.c".format(bin=path.join(bindir, "prootwrap")))
        os.chmod(path.join(bindir, "prootwrap"), 0o750)
        
        # Download proot
        if not options["no-download"]:
            self.stdout.write("Downloading proot from http://static.proot.me/")
            os.system("wget -q -O '{}' http://static.proot.me/proot-`uname -m`".format(path.join(bindir, "proot")))
            os.chmod(path.join(bindir, "proot"), 0o750)
        
        # Priviliged stuff
        root_commands = [
            "chgrp -R {webuser} '{base}'".format(base=settings.BASE_DIR, webuser="{webuser}"),
            "chmod -R g+rx '{}'".format(settings.BASE_DIR),
            "find {} -type d -print0 | xargs -0 chmod g+w".format(settings.BASE_DIR),
            "chown {nobody} '{prootwrap}'".format(prootwrap = path.join(bindir, "prootwrap"), nobody="{nobody}"),
            "chmod u+s '{}'".format(path.join(bindir, "prootwrap"))
        ]
        
        if not options["suid"] and not options["no-suid"]:
            self.stdout.write("I need to do the following, but I need permission to do so:")
            self.stdout.write("- Change the group of all the files in the sandbox to the web user")
            self.stdout.write("- Change the owner of prootwrap to a sandbox user")
            self.stdout.write("- Add the setuid bit to prootwrap")
            self.stdout.write("The source of prootwrap is in ifaces/r/prootwrap.c if you are worried")
        
        
        def write_help(webuser, nobody):
            for l in root_commands:
                self.stdout.write(l.format(webuser=webuser, nobody=nobody))
        
        # Sudo check
        sudo = True
        if not find_executable("sudo"):
            sudo = False
        
        i = None
        while not options["suid"] and not options["no-suid"] and i not in ["y", "n", "yes", "no"]:
            i = input("Do you agree to this? [Y/N/?] ")
            
            if i == "?":
                self.stdout.write("The following commands will be ran:")
                write_help("[webuser]", "[nobody]")
        
        if options["suid"] or i in ["y", "yes"]:
            webuser = input("What is the name/id of the webuser (possibly 'www-data')? ")
            nobody = input("What shall I use as the name/id as the sandbox user (maybe 'nobody')? ")
            
            if sudo:
                for l in root_commands:
                    self.stdout.write("sudo "+l.format(webuser=webuser, nobody=nobody))
                    os.system("sudo "+l.format(webuser=webuser, nobody=nobody))
            
                self.stdout.write("Files permissioned succesfully.")
                self.stdout.write("Note that any change in permission in the future will likely break the setuid.")
            else:
                self.stdout.write(
                    "Sudo was not found on your system; you need to run the following commands manually as root:"
                )
                write_help(webuser, nobody)
        else:
            self.stdout.write(
                "The system should still run but it will not be sandboxed; people WILL try to delete files"
            )
