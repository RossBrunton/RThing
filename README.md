## RThing ##
This is a web based teaching tool, initially designed for R (hence the unimaginitive name) in a similar style to things like codeacadamy. It uses Django (python) as a web framework, and interfaces with an existing instalation of R. It uses Django's admin interface to allow staff to create courses in a user friendly way.

It was implemented as part of a summer internship by Ross Brunton, and was funded by Heriot-Watt university and The Quality Assurance Agency for Higher Education.

### Requirements ###
This application only runs on a Linux server.

This application runs on Python 3.3 or greater or Python 2.7 or greater, so one of those is required. Python 2.7 is
recommended to avoid any headaches when setting up.

Virtualenv is also required to install Python packages.

A database is also required; by default mysql is used and configured in db.cnf.

This can be changed in the settings file to anything Django supports (PostgreSQL, Sqlite or Oracle), but in that case
you'll need to figure out dependencies as well.

When using mysql, you need to install the development libraries for python3 and mysql (python3-dev and
libmysqlclient-dev possibly) for the python package "mysqlclient".

Memcached is used as a cache, and should be running.

ghostscript, R and gcc are also required for the R interface.

A web server is required also, Apache with mod_wsgi is recommended. But, again, if you know what you are doing it should
run on Nginx with Gunicorn. Due to the way mod_wsgi works, it will only run with the version of Python that is compiled
into it. Usually this will be 2.7.

An email server is required (for sending password resets), although you can use another server to send it. See
settings_local.py.sample for config.

For Debian; the packages (`python2.7` or `python3`), `python-virtualenv`, (`python2.7-dev` or `python3-dev`),
`libmysqlclient-dev`, `memcached`, `gcc`, `apache2`, `libapache2-mod-wsgi`, `ghostscript`, `mysql-server` and `r-base`.

Optionally, you can have authentication work using the environment variable REMOTE_USER (which should contain a
username). See doc/users for details.

### Installation ###
Copy the files over to where they will live; you can use any location:
> mkdir /var/www/rthing
> cp -r . /var/www/rthing/
> cd /var/www/rthing

Set up a virtualenv (for python 2.7 in this case):
> virtualenv -p /usr/bin/python2.7 .

Activate the virtualenv:
> source bin/activate

Install packages:
> pip install django==1.7 django-ordered-model six
> pip install mysqlclient # mysql only
> pip install python-memcached # Python 2.*
> pip install python3-memcached # Python 3.*

Set up settings:
> cp ./settings_local.py.sample ./settings_local.py
> $EDITOR ./settings_local.py

And set up database connection:
> cp ./db.cnf.sample ./db.cnf
> $EDITOR ./db.cnf

Perform database sync:
> python manage.py migrate

Collect static files:
> python manage.py collectstatic

Create an initial user:
> python manage.py createsuperuser

Set up the sandbox:
> python manage.py rsandbox
