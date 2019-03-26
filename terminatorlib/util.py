#!/usr/bin/env python3
#    Terminator.util - misc utility functions
#    Copyright (C) 2006-2010  cmsj@tenshu.net
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, version 2 only.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA
"""Terminator.util - misc utility functions"""

import os
import sys
import pwd
import uuid
import inspect
import subprocess

from loguru import logger

import cairo

try:
    import gi
    gi.require_version('Gtk', '3.0')
    from gi.repository import Gtk, Gdk
except ImportError:
    print('You need Gtk 3.0+ to run Remotinator.')
    sys.exit(1)

# set this to true to enable debugging output
DEBUG = os.environ.get('TERMINATOR_DEBUG', 'no') == 'yes'
# set this to true to additionally list filenames in debugging
DEBUGFILES = False
# list of classes to show debugging for. empty list means show all classes
DEBUGCLASSES = []
# list of methods to show debugging for. empty list means show all methods
DEBUGMETHODS = []

def dbg(log=""):
    logger.debug(log)

def err(log = ""):
    logger.error(log)

def gerr(message = None):
    """Display a graphical error. This should only be used for serious
    errors as it will halt execution"""

    dialog = Gtk.MessageDialog(None, Gtk.DialogFlags.MODAL,
            Gtk.MessageType.ERROR, Gtk.ButtonsType.OK, message)
    dialog.run()
    dialog.destroy()


def has_ancestor(widget, wtype):
    """Walk up the family tree of widget to see if any ancestors are of type"""
    while widget:
        widget = widget.get_parent()
        if isinstance(widget, wtype):
            return True
    return False


def manual_lookup():
    '''Choose the manual to open based on LANGUAGE'''
    return 'http://terminator-gtk3.readthedocs.io/en/latest/'


def path_lookup(command):
    '''Find a command in our path'''
    if os.path.isabs(command):
        return command if os.path.isfile(command) else None

    if command.startswith('./') and os.path.isfile(command):
        dbg('path_lookup: Relative filename %s found in cwd' % command)
        return command

    paths = os.environ.get('PATH', '/usr/local/bin:/usr/bin:/bin').split(':')
    dbg('path_lookup: Using %d paths: %s' % (len(paths), paths))

    for path in paths:
        target = os.path.join(path, command)
        if os.path.isfile(target):
            dbg('path_lookup: found %s' % target)
            return target

    dbg('path_lookup: Unable to locate %s' % command)


def shell_lookup():
    """Find an appropriate shell for the user"""
    shells = ['bash', 'zsh', 'tcsh', 'ksh', 'csh', 'sh']
    try:
        usershell = pwd.getpwuid(os.getuid())[6]
        shells = [usershell] + shells
    except KeyError:
        err('unable to find user shell %s' % usershell)
        pass

    for shell in shells:
        if os.path.isfile(shell):
            return shell
        rshell = path_lookup(shell)
        if rshell:
            dbg('shell_lookup: Found %s at %s' % (shell, rshell))
            return rshell
    dbg('shell_lookup: Unable to locate a shell')


def widget_pixbuf(widget, maxsize=None):
    """Generate a pixbuf of a widget"""
    # FIXME: Can this be changed from using "import cairo" to "from gi.repository import cairo"?
    window = widget.get_window()
    width, height = window.get_width(), window.get_height()

    longest = max(width, height)

    if maxsize is not None:
        factor = float(maxsize) / float(longest)

    if not maxsize or (width * factor) > width or (height * factor) > height:
        factor = 1

    preview_width, preview_height = int(width * factor), int(height * factor)

    preview_surface = Gdk.Window.create_similar_surface(window,
        cairo.CONTENT_COLOR, preview_width, preview_height)

    cairo_context = cairo.Context(preview_surface)
    cairo_context.scale(factor, factor)
    Gdk.cairo_set_source_window(cairo_context, window, 0, 0)
    cairo_context.paint()

    scaledpixbuf = Gdk.pixbuf_get_from_surface(preview_surface, 0, 0, preview_width, preview_height);
    return(scaledpixbuf)


def get_config_dir():
    """Expand all the messy nonsense for finding where ~/.config/terminator really is"""
    configdir = os.environ.get('XDG_CONFIG_HOME') or os.path.join(os.path.expanduser('~'), '.config')
    dbg('Found config dir: %s' % configdir)
    return os.path.join(configdir, 'terminator')


def dict_diff(reference, working):
    """Examine the values in the supplied working set and return a new dict
    that only contains those values which are different from those in the
    reference dictionary
    >>> a = {'foo': 'bar', 'baz': 'bjonk'}
    >>> b = {'foo': 'far', 'baz': 'bjonk'}
    >>> dict_diff(a, b)
    {'foo': 'far'}
    """

    result = {}

    for key in reference:
        if reference[key] != working[key]:
            result[key] = working[key]

    return result

# Helper functions for directional navigation
def get_edge(allocation, direction):
    """Return the edge of the supplied allocation that we will care about for directional navigation"""
    if direction == 'left':
        edge = allocation.x
        p1, p2 = allocation.y, allocation.y + allocation.height
    elif direction == 'up':
        edge = allocation.y
        p1, p2 = allocation.x, allocation.x + allocation.width
    elif direction == 'right':
        edge = allocation.x + allocation.width
        p1, p2 = allocation.y, allocation.y + allocation.height
    elif direction == 'down':
        edge = allocation.y + allocation.height
        p1, p2 = allocation.x, allocation.x + allocation.width
    else:
        raise ValueError('unknown direction %s' % direction)
    return (edge, p1, p2)


def get_nav_possible(edge, allocation, direction, p1, p2):
    """Check if the supplied allocation is in the right direction of the
    supplied edge"""
    x1, x2 = allocation.x, allocation.x + allocation.width
    y1, y2 = allocation.y, allocation.y + allocation.height
    if direction == 'left':
        return(x2 <= edge and y1 <= p2 and y2 >= p1)
    elif direction == 'right':
        return(x1 >= edge and y1 <= p2 and y2 >= p1)
    elif direction == 'up':
        return(y2 <= edge and x1 <= p2 and x2 >= p1)
    elif direction == 'down':
        return(y1 >= edge and x1 <= p2 and x2 >= p1)
    else:
        raise ValueError('Unknown direction: %s' % direction)


def get_nav_offset(edge, allocation, direction):
    """Work out how far edge is from a particular point on the allocation
    rectangle, in the given direction"""
    if direction == 'left':
        return(edge - (allocation.x + allocation.width))
    elif direction == 'right':
        return(allocation.x - edge)
    elif direction == 'up':
        return(edge - (allocation.y + allocation.height))
    elif direction == 'down':
        return(allocation.y - edge)
    else:
        raise ValueError('Unknown direction: %s' % direction)

def get_nav_tiebreak(direction, cursor_x, cursor_y, rect):
    """We have multiple candidate terminals. Pick the closest by cursor
    position"""
    if direction in ['left', 'right']:
        return(cursor_y >= rect.y and cursor_y <= (rect.y + rect.height))
    elif direction in ['up', 'down']:
        return(cursor_x >= rect.x and cursor_x <= (rect.x + rect.width))
    else:
        raise ValueError('Unknown direction: %s' % direction)

def enumerate_descendants(parent):
    """Walk all our children and build up a list of containers and
    terminals"""
    # FIXME: Does having to import this here mean we should move this function
    # back to Container?
    from .factory import Factory

    containerstmp = []
    containers = []
    terminals = []
    maker = Factory()

    if parent is None:
        err('no parent widget specified')
        return

    for descendant in parent.get_children():
        if maker.isinstance(descendant, 'Container'):
            containerstmp.append(descendant)
        elif maker.isinstance(descendant, 'Terminal'):
            terminals.append(descendant)

        while containerstmp:
            child = containerstmp.pop(0)
            for descendant in child.get_children():
                if maker.isinstance(descendant, 'Container'):
                    containerstmp.append(descendant)
                elif maker.isinstance(descendant, 'Terminal'):
                    terminals.append(descendant)
            containers.append(child)

    dbg('%d containers and %d terminals fall beneath %s' % (len(containers), len(terminals), parent))
    return(containers, terminals)


def make_uuid(str_uuid=None):
    """Generate a UUID for an object"""
    return uuid.UUID(str_uuid) if str_uuid else uuid.uuid4()


def inject_uuid(target):
    """Inject a UUID into an existing object"""
    if getattr(target, "uuid", None):
        dbg("Object already has a UUID: %s" % target)
    else:
        target.uuid = make_uuid()
        dbg("Injecting UUID %s into: %s" % (target.uuid, target))


def spawn_new_terminator(cwd, args):
    """Start a new terminator instance with the given arguments"""
    cmd = sys.argv[0]

    if not os.path.isabs(cmd):
        # Command is not an absolute path. Figure out where we are
        cmd = os.path.join(cwd, sys.argv[0])
        if not os.path.isfile(cmd):
            # we weren't started as ./terminator in a path. Give up
            err('Unable to locate Terminator')
            return False
    dbg("Spawning: %s" % cmd)
    subprocess.Popen([cmd]+args)


def display_manager():
    """Try to detect which display manager we run under"""
    return 'WAYLAND' if os.environ.get('WAYLAND_DISPLAY') else 'X11'
