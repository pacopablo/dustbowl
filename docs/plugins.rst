Modules
========


Dustbowl can be extended via plugin modules.  Modules are simply python
packages that specify the ``[dustbowl.modules]`` entry point.  Dustbowl relies
on modules for most of its work.  Without modules, dustbowl is really nothing
more than a standard Python REPL.

Dustbowl includes two plugins: ``config`` and ``logcmd``.  The ``config``
plugin provides access to the config object in the console.  ``logcmd``
provides commands for viewing and managing the console log.

When Dustbowl starts, it will search the ``PYTHONPATH`` for existing modules.
Any modules found on the ``PYTHONPATH`` will be loaded, but disabled by
default.  If a pluging modules directory is specified on the command line via
``-p``, then it will be searched for dustbowl modules.  Any modules found in
this directory will be loaded and enabled by default.  Additionally, the
modules provided by Dustbowl itself, ``config`` and ``logcmd`` are loaded and
enabled at startup.

Once the Dustbowl console has been started, one can enable modules via the
``.module.enable`` command

