# -*- coding: utf-8 -*-
#
# Modifcations Copyright (C) 2009 John Hampton <pacopablo@pacopablo.com>
#
# Original code from Trac trunk r8199
# http://svn.edgewall.org/reops/trac/trunk
#
# Original Copyright and License:
# Copyright (C) 2003-2009 Edgewall Software
# Copyright (C) 2003-2007 Jonas Borgström <jonas@edgewall.com>
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
# Author: Jonas Borgström <jonas@edgewall.com>

# Standard Library imports
import sys
import os.path
import inspect

# Third Party imports
import pkg_resources
from pkg_resources import DistributionNotFound, VersionConflict, UnknownExtra

# Local imports
from api import Component, ComponentManager, Interface, IShellCommandProvider
from api import ExtensionPoint, IShellConsoleObjectProvider, DustbowlObj
from error import ConsoleObjectError
from config import Configuration
from log import NullLogger
from util import format_exception

__all__ = [
    'Environment',
    'IEnvObjectProvider',
]


class IEnvObjectProvider(Interface):
    def get_console_objects(self):
        """ Return an iterable of 2-tuples of (key, value) pairs.

        The value will be attached to the environment as the given key
        """


class Environment(Component, ComponentManager):
    """The environment loads plugins """

    commands = ExtensionPoint(IShellCommandProvider)
    console_objects = ExtensionPoint(IShellConsoleObjectProvider)
    env_objects = ExtensionPoint(IEnvObjectProvider)

    def __init__(self, config=None, entry_point=None, plugins=None,
                logger=None, locals=None):
        """Initialize the Dustbowl environment.

        @param config: the absolute path to a configuration file.
        @param entry_point: The entry point used to locate plugins.
        @param plugins: a list of tuples containing paths in which to look for
                        plugins and a boolean indicating whether or not
                        plugins loaded from the specified path should be
                        auto-enabled.
        @param logger: a Python logger instance.

        ``sys.path`` will be automatically added to the list of plugin
        directories.  All entries of ``sys.path`` will not be auto-enabled.
        """
        ComponentManager.__init__(self)


        self.setup_config(config)
        self.setup_log(logger)

        # Load plugins
        self.plugin_data = dict()
        if not plugins:
            plugins = list()
        self.load_modules(plugins, entry_point=entry_point)

        if locals:
            self.parent_locals = locals

        for provider in self.console_objects:
            for key, value in provider.get_console_objects():
                self.add_console_object(key, value, provider.__class__.__name__)
                continue
            continue

        for provider in self.env_objects:
            for key, value in provider.get_env_objects():
                self.add_env_object(key, value, provider.__class__.__name__)
                continue
            continue


    def component_activated(self, component):
        """Initialize additional member variables for components.

        Every component activated through the `Environment` object gets three
        member variables: `env` (the environment object), `config` (the
        environment configuration) and `log` (a logger object)."""
        component.env = self
        component.config = self.config
        component.log = self.log

    def is_component_enabled(self, cls):
        """Implemented to only allow activation of components that are not
        disabled in the configuration.

        This is called by the `ComponentManager` base class when a component is
        about to be activated. If this method returns false, the component does
        not get activated."""
        if not isinstance(cls, basestring):
            component_name = (cls.__module__ + '.' + cls.__name__).lower()
        else:
            component_name = cls.lower()

        for key, value in self.plugin_data.iteritems():
            if component_name == key or component_name.startswith(key + '.'):
                value['activated'] = True
                return value['loaded']
        return False

    def setup_config(self, configpath):
        """Load the configuration file."""
        self.config = Configuration(configpath)

    def setup_log(self, logger):
        """Initialize the logging sub-system."""
        if logger:
            self.log = logger
        else:
            self.log = NullLogger()

    def is_enabled(self, module_name):
        """ Return whether a module is enabled in the config.
        """
        for key, value in self.config.options('components'):
            k = key.lower()
            mod = module_name.lower()
            if mod == k or k.endswith('*') and mod.startswith(k[:-1]):
                return self.config.getbool('components', key)
        return False

    def load_modules(self, plugins=None, entry_point='dustbowl.modules'):
        """ Load plugins """
        def _log_error(item, e):
            ue = format_exception(e)
            if isinstance(e, DistributionNotFound):
                self.log.debug('Skipping "%s": ("%s" not found)', item, ue)
            elif isinstance(e, VersionConflict):
                self.log.error('Skipping "%s": (version conflict "%s")',
                              item, ue)
            elif isinstance(e, UnknownExtra):
                self.log.error('Skipping "%s": (unknown extra "%s")', item, ue)
            elif isinstance(e, ImportError):
                self.log.error('Skipping "%s": (can\'t import "%s")', item, ue)
            else:
                self.log.error('Skipping "%s": (error "%s")', item, ue)

        ws = pkg_resources.WorkingSet(sys.path)

        # Look for core modules
        ws.add_entry(os.path.dirname(
                        pkg_resources.resource_filename(__name__, '')))
        for entry in ws.iter_entry_points(entry_point):
            if entry.name.startswith('dustbowl.plugins'):
                entry_data = {
                    'entry' : entry,
                    'loaded' : False,
                    'activated' : False,
                    'auto_enable' : True,
                }
                self.plugin_data.setdefault(entry.name, entry_data)

        # Look for modules in sys.path
        for p in sys.path:
            ws.add_entry(p)
        for entry in ws.iter_entry_points(entry_point):
            entry_data = {
                'entry' : entry,
                'loaded' : False,
                'activated' : False,
                'auto_enable' : False,
            }
            self.plugin_data.setdefault(entry.name, entry_data)

        # Look for modules from plugin dir specified in the config or on the
        # command line
        distributions, errors = ws.find_plugins(
                                        pkg_resources.Environment(plugins))
        for dist in distributions:
            self.log.debug('Found plugin %s at %s', dist, dist.location)
            ws.add(dist)

        for entry in ws.iter_entry_points(entry_point):
            entry_data = {
                'entry' : entry,
                'loaded' : False,
                'activated' : False,
                'auto_enable' : False,
                }
            self.plugin_data.setdefault(entry.name, entry_data)

        for entry_name, data in self.plugin_data.iteritems():
            if data['auto_enable'] or self.is_enabled(entry_name):
                try:
                    self.log.debug('Loading %s from %s', data['entry'].name,
                                  data['entry'].dist)
                    # We need to make sure the distribution is on the path
                    # before we can load it.
                    data['entry'].dist.activate()
                    data['entry'].load(require=True)
                    data['loaded'] = True
                except (ImportError, DistributionNotFound, VersionConflict,
                        UnknownExtra), e:
                    # Print the last traceback to the debug buffer
                    _log_error(data['entry'], e)
            continue


        for dist, e in errors.iteritems():
            _log_error(dist, e)


    #noinspection PyBroadException
    def __call__(self, cmd, *args, **kwargs):
        """ Invoke a command """
        try:
            for command in self.commands:
                if command.match(cmd):
                    command.run(cmd, *args, **kwargs)
                    break
                continue
            else:
                print("Could not find implementation for %s" % str(cmd))
        except:
            print("Error when calling %s.  See the log for details" % str(cmd))
            self.log.error("Error calling %s" % str(cmd), exc_info=True)

    def _add_namespace_console_object(self, parts, value):
        """ Return the namesapce object with the value attached.

        Handles sub-namespaces also
        """

        key = parts[-1]
        namespaces = parts[:-1]
        global_ns = self.parent_locals.get(namespaces[0], DustbowlObj())
        ns_obj = global_ns
        cur_ns = [namespaces[0]]
        for ns in namespaces[1:]:
            cur_ns.append(ns)
            if not hasattr(ns_obj, ns):
                setattr(ns_obj, ns, DustbowlObj())
            ns_obj = getattr(ns_obj, ns)
            if not isinstance(ns_obj, DustbowlObj):
                raise ConsoleObjectError('.'.join(parts), True, cur_ns)
        if not hasattr(ns_obj, key):
            setattr(ns_obj, key, value)
        else:
            raise ConsoleObjectError('.'.join(parts))
        self.parent_locals[namespaces[0]] = global_ns


    def _add_global_console_object(self, key, value):
        """ Adds a console object without considering namespaces """
        if key in self.parent_locals:
            raise ConsoleObjectError(key)
        self.parent_locals[key] = value


    def add_console_object(self, key, value, provider=None):
        """ Add the value to the console context with the given key """
        if provider is None:
            caller_frame = inspect.stack()[1][0]
            caller_class = ''
            if 'self' in caller_frame.f_locals:
                caller_class = caller_frame.f_locals['self'].__class__.__name__
            provider = "%s%s" % (caller_class and (caller_class + '.') or '',
                                 caller_frame.f_code.co_name)

        parts = key.split('.')
        is_ns = len(parts) > 1
        try:
            if not is_ns:
                self._add_global_console_object(key, value)
            else:
                self._add_namespace_console_object(parts, value)
            self.log.debug("%s added '%s' to the console" %
                           (provider, '.'.join(parts) +
                           (callable(value) and '()' or '')))
        except ConsoleObjectError, e:
            self.log.error("%s  %s must provide a different key"
                           % (e.msg, provider))
            return


    def add_env_object(self, key, value, provider=None):
        """ Add the value to the environment as the given attribute """
        if provider is None:
            caller_frame = inspect.stack()[1][0]
            caller_class = ''
            if 'self' in caller_frame.f_locals:
                caller_class = caller_frame.f_locals['self'].__class__.__name__ 
            provider = "%s%s" % (caller_class and (caller_class + '.') or '',
                                 caller_frame.f_code.co_name)

        attr = getattr(self, key, None)
        if attr:
            self.log.error("The attribute/method >>%s<< already exists in the "
                           "environment.  %s must provide a different "
                           "key" % (str(key), provider))
        else:
            setattr(self, key, value)
            self.log.debug("%s added '%s' to the environemnt" %
                           (provider,
                            str(key) + (callable(value) and '()' or '')))
