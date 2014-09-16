## Adding a new language ##

### Config ###
Language interfaces (such as R) are defined in settings.py in the IFACES key. Which is an object. Keys are a name for
the interface (used when storing it in the database) and the value is a (`pretty name`, `package`) pair. The pretty name
will be displayed on the admin form, and the package must be a Python package meeting the language interface.

### Language Interface ###
Languages are Python modules which must define the following properties:

#### PROMPT ####
The string to display at the beginning of prompts on the web page. Such as ">" or "$" or ">>>".

#### LINE_END ####
The line ending character for the language, usually ";". If the user submits code that doesn't end with this, it will
appended as a convienience.

#### is_equivalent(str, str) ####
Takes in two strings, and should return True if they would result in the same output, or False if it is unknown or they
are different. This should not invoke any other programs, and doesn't need to return True in all cases where they are
equivalent. It's used to quickly check so that we don't have to call `run` any more times than is needed.

#### generic_print(str) ####
Takes in a string and returns a "print" statement in the language. This statement should cause the output to create a
line break, followed by a line containing the argument to `generic_print` followed by another line break. In most
languages "print('arg');" is sufficient.

#### run(dict) ####
Takes in a dict, invokes the language's interpreter or whatever, and returns another dict containing the results.

The input dict contains the following:

- `namespace` (str): The namespace to run in, this will be the name of a directory in `settings.NAMESPACE_DIR` that should
be made visible to the program as it contains the task files.
- `commands` (str): The command to actually execute as a single string. May contain newlines but will not contain any non-
ascii characters.
- `user` (optional int): The user id of the user executing this command.
- `uses_random` (optional bool): Whether `uses_random` on the task is true. If this key is absent then assume false.
- `seed` (optional int): The seed to use for the RNG. If `uses_random` is true, then you may assume this key exists.
- `uses_image` (optional bool): Whether `uses_image` on the task is true.
- `timeout` (optional int): The timeout in seconds, the code should not run longer than this.

The output dict, which this function returns, contains the following keys:

- `out` (str): The output of the program, usually from stdout.
- `err` (str): Error output of the program, usually from stderr.
- `is_error` (bool): Whether an error occurred in the commands that were ran.
- `media` (optional str): Media, such as images, that were also output. This should be a data URI and may be absent if
the program didn't output any media.

### Security Implications ###
You are running untrusted code on your system, so the following must be prevented:

- Reading arbitrary files
- Writing arbitrary files
- Executing arbitrary binary files
- Creating huge amounts of memory.
- Consuming huge amounts of disk space.
- Programs that don't terminate or invoke a shell or something.
- Sending signals to other processes.
