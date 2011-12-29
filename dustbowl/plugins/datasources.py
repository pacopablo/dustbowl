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
import re

# Third Party Imports
from sqlalchemy import create_engine, orm
from sqlalchemy.orm import sessionmaker, scoped_session

# Local Imports
from dustbowl.api import Component, implements, IShellConsoleObjectProvider
from dustbowl.api import ExtensionPoint, Interface
from dustbowl.env import IEnvObjectProvider

__all__ = [
    'IDataSourceProvider',
    'DataSourceManager',
    'ConfigDataSource',
]

KNOWN_OPTIONS = ['encoding', 'convert_unicode']
OPTION_KEYS_RE = r'sqlalchemy\.(?P<source>[\w\d]+?)\.(?P<option>[\w\d]+)'
URL_RE = r'sqlalchemy\.(?P<source>[\w\d]+?)\.url'
url = re.compile(URL_RE)
sqloptions = re.compile(OPTION_KEYS_RE)


class IDataSourceProvider(Interface):
    def get_data_source(self):
        """ Yield (key, source) tuples. """


class DataSourceManager(Component):
    """ Provide access to datasources """

    data_source_providers = ExtensionPoint(IDataSourceProvider)
    implements(IShellConsoleObjectProvider, IEnvObjectProvider)

    def get_datasource(self, datasource, part='scoped_session', **kwargs):
        try:
            sources = self.datasources
        except AttributeError:
            self.datasources = {}
            for provider in self.data_source_providers:
                for k, engine in provider.get_data_source():
                    sm = sessionmaker(bind=engine, **kwargs)
                    ss = scoped_session(sm)
                    self.datasources[k] = {'engine': engine,
                                           'sessionmaker': sm,
                                           'scoped_session': ss,}
                    continue
                continue
            sources = self.datasources
        try:
            ret = sources[datasource][part]
        except KeyError:
            self.log.warning('The datasource >> %s << was not found' %
                             str(datasource))
            ret = None
        return ret

    def get_console_objects(self):
        yield ('get_datasource', self.get_datasource)

    def get_env_objects(self):
        yield ('get_datasource', self.get_datasource)



class ConfigDataSource(Component):
    """ Load SQLAlchemy Data Sources from the configuration file """

    implements(IDataSourceProvider)

    def get_data_source(self):
        global url

        sections = self.config.sections()
        source_info = {}
        for s in sections:
            for k, v in self.config.options(s):
                g = url.match(k)
                if g:
                    key = g.group('source')
                    args_dict = self._parse_engine_args(key, s)
                    source = create_engine(v, **args_dict)
                    source_info[key] = source
                continue
            continue

        for k, s in source_info.items():
            yield (k, s)

    def _parse_engine_args(self, source, section):
        """ Create a dictionary of keyword arguments to be passed to the
        create_engine call.

        The options are in the format: sqlalchemy.<key>.<param> = <value>

        Currently, the availalbe options are:
         * encoding
         * convert_unicode
        """
        global sqloptions, KNOWN_OPTIONS

        engine_args = {}
        for k, v in self.config.options(section):
            g = sqloptions.match(k)
            if g and (source == g.group('source')):
                option = g.group('option')
                if option in KNOWN_OPTIONS:
                    engine_args[option] = getattr(self, '_get_' + option.upper(),
                                              lambda x, y: None)(section, k)
            continue
        return engine_args

    def _get_ENCODING(self, section, option):
        return self.config.get(section, option, None)

    def _get_CONVERT_UNICODE(self, section, option):
        return self.config.getbool(section, option, False)

