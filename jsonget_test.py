from unittest.case import TestCase

from asserts import assert_raises, assert_succeeds, assert_equal, \
    assert_raises_regex

from jsonget import assert_json_type, json_get


class AssertJsonTypeTest(TestCase):

    def test_str(self):
        with assert_succeeds(TypeError):
            assert_json_type("abc", str)
        with assert_raises(TypeError):
            assert_json_type(45, str)

    def test_int(self):
        with assert_succeeds(TypeError):
            assert_json_type(45, int)
        with assert_raises(TypeError):
            assert_json_type("313", int)
        with assert_raises(TypeError):
            assert_json_type(45.3, int)

    def test_float(self):
        with assert_succeeds(TypeError):
            assert_json_type(45.3, float)
        with assert_succeeds(TypeError):
            assert_json_type(45, float)
        with assert_raises(TypeError):
            assert_json_type("45.3", float)

    def test_bool(self):
        with assert_succeeds(TypeError):
            assert_json_type(True, bool)
        with assert_raises(TypeError):
            assert_json_type(0, bool)

    def test_list(self):
        with assert_succeeds(TypeError):
            assert_json_type(["foo", "bar"], list)
        with assert_raises(TypeError):
            assert_json_type(0, list)

    def test_dict(self):
        with assert_succeeds(TypeError):
            assert_json_type({"foo": "bar"}, dict)
        with assert_raises(TypeError):
            assert_json_type(0, dict)

    def test_null(self):
        with assert_succeeds(TypeError):
            assert_json_type(None, None)
        with assert_raises(TypeError):
            assert_json_type(0, None)


class JsonGetTest(TestCase):

    def test_empty_path_elements(self):
        with assert_raises(ValueError):
            json_get({}, "/foo")
        with assert_raises(ValueError):
            json_get({"foo": 1}, "foo/")
        with assert_raises(ValueError):
            json_get({"foo": {"bar": 1}}, "foo//bar")
        with assert_raises(ValueError):
            json_get([{"foo": 1}], "[0]foo")

    def test_empty_path(self):
        j = {"foo": "bar"}
        assert_equal(j, json_get(j, ""))

    def test_slash_only(self):
        j = {"foo": "bar"}
        assert_equal(j, json_get(j, "/"))

    def test_ignore_leading_slash(self):
        j = {"foo": 44}
        assert_equal(44, json_get(j, "/foo"))

    def test_sub_path(self):
        j = {"foo": {"bar": 44}}
        assert_equal(44, json_get(j, "foo/bar"))

    def test_sub_path_missing(self):
        j = {"foo": {"bar": 44}}
        with assert_raises(ValueError):
            json_get(j, "foo/baz")

    def test_string_is_not_a_sub_path(self):
        j = {"foo": "abc"}
        with assert_raises_regex(
                TypeError, "JSON path '/foo' is not an object"):
            json_get(j, "foo/bar/baz")

    def test_int_is_not_a_sub_path(self):
        j = {"foo": {"num": 3.4}}
        with assert_raises_regex(
                TypeError, "JSON path '/foo/num' is not an object"):
            json_get(j, "/foo/num/bar")

    def test_correct_type(self):
        j = {"foo": 44}
        json_get(j, "foo", int)

    def test_wrong_type(self):
        j = {"foo": 44}
        with assert_raises(TypeError):
            json_get(j, "foo", str)

    def test_root_array(self):
        j = ["a", "b", "c"]
        assert_equal("b", json_get(j, "[1]"))

    def test_array_in_object(self):
        j = {"foo": ["a", "b", "c"]}
        assert_equal("b", json_get(j, "foo[1]"))

    def test_nested_arrays(self):
        j = [["a0", "b0"], ["a1", "b1"], ["a2", "b2"]]
        assert_equal("a1", json_get(j, "[1][0]"))

    def test_mixed_objects_and_arrays(self):
        j = [{}, {"foo": ["a", "b", "c"]}]
        assert_equal("c", json_get(j, "[1]/foo[2]"))

    def test_int_not_an_array(self):
        j = {"foo": 42}
        with assert_raises_regex(
                TypeError, "JSON path '/foo' is not an array"):
            json_get(j, "foo[0]")

    def test_string_not_an_array(self):
        j = {"foo": "bar"}
        with assert_raises_regex(
                TypeError, "JSON path '/foo' is not an array"):
            json_get(j, "foo[0]")

    def test_object_not_an_array(self):
        j = {"foo": {}}
        with assert_raises_regex(
                TypeError, "JSON path '/foo' is not an array"):
            json_get(j, "foo[0]")

    def test_array_out_of_bound(self):
        j = {"foo": [1, 2, 3]}
        expected_message = r"JSON array '/foo' too small \(3 <= 4\)"
        with assert_raises_regex(IndexError, expected_message):
            json_get(j, "foo[4]")

    def test_error_path(self):
        j = {"foo": [None, {"bar": []}]}
        expected_message = r"JSON array '/foo\[1\]/bar' too small \(0 <= 0\)"
        with assert_raises_regex(IndexError, expected_message):
            json_get(j, "foo[1]/bar[0]")
