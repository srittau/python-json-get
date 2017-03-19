#!/usr/bin/python3

from setuptools import setup


setup(
    name="json-get",
    version="1.0",
    description="Get values from JSON objects using a path expression",
    author="Sebastian Rittau",
    author_email="srittau@rittau.biz",
    url="https://github.com/srittau/python-json-get",
    py_modules=["jsonget", "jsonget_test"],
    tests_require=["asserts >= 0.6"],
    license="MIT",
)
