## File Listing ##

This document serves to list all the files in the system, and does not assume any knowledge of Python or Django.

### bin, include, lib, local ###
Used by virtualenv to store local packages, binaries, libraries and what have you.

### courses, rthing, staff, stats, tasks, users ###
Django "apps"; each app may contain any of the following files:

- admin.py
Admin Models for the admin page, and other admin stuffs
- forms.py
Forms for displaying on pages
- models.py
Database models for the app
- templatetags
Tags for the templating system
- tests.py
Unit tests
- urls.py
URLs that the app uses
- utils.py
General utility methods
- views.py
Handle requests
- migrations
Migrations to track changes in database schema

The apps are as follows, and serve as a way to divide up the project

- courses
General course information and views. This handles the course list, course pages and lesson pages, as well as the
database models for each.
- export
Exporting and importing courses to text.
- rthing
Contains the root url config which refers to the urls of all other apps and also contains anything that is to general
for any other app.
- staff
Staff features; adding removing people from courses, uploading files. Generally anything that requires you to be a staff
member to do.
- stats
Models and views that relate to viewing or saving statistics.
- tasks
Views for handling tasks, this does not store the task model, and is intended to handle "behind the scenes" views such
as handling code from the client.
- users
User functions, such as password resets and a model that adds extra data to Django's auth system.

### doc ###
Documentation

### ifaces ###
Interfaces; each package except `management` should be a language for this system to integrate with. The `management`
folder contains commands that the `manage.py` script uses.

### media ##
Uploads from lecturers that are visible from the web server. This folder should be served under `/media/` and must be
writeable for the web user.

### namespaces ###
Directories for files uploaded into lessons for the code prompt. Each folder is a single namespace that will be the
working directory for an R prompt that runs a task.

### sandboxes ###
Sandboxes for each language.

### static ###
Static files; these will be collected by `collectstatic`, along with static files for Django's admin system, and stored
in `collectedstatic` for serving my the webserver.

### templates ###
Templates for views to serve.
