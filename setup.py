#!/usr/bin/env python3

import os.path
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="json-get",
    version="2.0.0",
    description="Get values from JSON objects using a path expression",
    long_description=read("README.rst"),
    author="Sebastian Rittau",
    author_email="srittau@rittau.biz",
    url="https://github.com/srittau/python-json-get",
    packages=["jsonget", "jsonget_test"],
    package_data={"jsonget": ["py.typed"]},
    python_requires=">=3.7",
    tests_require=["asserts>=0.6, <0.12"],
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development",
    ]
)
