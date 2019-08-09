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
Stack and Traceback Inspection Instrumentation
==============================================
"""

import inspect


def format_frame(frame):
    name = []
    module = inspect.getmodule(frame)
    if module:
        name.append(module.__name__)
    # detect classname
    if 'self' in frame.f_locals:
        name.append(frame.f_locals['self'].__class__.__name__)
    codename = frame.f_code.co_name
    if codename != '<module>':
        name.append(codename)
    return '.'.join(name)


def get_caller(skip=1, get_stack=False):
    # Based on http://stackoverflow.com/a/9812105
    stack = inspect.stack()
    done = False
    parentframe = None
    ancestors = []
    while not done:
        start = 1 + skip
        if len(stack) < start + 1:
            return ''
        parentframe = stack[start][0]
        ancestors = stack[start+1:]
        for ancestor in ancestors:
            code_name = ancestor[0].f_code.co_name
            if code_name in ['__enter__', 'inner', '__exit__']:
                ancestors.remove(ancestor)
        code_name = parentframe.f_code.co_name
        if code_name in ['__enter__', 'inner', '__exit__']:
            skip += 1
        else:
            done = True

    if get_stack is False:
        return format_frame(parentframe)
    else:
        return format_frame(parentframe), ancestors
