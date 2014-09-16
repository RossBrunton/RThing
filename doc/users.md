## User Management ##

### Remote Logins ###
The system supports authentication using `REMOTE_LOGIN` instead of using its own authentication. To enable this set
`USE_REMOTE_USER` in settings.py to True. This does the following:
- If the request has the `REMOTE_LOGIN` environment variable set, then the request will automatically log in as the user
with the username `CLEAN_REMOTE(REMOTE_LOGIN)` for the function CLEAN_REMOTE in settings.py.
- Users that don't exist are not created; the system refuses to log them in.
- If the user has no (or invalid) credentials, the system will display `settings.REMOTE_DENIED_MESSAGE` instead of a log
 in prompt.
- The links to log out and change password are hidden.
- Passwords are ignored and unused, but the system still requires them in case `USE_REMOTE_USER` should be turned off in
the future.

### Adding Superusers ###
Run `manage.py createsuperuser` from a shell and follow the directions.

### Adding Lecturers ###
To add new lecturers to the system, do the following as a superuser:

1. visit `/admin/` of the site.
2. Under `auth` select `Users`.
3. Select `Add user` in the upper right of the page.
4. Set a username and password and select `save`. If you are using remote logins, the password will be ignored.
5. On the next page, set the lecturer's email address, check `staff status` and add them to the "Course Editor" group.
6. Select `save` again.

### Adding Students ###
You do not need to add students; when they are added to the course logins are provided automatically for them. Their
password will be set to their username and their email set to `username@settings.EMAIL_DOMAIN`.
