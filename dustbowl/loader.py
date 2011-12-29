# -*- coding: utf-8 -*-
#
# Modifcations Copyright (C) 2009 John Hampton <pacopablo@pacopablo.com>
#
# Original code from Trac trunk r8199 
# http://svn.edgewall.org/reops/trac/trunk
#
# Original Copyright and License:
# Copyright (C) 2005-2009 Edgewall Software
# Copyright (C) 2005-2006 Christopher Lenz <cmlenz@gmx.de>
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution. The terms
# are also available at http://trac.edgewall.org/wiki/TracLicense.
#
# This software consists of voluntary contributions made by many
# individuals. For the exact contribution history, see the revision
# history and logs, available at http://trac.edgewall.org/log/.
#
# Author: Christopher Lenz <cmlenz@gmx.de>

# Standard Library Imports
import os
import sys
import imp
from glob import glob

# Third Party Imports
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict, UnknownExtra

# Local Imports
from util import exception_to_unicode


__all__ = ['load_plugins']


def _enable_plugin(env, module):
    """Enable the given plugin module by adding an entry to the configuration.
    """
    if module + '.*' not in env.config['components']:
        env.config['components'].set(module + '.*', 'enabled')


def _log_error(env, item, e):
    ue = exception_to_unicode(e)
    if isinstance(e, DistributionNotFound):
        env.log.debug('Skipping "%s": ("%s" not found)', item, ue)
    elif isinstance(e, VersionConflict):
        env.log.error('Skipping "%s": (version conflict "%s")',
                      item, ue)
    elif isinstance(e, UnknownExtra):
        env.log.error('Skipping "%s": (unknown extra "%s")', item, ue)
    elif isinstance(e, ImportError):
        env.log.error('Skipping "%s": (can\'t import "%s")', item, ue)
    else:
        env.log.error('Skipping "%s": (error "%s")', item, ue)


def load_eggs(env, paths, entry_point, auto_enable=False):
    """Loader that loads any eggs in the plugin directory."""
    # Note that the following doesn't seem to support unicode search_path
    ws = pkg_resources.WorkingSet([])
    distributions, errors = ws.find_plugins(pkg_resources.Environment(paths))


    for dist in distributions:
        env.log.debug('Found plugin %s at %s', dist, dist.location)
        ws.add(dist)

    for dist, e in errors.iteritems():
        _log_error(env, dist, e)

    for entry in ws.iter_entry_points(entry_point):
        env.log.debug('Loading %s from %s', entry.name, entry.dist)
        try:
            # We need to make sure the distribution is on the path before we can load it.
            entry.dist.activate()
            entry.load(require=True)
        except (ImportError, DistributionNotFound, VersionConflict,
                UnknownExtra), e:
            """ Print the last traceback to the debug buffer """
            _log_error(env, entry, e)
        else:
            if auto_enable:
                _enable_plugin(env, entry.module_name)


def load_plugins(env, entry_point, paths=[], auto_enable=False):
    """Load all plugin components found on the given search path."""
    load_eggs(env, paths, entry_point, auto_enable=auto_enable)
