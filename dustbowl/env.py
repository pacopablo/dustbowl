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
#import setuptools
import pkg_resources
import os.path
import inspect

# Third Party imports

# Local imports
from api import Component, ComponentManager, Interface, IShellCommandProvider
from api import ExtensionPoint, IShellConsoleObjectProvider, implements, DustbowlObj
from error import ConsoleObjectError
from config import Configuration
from log import NullLogger
from loader import load_plugins

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

    def __init__(self, config=None, entry_point=None, plugins=[],
                logger=None, locals={}):
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
        self._plugins_loaded = list()
        self.load_plugins(plugins, entry_point=entry_point)
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

        rules = [(name.lower(), value.lower() in ('enabled', 'on'))
                 for name, value in self.config.options('components')]
        rules.sort(lambda a, b: -cmp(len(a[0]), len(b[0])))

        for pattern, enabled in rules:
            if component_name == pattern or pattern.endswith('*') \
                    and component_name.startswith(pattern[:-1]):
                return enabled
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


    def load_plugins(self, plugins=[], entry_point='dustbowl.modules'):
        """ Load plugins """
        disabled = list(sys.path)
        enabled = [os.path.dirname(pkg_resources.resource_filename(__name__, ''))]
        for path, auto_enable in plugins:
            if auto_enable:
                enabled.append(path)
            else:
                disabled.append(path)
        inherited_plugins = self.config.get('inherit', 'plugins_dir', )
        if inherited_plugins:
            enabled.append(inherited_plugins)
        load_plugins(self, entry_point, enabled, True)
        load_plugins(self, entry_point, disabled, False)


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
