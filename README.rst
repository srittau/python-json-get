Python JSON Get
===============

Get values from JSON objects usings a path expression. Optional type
checking is possible.

>>> from jsonget import json_get
>>> j = {
...     "foo": {"num": 3.4, "s": "Text"},
...     "arr": [10, 20, 30],
... }
>>> json_get(j, "/foo/num")
3.4
>>> json_get(j, "/arr[1]")
20
>>> json_get(j, "/foo/unknown")
Traceback (most recent call last):
    ...
ValueError: JSON path '/foo/unknown' not found

Values are optionally checked against one of the following types:
str, int, float, bool, list, and dict. Checking for null values is not
supported.

>>> json_get(j, "/foo/num", str)
Traceback (most recent call last):
    ...
TypeError: wrong JSON type str != float

float will match any number, int will only match numbers without
a fractional part.

>>> json_get(j, "/foo/num", float)
3.4
>>> json_get(j, "/foo/num", int)
Traceback (most recent call last):
    ...
TypeError: wrong JSON type int != float
