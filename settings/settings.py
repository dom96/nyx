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
from IRCLibrary import IRC
#This will load the settings from settings.xml
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

def makeBool(txt):
    if txt.lower() == "false":
        return False
    elif txt.lower()== "true":
        return True
    else:
        return False

def loadSettings():
    loadedSettings=settings()
    import xml.dom.minidom, os.path, sys
    #Parse the settings.xml file...os.path.abspath(os.path.dirname(sys.argv[0])) get's the scripts directory
    xmlDoc=xml.dom.minidom.parse(os.path.abspath(os.path.dirname(sys.argv[0])) + "/settings/settings.xml")
    """1.Get the nicks:"""
    #""1a.Get the nicks tag, and use getText() to get the TEXT_NODE of the nicks tag
    nicksTag=xmlDoc.getElementsByTagName("nicks")[0]
    nicksTagText=getText(nicksTag.childNodes)
    #""1b.Split it into space( ) and add it to settings.nicks[]
    for i in nicksTagText.split(" "): loadedSettings.nicks.append(i);
    """2.Get the username"""
    usernameTag=xmlDoc.getElementsByTagName("username")[0]
    usernameTagText=getText(usernameTag.childNodes)
    loadedSettings.username=usernameTagText
    """3.Get the realname"""
    realnameTag=xmlDoc.getElementsByTagName("realname")[0]
    realnameTagText=getText(usernameTag.childNodes)
    loadedSettings.realname=realnameTagText

    """4.Get the chatTextView colors"""
    chatColorsTag=xmlDoc.getElementsByTagName("chatColors")
    for colorTag in chatColorsTag[0].childNodes:
        if colorTag.nodeType == colorTag.ELEMENT_NODE:
            name = getAttribute(colorTag.attributes,"name")
            r = int(getAttribute(colorTag.attributes,"red"))
            g = int(getAttribute(colorTag.attributes,"green"))
            b = int(getAttribute(colorTag.attributes,"blue"))

            sColor = gtk.gdk.Color(red=r * 257,green=g * 257,blue=b * 257,pixel=0)
            setChatColorVar(loadedSettings,name,sColor)

    """5.Get the treeviews Colors"""
    treeColorsTag=xmlDoc.getElementsByTagName("treeviewColors")
    for colorTag in treeColorsTag[0].childNodes:
        if colorTag.nodeType == colorTag.ELEMENT_NODE:
            name = getAttribute(colorTag.attributes,"name")
            r = int(getAttribute(colorTag.attributes,"red"))
            g = int(getAttribute(colorTag.attributes,"green"))
            b = int(getAttribute(colorTag.attributes,"blue"))

            sColor = gtk.gdk.Color(red=r * 257,green=g * 257,blue=b * 257,pixel=0)
            setTreeColorVar(loadedSettings,name,sColor)
    """6.Get the server"""
    serversTag=xmlDoc.getElementsByTagName("servers")[0]
    for serverTag in serversTag.childNodes:
        if serverTag.nodeType == serverTag.ELEMENT_NODE:
            if serverTag.nodeName == "server":
                nServer = sServer()
                nServer.cName = getAttribute(serverTag.attributes,"name") #Name of the server
                nServer.autoconnect = makeBool(getAttribute(serverTag.attributes,"autoconnect")) #Determines whether to connect to this server when Nyx starts
                nServer.addresses = [] #Addresses for this server(If the first server is unavailable, Nyx tries connecting to the enxt one)
                #Get the addresses to connect to.
                for addressTag in serverTag.childNodes:
                    if addressTag.nodeType == addressTag.ELEMENT_NODE:
                        #address()
                        address = sServer()
                        address.cAddress = getText(addressTag.childNodes)
                        address.cPort = int(getAttribute(addressTag.attributes,"port"))
                        address.cSsl = makeBool(getAttribute(addressTag.attributes,"ssl"))
                        nServer.addresses.append(address)
                loadedSettings.servers.append(nServer)
    return loadedSettings

"""Sets the chatTextViewColors in loadedSettings"""
def setChatColorVar(loadedSettings,name,color):
    if name == "server":
        loadedSettings.serverColor = color
    elif name == "motd":
        loadedSettings.motdColor = color
    elif name == "nick":
        loadedSettings.nickColor = color
    elif name == "time":
        loadedSettings.timeColor = color
    elif name == "part":
        loadedSettings.partColor = color
    elif name == "join":
        loadedSettings.joinColor = color
    elif name == "highlight":
        loadedSettings.highlightColor = color
"""Sets the treeviewColors in loadedSettings"""
def setTreeColorVar(loadedSettings,name,color):
    if name == "normal":
        loadedSettings.normalTColor = color
    elif name == "highlight":
        loadedSettings.highlightTColor = color
    elif name == "talk":
        loadedSettings.talkTColor = color
    elif name == "status":
        loadedSettings.statusTColor = color

class sServer:
    cName=""

class settings:
    nicks=[] #Nicks(If one is taken, Nyx will try the next one...etc.)
    username="" #Username - Why am i even saying this it's obvious! heh
    realname="" #realname
    #chatColors
    serverColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    motdColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    nickColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    timeColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    partColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    joinColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    highlightColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    #treeviewColors
    normalTColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    highlightTColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    talkTColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    statusTColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    #List of servers, available for connecting...(class IRCLibrary.IRC())
    servers=[]

import inspect
debugInfo=True
def pDebug(txt):
    if debugInfo:
        func = str(inspect.getframeinfo(inspect.currentframe().f_back).function)
        filename = str(inspect.getframeinfo(inspect.currentframe().f_back).filename);filename = filename.split("/")[len(filename.split("/"))-1]
        print "[\033[1;34m"+str(inspect.currentframe().f_back.f_lineno).rjust(3, '0')+"\033[1;m, " + filename +"(" + func + ")]\n    " + str(txt)
