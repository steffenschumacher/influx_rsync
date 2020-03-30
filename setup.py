# coding: utf-8
from setuptools import setup, find_packages  # noqa: H301

NAME = "influx_rsync"
VERSION = "1.0.0"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
    "influxdb"
]

setup(
    name=NAME,
    version=VERSION,
    description="influx_rsync incrementally copies data from one db to another",
    author_email="ssch@wheel.dk",
    url="",
    keywords=["influxdb", "influx_rsync"],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    include_package_data=True,
    install_requires=REQUIRES,
    setup_requires=[
        'pytest-runner', 'wheel', 'twine'
    ],
    packages=find_packages(),
    long_description="""\
    influx_rsync
    """
)
