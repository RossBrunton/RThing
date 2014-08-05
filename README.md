## RThing ##

### Requirements ###
This application runs on Python 3.3 or greater, so that is required, as is virtualenv to install dependancies.

A database is also required; by default mysql is used, but this can be changed in the settings file to anything Django
supports (PostgreSQL, Sqlite or Oracle), but you'll need to set it up yourself.

When using mysql, you need to install the development libraries for python3 and mysql (python3-dev and
libmysqlclient-dev possibly) for the python package "mysqlclient".

### Installation ###
Copy the files over to where they will live; you can use any location:
> mkdir /var/www/rthing
> cp -r . rthing/
> cd /var/www/rthing

Set up a virtualenv:
> virtualenv -p /usr/bin/python3 .
> source bin/activate

Install packages:
> pip install django django-ordered-models
> pip install mysqlclient #mysql only

Set up settings:
> cp ./rthing/settings.py.sample ./rthing/settings.py
> $EDITOR ./rthing/settings.py

And set up database connection:
> cp ./db.cnf.sample ./db.cnf
> $EDITOR ./db.cnf

Perform database sync:
> python manage.py syncdb

