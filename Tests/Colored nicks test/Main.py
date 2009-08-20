#!/usr/bin/env python
import random
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




print canonicalColor("dom95asdasdsadsadsadsadsadsad65")
