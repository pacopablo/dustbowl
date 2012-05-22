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
import logging

# Third Party Imports

# Local Imports
from dustbowl.api import IShellCommandProvider, Component, implements

__all__ = [
    'LogCmdProvider',
]

#noinspection PyInitNewSignature
class LogCmdProvider(Component):
    """ Shows the messages that have been logged.

    The log command requires one of the following arguements:
     * show
     * save
     * clear

    show:  Will show all unread log messages.  If passed the 'all' parameter, all
           log message with be shown regardless of read status.
    save:  Must be passed the name of a file.  The log will be saved to the
           specified file.  The file will be overwritten if it already exists.
    clear: Clears the log.

    Examples:
     1) >>> .log.show
     1) >>> .log.show.all
     1) >>> .log.save 'logfile.log'
     1) >>> .log.clear
    """

    implements(IShellCommandProvider)

    def __init__(self):
        self.level = self.log.getEffectiveLevel()

    def match(self, cmd):
        c = cmd.lower()
        return c == 'log' or c.startswith('log.')

    def run(self, cmd, *args, **kwargs):
        cmds = cmd.split('.')
        num_cmds = len(cmds)
        if num_cmds == 1:
            self.log.log(self.level, *args, **kwargs)
        elif num_cmds > 1:
            f = getattr(self, '_log_%s' % cmds[1], None)
            if f:
                f(cmd, *args, **kwargs)

    def _log_setlevel(self, *args, **kwargs):
        if len(*args) < 1:
            print("A logging level of DEBUG, INFO, WARNING, ERROR, or CRITICAL must be specified.")
            print("The current log level is: %s" % logging._levelNames[self.level])
        else:
            level = args[0]
            if isinstance(level, basestring) and \
               level.upper() in logging._levelNames:
                self.level = logging._levelNames[level]
            elif isinstance(level, int) and level in logging._levelNames:
                self.level = level
            else:
                print("Unknown logging level %s.  Log level remains: %s" %
                        (level, logging._levelNames[self.level]))
        pass

    def _log_show(self, cmd, *args, **kwargs):
        """ Show log entries in the console.

        When invoked as .log.show, all log entries that have not yet been
        viewed are shown.  If invoked as .log.show.all, the entire log is
        shown, regardless of whether it has been seen previously.
        """
        startidx = getattr(self, 'startidx', 0)
        length = self.log._buffer_hndlr.get_length()

        cmds = cmd.split('.')
        showall = cmds[2:3]
        if not showall:
            text = '\n  '.join(self.log._buffer_hndlr.get_lines(startidx))
        elif showall[0].lower() == 'all':
            text = '\n  '.join(self.log._buffer_hndlr.get_lines())
        else:
            text = '\n'
        print('  ' + text)
        self.startidx = length
        return False

    def _log_save(self, *args, **kwargs):
        print('Not Implemented yet')
        return False

    def _log_clear(self, *args, **kwargs):
        self.log._buffer_hndlr.clear_log()
        self.startidx = 0
        print('Log Cleared')
        return False
