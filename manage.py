#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rthing.settings")

    from django.core.management import execute_from_command_line
    
    try:
        execute_from_command_line(sys.argv)
    except ImportError:
        print("You need to copy over settings.py and db.cnf; see README for details.")
