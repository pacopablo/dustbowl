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
    description='Dustbowl',
    scripts=['scripts/dustbowl'],
    url='http://pacopablo.github.com/dustbowl',
    license='MIT',
    zip_safe = False,
    entry_points = """
        [dustbowl.modules]
        dustbowl.plugins.logcmd = dustbowl.plugins.logcmd
        dustbowl.plugins.datasources = dustbowl.plugins.datasources
        dustbowl.plugins.config = dustbowl.plugins.config
    """
)

