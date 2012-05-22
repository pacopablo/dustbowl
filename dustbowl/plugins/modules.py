# -*- coding: utf-8 -*-
#
# Copyright (C) 2012 John Hampton <pacopablo@pacopablo.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: John Hampton <pacopablo@pacopablo.com>

__author__ = 'John Hampton'

# Std Library Imports

# Local Imports

# Third Party Imports
from dustbowl.api import IShellCommandProvider, Component, implements


__all__ = [
    'ModuleCmdProvider',
    ]

#noinspection PyInitNewSignature
class ModuleCmdProvider(Component):
    """ Enables management of plugin modules.

    The module command requires one of the following arguments:
     * list
     * enable
     * disable

    list:  Will show all unread log messages.  If passed the 'all' parameter,
    all
           log message with be shown regardless of read status.
    enable:  Must be passed the name of a file.  The log will be saved to the
           specified file.  The file will be overwritten if it already exists.
    disable: Clears the log.

    Examples:
     1) >>> .module.list
     1) >>> .module.list all
     1) >>> .module.list enabled
     1) >>> .module.list disabled
     1) >>> .module enable 'module_spec'
     1) >>> .module.disable 'nodule_spec'
    """

    implements(IShellCommandProvider)

    def match(self, cmd):
        c = cmd.lower()
        return c == 'module' or c.startswith('module.')

    def run(self, cmd, *args, **kwargs):
        cmds = cmd.split('.')
        num_cmds = len(cmds)
        if num_cmds == 1:
            self.log.log(self.level, *args, **kwargs)
        elif num_cmds > 1:
            f = getattr(self, '_log_%s' % cmds[1], None)
            if f:
                f(cmd, *args, **kwargs)
