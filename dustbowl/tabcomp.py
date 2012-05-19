# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 John Hampton <pacopablo@pacopablo.com>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.
#
# Author: John Hampton <pacopablo@pacopablo.com>

def enable_tabbed_completion(historyPath='.dustbowl.hist', context=None):
    import atexit
    import os
    import readline
    import rlcompleter

    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind ("bind ^I rl_complete")
    if 'libedit' in readline.__doc__:
        readline.parse_and_bind('bind "\e[3~" ed-delete-next-char')

    context = context or globals()
    readline.set_completer(rlcompleter.Completer(context).complete)

    def save_history(historyPath=historyPath):
        import readline
        readline.write_history_file(historyPath)

    if os.path.exists(historyPath):
        readline.read_history_file(historyPath)

    atexit.register(save_history)
    del os, atexit, readline, rlcompleter, save_history, historyPath
