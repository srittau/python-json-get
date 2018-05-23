from unittest import TestCase

from asserts import assert_raises, assert_succeeds, assert_equal, \
    assert_raises_regex

from jsonget import JsonValue, json_get_default, JList
from jsonget import assert_json_type, json_get


class AssertJsonTypeTest(TestCase):
    def test_str(self) -> None:
        with assert_succeeds(TypeError):
            assert_json_type("abc", str)
        with assert_raises(TypeError):
            assert_json_type(45, str)

    def test_int(self) -> None:
        with assert_succeeds(TypeError):
            assert_json_type(45, int)
        with assert_raises(TypeError):
            assert_json_type("313", int)
        with assert_raises(TypeError):
            assert_json_type(45.3, int)

    def test_float(self) -> None:
        with assert_succeeds(TypeError):
            assert_json_type(45.3, float)
        with assert_succeeds(TypeError):
            assert_json_type(45, float)
        with assert_raises(TypeError):
            assert_json_type("45.3", float)

    def test_bool(self) -> None:
        with assert_succeeds(TypeError):
            assert_json_type(True, bool)
        with assert_raises(TypeError):
            assert_json_type(0, bool)

    def test_list(self) -> None:
        with assert_succeeds(TypeError):
            assert_json_type(["foo", "bar"], list)
        with assert_raises(TypeError):
            assert_json_type(0, list)

    def test_dict(self) -> None:
        with assert_succeeds(TypeError):
            assert_json_type({"foo": "bar"}, dict)
        with assert_raises(TypeError):
            assert_json_type(0, dict)

    def test_null(self) -> None:
        with assert_succeeds(TypeError):
            assert_json_type(None, None)
        with assert_raises(TypeError):
            assert_json_type(0, None)

    def test_expected_null_exception_message(self) -> None:
        with assert_raises_regex(TypeError, "wrong JSON type None != str"):
            assert_json_type("", None)

    def test_did_not_expect_null_exception_message(self) -> None:
        with assert_raises_regex(TypeError, "wrong JSON type str != None"):
            assert_json_type(None, str)

    def test_jlist__empty_list(self) -> None:
        assert_json_type([], JList(int))

    def test_jlist__all_match(self) -> None:
        assert_json_type([1, 2, 3], JList(int))

    def test_jlist__nested(self) -> None:
        assert_json_type([[1, 2, 3], [], [4]], JList(JList(int)))

    def test_jlist__not_a_list(self) -> None:
        with assert_raises_regex(TypeError, "wrong JSON type list != str"):
            assert_json_type("foo", JList(str))

    def test_jlist__no_match(self) -> None:
        with assert_raises_regex(TypeError, "wrong JSON type int != str"):
            assert_json_type(["foo", "bar"], JList(int))

    def test_jlist__any_does_not_match(self) -> None:
        with assert_raises_regex(TypeError, "wrong JSON type int != str"):
            assert_json_type([45, "bar"], JList(int))


class JsonGetTest(TestCase):
    def test_empty_path_elements(self) -> None:
        with assert_raises(ValueError):
            json_get({}, "/foo")
        with assert_raises(ValueError):
            json_get({"foo": 1}, "foo/")
        with assert_raises(ValueError):
            json_get({"foo": {"bar": 1}}, "foo//bar")
        with assert_raises(ValueError):
            json_get([{"foo": 1}], "[0]foo")

    def test_empty_path(self) -> None:
        j = {"foo": "bar"}
        assert_equal(j, json_get(j, ""))

    def test_slash_only(self) -> None:
        j = {"foo": "bar"}
        assert_equal(j, json_get(j, "/"))

    def test_ignore_leading_slash(self) -> None:
        j = {"foo": 44}
        assert_equal(44, json_get(j, "/foo"))

    def test_sub_path(self) -> None:
        j = {"foo": {"bar": 44}}
        assert_equal(44, json_get(j, "foo/bar"))

    def test_sub_path_missing(self) -> None:
        j = {"foo": {"bar": 44}}
        with assert_raises(ValueError):
            json_get(j, "foo/baz")

    def test_string_is_not_a_sub_path(self) -> None:
        j = {"foo": "abc"}
        with assert_raises_regex(TypeError,
                                 "JSON path '/foo' is not an object"):
            json_get(j, "foo/bar/baz")

    def test_int_is_not_a_sub_path(self) -> None:
        j = {"foo": {"num": 3.4}}
        with assert_raises_regex(TypeError,
                                 "JSON path '/foo/num' is not an object"):
            json_get(j, "/foo/num/bar")

    def test_correct_type(self) -> None:
        j = {"foo": 44}
        json_get(j, "foo", int)

    def test_wrong_type(self) -> None:
        j = {"foo": 44}
        with assert_raises(TypeError):
            json_get(j, "foo", str)

    def test_root_array(self) -> None:
        j = ["a", "b", "c"]
        assert_equal("b", json_get(j, "[1]"))

    def test_array_in_object(self) -> None:
        j = {"foo": ["a", "b", "c"]}
        assert_equal("b", json_get(j, "foo[1]"))

    def test_nested_arrays(self) -> None:
        j = [["a0", "b0"], ["a1", "b1"], ["a2", "b2"]]
        assert_equal("a1", json_get(j, "[1][0]"))

    def test_mixed_objects_and_arrays(self) -> None:
        j = [{}, {"foo": ["a", "b", "c"]}]
        assert_equal("c", json_get(j, "[1]/foo[2]"))

    def test_int_not_an_array(self) -> None:
        j = {"foo": 42}
        with assert_raises_regex(TypeError,
                                 "JSON path '/foo' is not an array"):
            json_get(j, "foo[0]")

    def test_string_not_an_array(self) -> None:
        j = {"foo": "bar"}
        with assert_raises_regex(TypeError,
                                 "JSON path '/foo' is not an array"):
            json_get(j, "foo[0]")

    def test_object_not_an_array(self) -> None:
        j = {"foo": {}}  # type: JsonValue
        with assert_raises_regex(TypeError,
                                 "JSON path '/foo' is not an array"):
            json_get(j, "foo[0]")

    def test_array_out_of_bound(self) -> None:
        j = {"foo": [1, 2, 3]}
        expected_message = r"JSON array '/foo' too small \(3 <= 4\)"
        with assert_raises_regex(IndexError, expected_message):
            json_get(j, "foo[4]")

    def test_error_path(self) -> None:
        j = {"foo": [None, {"bar": []}]}  # type: JsonValue
        expected_message = r"JSON array '/foo\[1\]/bar' too small \(0 <= 0\)"
        with assert_raises_regex(IndexError, expected_message):
            json_get(j, "foo[1]/bar[0]")


class JsonGetDefaultTest(TestCase):
    def test_path_exists(self) -> None:
        j = {"foo": {"bar": 123}}
        v = json_get_default(j, "/foo/bar", None)
        assert_equal(123, v)

    def test_path_does_not_exist(self) -> None:
        j = {"baz": 0}
        v = json_get_default(j, "/foo/bar", "default value")
        assert_equal("default value", v)

    def test_index_does_not_exist(self) -> None:
        j = {
            "foo": [1, 2, 3],
        }
        v = json_get_default(j, "/foo[10]", 42)
        assert_equal(42, v)

    def test_type_does_not_match(self) -> None:
        j = {"foo": "bar"}
        with assert_raises(TypeError):
            json_get_default(j, "/foo", None, int)
