# -*- Mode: python; tab-width: 4; indent-tabs-mode:nil; coding:utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4
#
# MDAnalysis --- https://www.mdanalysis.org
# Copyright (c) 2006-2017 The MDAnalysis Development Team and contributors
# (see the file AUTHORS for the full list of names)
#
# Released under the GNU Public Licence, v2 or any higher version
#
# Please cite your use of MDAnalysis in published work:
#
# R. J. Gowers, M. Linke, J. Barnoud, T. J. E. Reddy, M. N. Melo, S. L. Seyler,
# D. L. Dotson, J. Domanski, S. Buchoux, I. M. Kenney, and O. Beckstein.
# MDAnalysis: A Python package for the rapid analysis of molecular dynamics
# simulations. In S. Benthall and S. Rostrup editors, Proceedings of the 15th
# Python in Science Conference, pages 102-109, Austin, TX, 2016. SciPy.
# doi: 10.25080/majora-629e541a-00e
#
# N. Michaud-Agrawal, E. J. Denning, T. B. Woolf, and O. Beckstein.
# MDAnalysis: A Toolkit for the Analysis of Molecular Dynamics Simulations.
# J. Comput. Chem. 32 (2011), 2319--2327, doi:10.1002/jcc.21787
#


"""Setting up logging --- :mod:`MDAnalysis.lib.log`
====================================================

Configure logging for MDAnalysis. Import this module if logging is
desired in application code.

Logging to a file and the console is set up by default as described
under `logging to multiple destinations`_.

The top level logger of the library is named *MDAnalysis* by
convention; a simple logger that writes to the console and logfile can
be created with the :func:`create` function. This only has to be done
*once*. For convenience, the default MDAnalysis logger can be created
with :func:`MDAnalysis.start_logging`::

 import MDAnalysis
 MDAnalysis.start_logging()

Once this has been done, MDAnalysis will write messages to the logfile
(named `MDAnalysis.log` by default but this can be changed with the
optional argument to :func:`~MDAnalysis.start_logging`).

Any code can log to the MDAnalysis logger by using ::

 import logging
 logger = logging.getLogger('MDAnalysis.MODULENAME')

 # use the logger, for example at info level:
 logger.info("Starting task ...")

The important point is that the name of the logger begins with
"MDAnalysis.".

.. _logging to multiple destinations:
   http://docs.python.org/library/logging.html?#logging-to-multiple-destinations

Note
----
The :mod:`logging` module in the standard library contains in depth
documentation about using logging.


Convenience functions
---------------------

Two convenience functions at the top level make it easy to start and
stop the default *MDAnalysis* logger.

.. autofunction:: MDAnalysis.start_logging
.. autofunction:: MDAnalysis.stop_logging


Other functions and classes for logging purposes
------------------------------------------------


.. versionchanged:: 2.0.0
   Deprecated :class:`MDAnalysis.lib.log.ProgressMeter` has now been removed.

.. autogenerated, see Online Docs

"""
import sys
import logging
import re

from tqdm.auto import tqdm

from .. import version


def start_logging(logfile="MDAnalysis.log", version=version.__version__):
    """Start logging of messages to file and console.

    The default logfile is named `MDAnalysis.log` and messages are
    logged with the tag *MDAnalysis*.
    """
    create("MDAnalysis", logfile=logfile)
    logging.getLogger("MDAnalysis").info(
        "MDAnalysis %s STARTED logging to %r", version, logfile)


def stop_logging():
    """Stop logging to logfile and console."""
    logger = logging.getLogger("MDAnalysis")
    logger.info("MDAnalysis STOPPED logging")
    clear_handlers(logger)  # this _should_ do the job...


def create(logger_name="MDAnalysis", logfile="MDAnalysis.log"):
    """Create a top level logger.

    - The file logger logs everything (including DEBUG).
    - The console logger only logs INFO and above.

    Logging to a file and the console as described under `logging to
    multiple destinations`_.

    The top level logger of MDAnalysis is named *MDAnalysis*.  Note
    that we are configuring this logger with console output. If a root
    logger also does this then we will get two output lines to the
    console.

    .. _logging to multiple destinations:
       http://docs.python.org/library/logging.html?#logging-to-multiple-destinations
    """

    logger = logging.getLogger(logger_name)

    logger.setLevel(logging.DEBUG)

    # handler that writes to logfile
    logfile_handler = logging.FileHandler(logfile)
    logfile_formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    logfile_handler.setFormatter(logfile_formatter)
    logger.addHandler(logfile_handler)

    # define a Handler which writes INFO messages or higher to the sys.stderr
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    # set a format which is simpler for console use
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger


def clear_handlers(logger):
    """clean out handlers in the library top level logger

    (only important for reload/debug cycles...)

    """
    for h in logger.handlers:
        logger.removeHandler(h)


class NullHandler(logging.Handler):
    """Silent Handler.

    Useful as a default::

      h = NullHandler()
      logging.getLogger("MDAnalysis").addHandler(h)
      del h

    see the advice on logging and libraries in
    http://docs.python.org/library/logging.html?#configuring-logging-for-a-library
    """
    def emit(self, record):
        pass


def echo(s='', replace=False, newline=True):
    r"""Simple string output that immediately prints to the console.

    The string `s` is modified according to the keyword arguments and then
    printed to :const:`sys.stderr`, which is immediately flushed.

    Parameters
    ----------
    s : str
        The string to output.
    replace : bool
        If ``True``, the string will be printed on top of the current line. In
        practice, ``\r`` is added at the beginning of the string.
    newline : bool
        If ``True``, a newline is added at the end of the string.

    """
    if replace:
        s = '\r' + s
    if newline:
        end='\n'
    else:
        end=''
    print(s, file=sys.stderr, end=end)
    sys.stderr.flush()


def _new_format(template, variables):
    """Format a string that follows the {}-based syntax.
    """
    return template.format(**variables)


def _legacy_format(template, variables):
    """Format a string that follows the %-based syntax.
    """
    return template % variables


def _guess_string_format(template):
    """Guess if the template follow {}-based or %-based syntax.
    """
    match = re.search(r'%\((step|numsteps|percentage)\)', template)
    if match is None:
        return _new_format
    else:
        return _legacy_format


class ProgressBar(tqdm):
    def __init__(self, *args, **kwargs):
        verbose = kwargs.pop('verbose', True)
        # disable: Whether to disable the entire progressbar wrapper [default: False].
        # If set to None, disable on non-TTY.
        # disable should be the opposite of verbose unless it's None
        disable = verbose if verbose is None else not verbose
        # disable should take precedence over verbose if both are set
        kwargs['disable'] = kwargs.pop('disable', disable)
        super(ProgressBar, self).__init__(*args, **kwargs)
