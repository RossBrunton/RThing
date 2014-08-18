from django.core.management.base import BaseCommand, CommandError

from optparse import make_option
import os
import shutil
from os import path
import stat
import re
import subprocess
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
        )
    )

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        if options["replace"] and options["no-replace"]:
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
        os.mkdir(path.join(basedir, "tmp"), 0o750)
        
        # Library list
        llist = settings.R_FILES[:]
        
        # Get libraries for R
        def addLib(lib):
            ldd = subprocess.Popen(
                ["ldd", lib],
                stdout=subprocess.PIPE,
                universal_newlines=True
            ).communicate()[0]
            for l in ldd.split("\n"):
                search = re.search(r"(\/[^\s]+)", l)
                if search and search.group(1) not in llist:
                    llist.append(search.group(1))
                    addLib(search.group(1))
        
        for lib in settings.R_LDD:
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
        for b in ["rwrap"]:
            self.stdout.write("Compiling {}".format(b))
            os.system("gcc -o {bin} {bin}.c".format(bin=path.join(bindir, b)))
            
            self.stdout.write("Copying {} to /{}".format(path.join(bindir, b), b))
            shutil.copy(path.join(bindir, b), path.join(basedir, b))
            os.chmod(path.join(basedir, b), 0o750)
            os.chmod(path.join(basedir, b), 0o750 | stat.S_ISGID)
