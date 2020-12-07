Python JSON Get
===============

.. image:: https://img.shields.io/pypi/l/json-get.svg
   :target: https://pypi.python.org/pypi/json-get/
.. image:: https://img.shields.io/github/release/srittau/python-json-get/all.svg
   :target: https://github.com/srittau/python-json-get/releases/
.. image:: https://img.shields.io/pypi/v/json-get.svg
   :target: https://pypi.python.org/pypi/json-get/
.. image:: https://img.shields.io/github/workflow/status/srittau/python-json-get/test-and-lint
   :target: https://github.com/srittau/python-json-get/actions

Get values from JSON objects usings a path expression. Optional type
checking is possible:

>>> from jsonget import json_get, json_get_default, JList
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
``str``, ``int``, ``float``, ``bool``, ``list``, and ``dict``.
Checking for null values is not supported:

>>> json_get(j, "/foo/num", str)
Traceback (most recent call last):
    ...
TypeError: wrong JSON type str != float

``float`` will match any number, ``int`` will only match numbers without
a fractional part:

>>> json_get(j, "/foo/num", float)
3.4
>>> json_get(j, "/foo/num", int)
Traceback (most recent call last):
    ...
TypeError: wrong JSON type int != float

Additionally, the type of list values can be checked:

>>> json_get(j, "/arr", JList(int))
[10, 20, 30]

``json_get_default()`` can be used to return a default value if a given
path does not exist:

>>> json_get_default(j, "/bar", "default value")
'default value'
