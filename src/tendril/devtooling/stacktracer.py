# Copyright (C) 2015 Chintalagiri Shashank
#
# This file is part of Tendril.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Stacktracing Instrumentation for Multi-threaded Applications
============================================================

Stack tracer for multi-threaded applications.
http://code.activestate.com/recipes/577334-how-to-debug-deadlocked-multi-threaded-programs/

Usage:

    import stacktracer
    stacktracer.start_trace("trace.html",interval=5,auto=True)
    # Set auto flag to always update file!

    ....
    stacktracer.stop_trace()

"""


import sys
import traceback
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

# Taken from http://bzimmer.ziclix.com/2008/12/17/python-thread-dumps/


def stacktraces():
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# ThreadID: %s" % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))

    return highlight("\n".join(code), PythonLexer(), HtmlFormatter(
      full=False,
      # style="native",
      noclasses=True,
    ))


# This part was made by nagylzs
import os
import time
import threading


class TraceDumper(threading.Thread):
    """Dump stack traces into a given file periodically."""
    def __init__(self, fpath, interval, auto):
        """
        @param fpath: File path to output HTML (stack trace file)
        @param auto: Set flag (True) to update trace continuously.
            Clear flag (False) to update only if file not exists.
            (Then delete the file to force update.)
        @param interval: In seconds: how often to update the trace file.
        """
        assert(interval > 0.1)
        self.auto = auto
        self.interval = interval
        self.fpath = os.path.abspath(fpath)
        self.stop_requested = threading.Event()
        threading.Thread.__init__(self)

    def run(self):
        while not self.stop_requested.isSet():
            time.sleep(self.interval)
            if self.auto or not os.path.isfile(self.fpath):
                self.stacktraces()

    def stop(self):
        self.stop_requested.set()
        self.join()
        try:
            if os.path.isfile(self.fpath):
                os.unlink(self.fpath)
        except:
            pass

    def stacktraces(self):
        with open(self.fpath, "wb+") as fout:
            fout.write(stacktraces())

_tracer = None


def trace_start(fpath, interval=5, auto=True):
    """Start tracing into the given file."""
    global _tracer
    if _tracer is None:
        _tracer = TraceDumper(fpath, interval, auto)
        _tracer.setDaemon(True)
        _tracer.start()
    else:
        raise Exception("Already tracing to %s" % _tracer.fpath)


def trace_stop():
    """Stop tracing."""
    global _tracer
    if _tracer is None:
        raise Exception("Not tracing, cannot stop.")
    else:
        _tracer.stop()
        _tracer = None
