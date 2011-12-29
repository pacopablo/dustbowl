# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 John Hampton <pacopablo@pacopablo.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: John Hampton <pacopablo@pacopablo.com>

# Standard Library Imports

# Third Party Imports

# Local Imports
from dustbowl.api import IShellConsoleObjectProvider, Component, implements

__all__ = [
    'ConfigManager',
]

class ConfigManager(Component):
    """ Provides access ot the config object """

    implements(IShellConsoleObjectProvider)

    def get_console_objects(self):
        """ Add access to the config object.

        TODO: This should probably be replaced by a plugin that provides a
        nicer interface to the config data
        """
        yield ('shellconfig', self.config)
