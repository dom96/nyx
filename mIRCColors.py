#!/usr/bin/env python
"""
IRCLibrary - Library for the IRC protocol
Copyright (C) 2009 Mad Dog Software 
http://maddogsoftware.co.uk - morfeusz8@yahoo.co.uk

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>
"""
import gtk
import pygtk

mIRCColors=dict()
mIRCColors[0]=gtk.gdk.Color(red=204 * 257, green=204 * 257, blue=204 * 257, pixel=0)
mIRCColors[1]=gtk.gdk.Color(red=0, green=0, blue=0, pixel=0)
mIRCColors[2]=gtk.gdk.Color(red=54 * 257, green=54 * 257, blue=178 * 257, pixel=0)
mIRCColors[3]=gtk.gdk.Color(red=42 * 257, green=140 * 257, blue=42 * 257, pixel=0)
mIRCColors[4]=gtk.gdk.Color(red=195 * 257, green=59 * 257, blue=59 * 257, pixel=0)
mIRCColors[5]=gtk.gdk.Color(red=199 * 257, green=50 * 257, blue=50 * 257, pixel=0)
mIRCColors[6]=gtk.gdk.Color(red=128 * 257, green=38 * 257, blue=127 * 257, pixel=0)
mIRCColors[7]=gtk.gdk.Color(red=102 * 257, green=54 * 257, blue=31 * 257, pixel=0)
mIRCColors[8]=gtk.gdk.Color(red=217 * 257, green=166 * 257, blue=65 * 257, pixel=0)
mIRCColors[9]=gtk.gdk.Color(red=61 * 257, green=204 * 257, blue=61 * 257, pixel=0)
mIRCColors[10]=gtk.gdk.Color(red=26 * 257, green=85 * 257, blue=85 * 257, pixel=0)
mIRCColors[11]=gtk.gdk.Color(red=47 * 257, green=140 * 257, blue=116 * 257, pixel=0)
mIRCColors[12]=gtk.gdk.Color(red=69 * 257, green=69 * 257, blue=230 * 257, pixel=0)
mIRCColors[13]=gtk.gdk.Color(red=176 * 257, green=55 * 257, blue=176 * 257, pixel=0)
mIRCColors[14]=gtk.gdk.Color(red=76 * 257, green=76 * 257, blue=76 * 257, pixel=0)
mIRCColors[15]=gtk.gdk.Color(red=149 * 257, green=149 * 257, blue=149 * 257, pixel=0)

def canonicalColor(s, bg=False, shift=0):
    """Assigns an (fg, bg) canonical color pair to a string based on its hash
    value.  This means it might change between Python versions.  This pair can
    be used as a *parameter to mircColor.  The shift parameter is how much to
    right-shift the hash value initially.
    """
    h = hash(s) >> shift
    fg = h % 14 + 2 # The + 2 is to rule out black and white.
    if bg:
        bg = (h >> 4) & 3 # The 5th, 6th, and 7th least significant bits.
        if fg < 8:
            bg += 8
        else:
            bg += 2
        return (fg, bg)
    else:
        return (fg, None)
