#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 John Hampton <pacopablo@pacopablo.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: John Hampton <pacopablo@pacopablo.com>

from setuptools import setup

setup(
    name='Dustbowl',
    version='1.0.1',
    packages=['dustbowl', 'dustbowl.plugins'],
    author='John Hampton',
    author_email='pacopablo@pacopablo.com',
    description='Dustbowl',
    scripts=['scripts/dustbowl'],
    url='http://pacopablo.github.com/dustbowl',
    install_requires = ['SQLAlchemy', 'colorama'],
    license='MIT',
    zip_safe = False,
    entry_points = """
        [dustbowl.modules]
        dustbowl.plugins.logcmd = dustbowl.plugins.logcmd
        dustbowl.plugins.datasources = dustbowl.plugins.datasources
        dustbowl.plugins.config = dustbowl.plugins.config
        dustbowl.plugins.modules = dustbowl.plugins.modules
    """,
    long_description = """
    Dustbowl
    ==========

    Dustbowl is an InteractiveConsole_ that allows for loading plugins.  These
    plugins are python packages that ``[dustbowl.modules]`` entry points.  One
    can create plugins for commonly repeated tasks.  The benefit to using an
    InteractiveConsole_ is that once a method from a plugin has been run, one
    can further inspect and manipulate its results and data.  Thus we have all
    the power of the Python REPL with assisting functions and commands.

    .. Links
    .. _InteractiveConsole: http://docs.python.org/library/code.html#code.InteractiveConsole
    """

)

