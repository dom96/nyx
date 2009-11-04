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


"""getText, Get's the text of a tag"""
def getText(nodelist):
    txt = ""
    #Loop through the nodeList
    for node in nodelist:
        #If a TEXT_NODE is found add it to txt
        if node.nodeType == node.TEXT_NODE:
            txt = txt + node.data
    #And return it
    return txt
def getAttribute(attrlist, attrName):
    txt = ""
    #Loop through the attributes
    for i in range(0,attrlist.length):
        #If the attributes name == attrName
        if attrlist.item(i).nodeName == attrName:
            txt=attrlist.item(i).nodeValue
    #Then return the attributes value
    return txt
