# -*- coding: utf-8 -*-
#
# Copyright (C) 2009, John Hampton <pacopablo@pacopablo.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: John Hampton <pacopablo@pacopablo.com>

# Standard library imports
import sys
from code import InteractiveConsole, compile_command

# Third Party imports
import colorama
from colorama import Fore, Style

# Local imports
import dustbowl.env

VERSION = '1.0.1'

CMD_TOKEN = "."

class DustbowlConsole(InteractiveConsole):

    def __init__(self, locals=None, filename="<console>", args=None, logger=None):
        InteractiveConsole.__init__(self, locals=locals, filename=filename)
        self.args = args
        self.locals = locals
        self.env = dustbowl.env.Environment(args.config,
                                          'dustbowl.modules',
                                          args.plugins,
                                          logger,
                                          self.locals)
        self.locals['__env__'] = self.env

    def interact(self, banner=None):
        global CMD_TOKEN

        # So, these two try statements don't seem very Pythonic.  I'm game
        # for a nicer way to determine whether or not ``ps1`` and ``ps2`` exist
        try:
            sys.ps1
        except AttributeError:
            sys.ps1 = ">>> "
        try:
            sys.ps2
        except AttributeError:
            sys.ps2 = "... "
        cprt = 'Type "help", "copyright", "credits" or "license" for more information.'
        colorama.init()
        if banner is None:
            self.write(Style.BRIGHT + Fore.BLUE + "Dustbowl" + Fore.RESET +
                       Style.NORMAL + ": Python %s on %s\n%s\n" %
                       (sys.version, sys.platform, cprt))
        else:
            self.write("%s\n" % str(banner))
        for i in self.env.plugin_data.itervalues():
            if i['loaded']:
                self.write(Style.DIM + "Loaded %s\n" % i['entry'].name +
                           Style.NORMAL)
        if 'readline' in sys.modules:
            self.write("Dustbowl Tabbed Completion Enabled\n")

        more = 0
        while 1:
            try:
                if more:
                    prompt = sys.ps2
                else:
                    prompt = sys.ps1
                try:
                    line = self.raw_input(prompt)
                    # Can be None if sys.stdin was redefined
                    encoding = getattr(sys.stdin, "encoding", None)
                    if encoding and not isinstance(line, unicode):
                        line = line.decode(encoding)
                except EOFError:
                    self.write("\n")
                    break
                else:
                    if line.strip().startswith(CMD_TOKEN):
                        line = self.process_command(line)
                    more = self.push(line)
            except KeyboardInterrupt:
                self.write("\nKeyboardInterrupt\n")
                self.resetbuffer()
                more = 0

    def process_command(self, line):
        global CMD_TOKEN
        pos = line.find(CMD_TOKEN)
        if pos >= 0:
            parts = line[pos:].split(' ')
            cmd = parts[0]
            args = ' '.join(parts[1:])
            return '%s__env__("%s"%s)' % (line[:pos], cmd.lstrip(CMD_TOKEN), args and ', ' + args or '') 
        else:
            return line
