#!/usr/bin/env python3
# Terminator by Chris Jones <cmsj@tenshu.net>
# GPL v2 only
"""terminalshot.py - Terminator Plugin to take 'screenshots' of individual
terminals"""

import os
from gi.repository import Gtk
from gi.repository import GdkPixbuf
import terminatorlib.plugin as plugin
from terminatorlib.translation import _
from terminatorlib.util import widget_pixbuf

# Every plugin you want Terminator to load *must* be listed in 'AVAILABLE'
AVAILABLE = ['OpenFolder']

class OpenFolder(plugin.MenuItem):

    def callback(self, menuitems, menu, terminal):
        """Add our menu items to the menu"""
        item = Gtk.MenuItem.new_with_mnemonic(_('Open Folder'))
        item.connect("activate", self.open_folder, terminal)
        menuitems.append(item)

    def open_folder(self, _widget, terminal):
        os.system('nautilus .')
