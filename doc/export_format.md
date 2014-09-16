## Export Format ##

From a line that looks like `type name {randomstring{` to a line that looks like `}randomstring}` the text inside is
considered to describe the object called `name`, which can of type `str` (text data), `dict` (name-value pairs), `list`
(list of values) or `comment` (everything inside is ignored).

For `str`, the lines inside are considered literal text, including all whitespace. For `dict`s and `list`s, each entry
is either in the format `type name:value` or as `type name {anotherrandomstring{` to `}anotherrandomstring}` blocks. For
lists, the name is ignored but dicts use them as the keys.

When using `type name:value`, the types are `str`, `bool`, `int`, `float`, `none` or `comment` as follows:
- `str`: Single line string, must not be encased in quotes and must contain no newlines.
- `bool`: Case insensitive true, yes 1 for true, or anything else for false.
- `int`: Integer.
- `float`: Floating point number.
- `none`: No data exists for this, this maps to the Python type None and it's value is ignored.
- `comment`: The value is ignored entirely 
