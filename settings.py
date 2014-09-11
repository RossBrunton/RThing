"""
Django settings.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/

Rthing adds a few other settings as follows:
ANSWER_LOCK - Whether the user be forbidden from using the prompt after they answer or skip the question
FOOTER - Displayed in the black box in the bottom of the screen
TEST_SQLITE - If true, then tests will be ran on a sqlite database rather than trying to create a new mysql table
EMAIL_DOMAIN - When a new user is created using the "add students to task", their email will be set to user@EMAIL_DOMAIN
IFACES - Dict containing languages and their package names, key is an internal name, value is a (Friendly name,
package name) pair
IFACE_DEF - The name of the default interface
USE_REMOTE_USER - If true, then authentication is left to the server using the REMOTE_USER var. See doc/users.md for
details
REMOTE_DENIED_MESSAGE - The message to be displayed when auth from USE_REMOTE_USER fails
CLEAN_REMOTE - A function that should take in a username from REMOTE_USER, and return a username for the system
R_FILES - Files to be copied into the system when rsandbox is ran
R_BIND - Files to be visible to the R prompt when it is running
NAMESPACE_DIR - Directory where namespaces are to live, these are the folders that store the files uploaded to lessons
for the prompt to see them
SANDBOX_DIR - Directory where sandboxes are to live, R creates two folders, r and tmps, for it"s root directory and
tmp directories.

This file will attempt to import all of settings_local.py to get their config vars. You should put any custom config
settings in that file
"""

import os
import sys
try:
    import settings_local
except ImportError:
    print("You need to copy over settings_local.py and db.cnf; see README for details.")


BASE_DIR = os.path.dirname(__file__)

DEBUG = False
TEMPLATE_DEBUG = DEBUG

INSTALLED_APPS = (
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "ordered_model",
    "rthing",
    "courses",
    "tasks",
    "stats",
    "staff",
    "users",
    "ifaces",
    "export"
)

MIDDLEWARE_CLASSES = (
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
)

if settings_local.USE_REMOTE_USER:
    MIDDLEWARE_CLASSES = MIDDLEWARE_CLASSES + ("django.contrib.auth.middleware.RemoteUserMiddleware",)

ROOT_URLCONF = "rthing.urls"
WSGI_APPLICATION = "wsgi.application"

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases
if "test" in sys.argv and settings_local.TEST_SQLITE:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": "testingdb.sqlite",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.mysql",
            "OPTIONS": {"read_default_file":os.path.join(BASE_DIR, "db.cnf")},
        }
    }


# Caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
        "LOCATION": "127.0.0.1:11211",
        "TIMEOUT":60*60, # An hour
    }
}

# Auth backets
if settings_local.USE_REMOTE_USER:
    AUTHENTICATION_BACKENDS = (
        "users.backends.CustomRemoteUserBackend",
    )
else:
    # Use default
    pass


# Template processors
TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "users.context_processors.use_remote_checker",
    "rthing.context_processors.footer_putter",
)

# Internationalization (not in use)
# https://docs.djangoproject.com/en/1.6/topics/i18n/
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "UTC"
USE_I18N = False
USE_L10N = False
USE_TZ = False

# Directiories
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static")
]
TEMPLATE_DIRS = [
    os.path.join(BASE_DIR, "templates")
]

# URLs
LOGIN_URL = "users:login"
LOGOUT_URL = "users:logout"

# More directories
NAMESPACE_DIR = os.path.join(BASE_DIR, "namespaces")
SANDBOX_DIR = os.path.join(BASE_DIR, "sandboxes")

from settings_local import *
