# -*- coding: utf-8 -*-
#
# Modifcations Copyright (C) 2009 John Hampton <pacopablo@pacopablo.com>
#
# Original code from Trac trunk r8199
# http://svn.edgewall.org/reops/trac/trunk
#
# Moved from util/text.py
#
# Copyright (C) 2003-2009 Edgewall Software
# Copyright (C) 2003-2004 Jonas Borgström <jonas@edgewall.com>
# Copyright (C) 2006 Matthew Good <trac@matt-good.net>
# Copyright (C) 2005-2006 Christian Boos <cboos@neuf.fr>
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
#         Matthew Good <trac@matt-good.net>
#         Christian Boos <cboos@neuf.fr>

# Standard Library Imports
import locale
import traceback
from StringIO import StringIO

# Third Party Imports

# Local Imports

__all__ = [
    'to_unicode',
    'format_exception',
    'get_last_traceback',
]

def to_unicode(text, charset=None):
    """Convert a `str` object to an `unicode` object.

    If `charset` is given, we simply assume that encoding for the text,
    but we'll use the "replace" mode so that the decoding will always
    succeed.
    If `charset` is ''not'' specified, we'll make some guesses, first
    trying the UTF-8 encoding, then trying the locale preferred encoding,
    in "replace" mode. This differs from the `unicode` builtin, which
    by default uses the locale preferred encoding, in 'strict' mode,
    and is therefore prompt to raise `UnicodeDecodeError`s.

    Because of the "replace" mode, the original content might be altered.
    If this is not what is wanted, one could map the original byte content
    by using an encoding which maps each byte of the input to an unicode
    character, e.g. by doing `unicode(text, 'iso-8859-1')`.
    """
    if charset:
        return unicode(text, charset, 'replace')
    else:
        try:
            return unicode(text, 'utf-8')
        except UnicodeError:
            return unicode(text, locale.getpreferredencoding(), 'replace')

def format_exception(e, traceback=""):
    message = '%s: %s' % (e.__class__.__name__, str(e))
    if traceback:
        traceback_only = get_last_traceback().split('\n')[:-2]
        message = '\n%s\n%s' % ('\n'.join(traceback_only), message)
    return message

def get_last_traceback():
    tb = StringIO()
    traceback.print_exc(file=tb)
    return tb.getvalue()

