#!/usr/bin/env python3
# Terminator by Chris Jones <cmsj@tenshu.net>
# GPL v2 only
"""layoutlauncher.py - class for the Layout Launcher window"""

import os

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from gi.repository import GObject

from .util import dbg, err, spawn_new_terminator
from . import config
from .translation import _
from .terminator import Terminator


class LayoutLauncher:

    def __init__ (self):
        self.terminator = Terminator()
        self.terminator.register_launcher_window(self)

        self.config = config.Config()
        self.config.base.reload()

        root = os.path.dirname(config.__file__)
        glade = os.path.join(root, 'layoutlauncher.glade')

        self.builder = Gtk.Builder()
        self.builder.add_from_file(glade)
        self.window = self.builder.get_object('layoutlauncherwin')

        icon_theme = Gtk.IconTheme.get_default()
        if icon_theme.lookup_icon('terminator-layout', 48, 0):
            self.window.set_icon_name('terminator-layout')
        else:
            dbg('Unable to load Terminator layout launcher icon')
            icon = self.window.render_icon(Gtk.STOCK_DIALOG_INFO, Gtk.IconSize.BUTTON)
            self.window.set_icon(icon)

        self.builder.connect_signals(self)
        self.window.connect('destroy', self.on_destroy_event)
        self.window.show_all()
        self.layouttreeview = self.builder.get_object('layoutlist')
        self.layouttreestore = self.builder.get_object('layoutstore')
        self.update_layouts()

    def on_destroy_event(self, widget, data=None):
        """Handle window destruction"""
        dbg('destroying self')
        self.terminator.deregister_launcher_window(self)
        self.window.destroy()
        del(self.window)

    def update_layouts(self):
        """Update the contents of the layout"""
        self.layouttreestore.clear()
        layouts = self.config.list_layouts()
        for layout in sorted(layouts, key=str.lower):
            if layout == "default":
                self.layouttreestore.prepend([layout])
            else:
                self.layouttreestore.append([layout])

    def on_launchbutton_clicked(self, widget):
        """Handle button click"""
        self.launch_layout()

    def on_row_activated(self, widget,  path,  view_column):
        """Handle item double-click and return"""
        self.launch_layout()

    def launch_layout(self):
        """Launch the selected layout as new instance"""
        dbg('We have takeoff!')
        selection = self.layouttreeview.get_selection()
        (listmodel, rowiter) = selection.get_selected()
        if not rowiter:
            # Something is wrong, just jump to the first item in the list
            selection.select_iter(self.layouttreestore.get_iter_first())
            (listmodel, rowiter) = selection.get_selected()
        layout = listmodel.get_value(rowiter, 0)
        dbg('Clicked for %s' % layout)
        cwd = self.terminator.origcwd or os.getcwd()
        spawn_new_terminator(cwd, ['-u', '-l', layout])


if __name__ == '__main__':
    import util
    util.DEBUG = True
    import terminal
    LAYOUTLAUNCHER = LayoutLauncher()

    Gtk.main()
