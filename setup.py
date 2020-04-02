#!/usr/bin/env python

try:
    from distutils.core import setup
except ImportError:
    from setuptools import setup
from catkin_pkg.python_setup import generate_distutils_setup

d = generate_distutils_setup(
    packages=['rqt_robot_dashboard'],
    package_dir={'': 'src'}
)

setup(**d)
