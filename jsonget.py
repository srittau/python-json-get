import re
from typing import Union, Type, List, cast

JsonType = Union[
    Type[str], Type[int], Type[float], Type[bool], Type[list], Type[dict], None
]
JsonValue = Union[str, int, float, bool, list, dict, None]
JsonPathElement = Union[str, int]
JsonPath = List[JsonPathElement]


def assert_json_type(value: JsonValue, expected_type: JsonType) -> None:
    """Check that a value has a certain JSON type.

    Raise TypeError if the type does not match.

    Supported types: str, int, float, bool, list, dict, and None.
    float will match any number, int will only match numbers without
    fractional part.
    """

    def type_name(t):
        if t is None:
            return "None"
        return t.__name__

    if expected_type is None:
        if value is None:
            return
    elif expected_type == float:
        if isinstance(value, float) or isinstance(value, int):
            return
    elif expected_type in [str, int, bool, list, dict]:
        if isinstance(value, expected_type):
            return
    else:
        raise TypeError("unsupported type")
    raise TypeError("wrong JSON type {} != {}".format(
        type_name(expected_type), type_name(type(value))))


def _parse_json_path(path):
    index_re = re.compile(r"\[(\d+)\]")
    full_index_re = re.compile(r"^(\[\d+\])+$")
    element_re = re.compile(r"^(.+?)(\[\d+\])*$")

    def parse_element(s: str) -> JsonPath:
        m = element_re.match(s)
        if not m:
            raise ValueError("invalid JSON path '{}'".format(path))
        indexes = parse_indexes(m.group(2)) if m.group(2) else []
        return [m.group(1)] + indexes

    def parse_indexes(s: str) -> JsonPath:
        return [int(i) for i in index_re.findall(s)]

    if path in ["", "/"]:
        return []

    if path[0] not in ["[", "/"]:
        path = "/" + path

    elements = path.split("/")
    if elements[0] and not full_index_re.match(elements[0]):
        raise ValueError("invalid JSON path '{}'".format(path))
    parsed = parse_indexes(elements[0])
    for element in elements[1:]:
        parsed.extend(parse_element(element))
    return parsed


ANY = "any"


def json_get(json: JsonValue, path: str,
             expected_type: Union[JsonType, str] = ANY) -> JsonValue:
    """Get a JSON value by path, optionally checking its type.

        >>> j = {"foo": {"num": 3.4, "s": "Text"}, "arr": [10, 20, 30]}
        >>> json_get(j, "/foo/num")
        3.4
        >>> json_get(j, "/arr[1]")
        20

    Raise ValueError if the path is not found:

        >>> json_get(j, "/foo/unknown")
        Traceback (most recent call last):
            ...
        ValueError: JSON path '/foo/unknown' not found

    Raise TypeError if the path contains a non-object element:

        >>> json_get(j, "/foo/num/bar")
        Traceback (most recent call last):
            ...
        TypeError: JSON path '/foo/num' is not an object

    Or a non-array element:

        >>> json_get(j, "/foo[2]")
        Traceback (most recent call last):
            ...
        TypeError: JSON path '/foo' is not an array

    Raise an IndexError if the array index is out of bounds:

        >>> json_get(j, "/arr[10]")
        Traceback (most recent call last):
            ...
        IndexError: JSON array '/arr' too small (3 <= 10)

    Recognized types are: str, int, float, bool, list, dict, and None.
    TypeError is raised if the type does not match.

        >>> json_get(j, "/foo/num", str)
        Traceback (most recent call last):
            ...
        TypeError: wrong JSON type str != float

    float will match any number, int will only match numbers without a
    fractional part.

        >>> json_get(j, "/foo/num", float)
        3.4
        >>> json_get(j, "/foo/num", int)
        Traceback (most recent call last):
            ...
        TypeError: wrong JSON type int != float
    """

    elements = _parse_json_path(path)

    current = json
    current_path = ""
    for i, element in enumerate(elements):
        if isinstance(element, str):
            if not isinstance(current, dict):
                msg = "JSON path '{}' is not an object".format(current_path)
                raise TypeError(msg) from None
            if element not in current:
                raise ValueError("JSON path '{}' not found".format(path))
            current_path += "/" + element
        else:
            if not isinstance(current, list):
                msg = "JSON path '{}' is not an array".format(current_path)
                raise TypeError(msg) from None
            if element >= len(current):
                msg = "JSON array '{}' too small ({} <= {})".format(
                    current_path, len(current), element)
                raise IndexError(msg)
            current_path += "[{}]".format(i)
        current = current[element]
    if expected_type != ANY:
        assert_json_type(current, cast(JsonType, expected_type))
    return current
