## RThing ##

### Requirements ###
This application runs on Python 3.3 or greater or Python 2.7 or greater, so one of those is required, as is virtualenv
to install dependancies.

A database is also required; by default mysql is used, but this can be changed in the settings file to anything Django
supports (PostgreSQL, Sqlite or Oracle), but you'll need to set it up yourself.

When using mysql, you need to install the development libraries for python3 and mysql (python3-dev and
libmysqlclient-dev possibly) for the python package "mysqlclient".

Memcached and gcc is also required.

For Debian; the packages (`python2.7` or `python3`), `python-virtualenv`, (`python2.7-dev` or `python3-dev`),
`libmysqlclient-dev`, `memcached`, `gcc`

### Installation ###
Copy the files over to where they will live; you can use any location:
> mkdir /var/www/rthing
> cp -r . rthing/
> cd /var/www/rthing

Set up a virtualenv:
> virtualenv -p /usr/bin/python3 .
> source bin/activate

Install packages:
> pip install django django-ordered-model six
> pip install mysqlclient # mysql only
> pip install python-memcached # Python 2.*
> pip install python3-memcached # Python 3.*

Set up settings:
> cp ./settings.py.sample ./settings.py
> $EDITOR ./settings.py

And set up database connection:
> cp ./db.cnf.sample ./db.cnf
> $EDITOR ./db.cnf

Perform database sync:
> python manage.py syncdb

Collect static files:
> python manage.py collectstatic
