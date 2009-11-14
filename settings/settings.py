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
#This will load the settings from settings.xml


def makeBool(txt):
    if txt.lower() == "false":
        return False
    elif txt.lower()== "true":
        return True
    else:
        return False

def loadSettings():
    loadedSettings=settings()
    import xml.dom.minidom, os.path, sys, XmlHelper
    #Parse the settings.xml file...os.path.abspath(os.path.dirname(sys.argv[0])) get's the scripts directory
    xmlDoc=xml.dom.minidom.parse(os.path.abspath(os.path.dirname(sys.argv[0])) + "/settings/settings.xml")
    """1.Get the nicks:"""
    #""1a.Get the nicks tag, and use getText() to get the TEXT_NODE of the nicks tag
    nicksTag=xmlDoc.getElementsByTagName("nicks")[0]
    nicksTagText=XmlHelper.getText(nicksTag.childNodes)
    #""1b.Split it into space( ) and add it to settings.nicks[]
    for i in nicksTagText.split(" "): loadedSettings.nicks.append(i);
    """2.Get the username"""
    usernameTag=xmlDoc.getElementsByTagName("username")[0]
    usernameTagText=XmlHelper.getText(usernameTag.childNodes)
    loadedSettings.username=usernameTagText
    """3.Get the realname"""
    realnameTag=xmlDoc.getElementsByTagName("realname")[0]
    realnameTagText=XmlHelper.getText(usernameTag.childNodes)
    loadedSettings.realname=realnameTagText

    """4.Get the chatTextView colors"""
    chatColorsTag=xmlDoc.getElementsByTagName("chatColors")
    for colorTag in chatColorsTag[0].childNodes:
        if colorTag.nodeType == colorTag.ELEMENT_NODE:
            name = XmlHelper.getAttribute(colorTag.attributes,"name")
            r = int(XmlHelper.getAttribute(colorTag.attributes,"red"))
            g = int(XmlHelper.getAttribute(colorTag.attributes,"green"))
            b = int(XmlHelper.getAttribute(colorTag.attributes,"blue"))

            sColor = gtk.gdk.Color(red=r * 257,green=g * 257,blue=b * 257,pixel=0)
            setChatColorVar(loadedSettings,name,sColor)

    """5.Get the treeviews Colors"""
    treeColorsTag=xmlDoc.getElementsByTagName("treeviewColors")
    for colorTag in treeColorsTag[0].childNodes:
        if colorTag.nodeType == colorTag.ELEMENT_NODE:
            name = XmlHelper.getAttribute(colorTag.attributes,"name")
            r = int(XmlHelper.getAttribute(colorTag.attributes,"red"))
            g = int(XmlHelper.getAttribute(colorTag.attributes,"green"))
            b = int(XmlHelper.getAttribute(colorTag.attributes,"blue"))

            sColor = gtk.gdk.Color(red=r * 257,green=g * 257,blue=b * 257,pixel=0)
            setTreeColorVar(loadedSettings,name,sColor)
    """6.Get the server"""
    serversTag=xmlDoc.getElementsByTagName("servers")[0]
    for serverTag in serversTag.childNodes:
        if serverTag.nodeType == serverTag.ELEMENT_NODE:
            if serverTag.nodeName == "server":
                nServer = sServer()
                nServer.cName = XmlHelper.getAttribute(serverTag.attributes,"name") #Name of the server
                nServer.autoconnect = makeBool(XmlHelper.getAttribute(serverTag.attributes,"autoconnect")) #Determines whether to connect to this server when Nyx starts
                nServer.addresses = [] #Addresses for this server(If the first server is unavailable, Nyx tries connecting to the enxt one)
                #Get the addresses to connect to.
                for addressTag in serverTag.childNodes:
                    if addressTag.nodeType == addressTag.ELEMENT_NODE:
                        #address()
                        address = sServer()
                        address.cAddress = XmlHelper.getText(addressTag.childNodes)
                        address.cPort = int(XmlHelper.getAttribute(addressTag.attributes,"port"))
                        address.cSsl = makeBool(XmlHelper.getAttribute(addressTag.attributes,"ssl"))
                        address.cPass = XmlHelper.getAttribute(addressTag.attributes,"pass")
                        nServer.addresses.append(address)
                loadedSettings.servers.append(nServer)
                
    #Get the themePath
    themeTag=xmlDoc.getElementsByTagName("theme")[0]
    loadedSettings.themePath = XmlHelper.getAttribute(themeTag.attributes,"path")
                
                
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
    elif name == "error":
        loadedSettings.errorColor = color

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
    #chatColors - TODO:This is obsolete...
    serverColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    motdColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    nickColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    timeColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    partColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    joinColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    highlightColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    errorColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    #treeviewColors - TODO:This is obsolete
    normalTColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    highlightTColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    talkTColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    statusTColor=gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)
    #List of servers, available for connecting...(class IRCLibrary.IRC())
    servers=[]
    #Theme path
    themePath=""

class theme:
    def __init__(self):
        self.name=""
        self.replaces=[]
        self.styles=[]
        
    """Loads the theme"""
    def loadTheme(self, path):
        loadedTheme = self

        import xml.dom.minidom, os.path, sys, XmlHelper
        xmlDoc=xml.dom.minidom.parse(os.path.abspath(os.path.dirname(sys.argv[0])) + path)
        
        #Get the name of the theme
        nameTag=xmlDoc.getElementsByTagName("name")[0]
        nameTagText=XmlHelper.getText(nameTag.childNodes)
        loadedTheme.name = nameTagText
        
        #Get all the REPLACE Tags
        replaceTags=xmlDoc.getElementsByTagName("replace")
        for replaceTag in replaceTags:
            key = XmlHelper.getAttribute(replaceTag.attributes,"key")
            text = XmlHelper.getAttribute(replaceTag.attributes,"text")
            loadedTheme.replaces.append(dict({"key": self.replaceEscapes(key), "text": self.replaceEscapes(text)}))
            
        #Get the STYLE Tags
        styleTags=xmlDoc.getElementsByTagName("style")
        for styleTag in styleTags:
            name = XmlHelper.getAttribute(styleTag.attributes,"name")
            insert = XmlHelper.getAttribute(styleTag.attributes,"insert")
            ifStatmnt = XmlHelper.getAttribute(styleTag.attributes,"if")
            
            
            loadedTheme.styles.append(dict({'name': self.replaceEscapes(name), "insert": self.replaceEscapes(insert), "if": self.replaceEscapes(ifStatmnt)}))
        return loadedTheme
        
    """This function replaces escapes for example \x03"""
    def replaceEscapes(self, text):
        return text.replace("\\x03","\x03").replace("\\x02","\x02").replace("\\x1f", "\x1f")
        
        
    """
    Parses a style specified('name') and returns the output.
    Used in IRCEvents
    """
    def parseStyle(self, name, nick, host, msgType, channel, msg, server, nickColor="01", nick1="", nickColor1="01"):
        nickColor = str(nickColor)

        for style in self.styles:
            ifStatmnt = self.checkIfStatmnt(style["if"], nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
            if style["name"] == name and ifStatmnt:
                output = style["insert"]
                #Loop through the replaces and replace them in output
                
                output = self.replaceReplaces(output, nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
                    
                #replaceText after replacing 'replaces', so that replaces don't replace
                #stuff in (msg) or (channel)
                output = self.replaceText(output, nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
                return output
                
        return False
        
    """Checks the if statements, returns True if the statement returns True"""
    def checkIfStatmnt(self, ifStatmnt, nick, host, msgType, channel, msg, server, nickColor="01", nick1="", nickColor1="01"):
        import re

        if "==" in ifStatmnt:
            #TODO: think of a way that you can compare text with spaces.... $nM$ == Text With Spaces
            ifStatmnt = ifStatmnt.replace(" ","")
            pos = ifStatmnt.find("==")
            first = ifStatmnt[:pos]  #Before the ==
            second = ifStatmnt[pos+2:]  #After the ==
            
            first = self.replaceReplaces(first, nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
            second = self.replaceReplaces(second, nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
    
            first = self.replaceText(first, nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
            second = self.replaceText(second, nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
        
            #Check if this statement is true.
            return first == second
        
        elif "!=" in ifStatmnt:
            #TODO: think of a way that you can compare text with spaces.... $nM$ == Text With Spaces
            ifStatmnt = ifStatmnt.replace(" ","")
            
            pos = ifStatmnt.find("!=")
            first = ifStatmnt[:pos]  #Before the !=
            second = ifStatmnt[pos+2:]  #After the !=
    
            first = self.replaceReplaces(first, nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
            second = self.replaceReplaces(second, nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
    
            first = self.replaceText(first, nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
            second = self.replaceText(second, nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
            
            #Check if this statement is true.
            return first != second
            
        return True
            
    
    def regexReplace(self, pattern, text, replaceWith):
        import re
        m = re.finditer(pattern, text)
        #When the length of text changes you need to change the matches index's
        plusIndex = 0
        minusIndex = 0
        #Loop through the matches
        for match in m:
            lenBeforeReplace = len(text) #Length of text before the text is replaced
            
            text = text[:(match.start(0) - minusIndex) + plusIndex] + replaceWith + text[(match.end(0) - minusIndex) + plusIndex:]
            
            lenAfterReplace = len(text) #Length of text after the text is replaced
            if lenAfterReplace > lenBeforeReplace:
                plusIndex += lenAfterReplace - lenBeforeReplace
            else:
                minusIndex += lenBeforeReplace - lenAfterReplace
                    
        return text
    
    
    """Replaces '<replace .../>' tags"""
    def replaceReplaces(self, text, nick, host, msgType, channel, msg, server, nickColor="01", nick1="", nickColor1="01"):
        import re
        for replace in self.replaces:
            #Only check this replace against the text
            #If it matches, otherwise it'll just create a infinite loop
            #since i call, self.replaceReplaces
            if len(re.findall("(?<!\\\\)" + replace["key"], text)) > 0: 
                textReplace = self.replaceReplaces(replace["text"], nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
                textReplace = self.replaceText(textReplace, nick, host, msgType, channel, msg, server, nickColor, nick1, nickColor1)
                text = self.regexReplace("(?<!\\\\)" + replace["key"], text, textReplace)

                #Replace any Escaped 'replaces', for example \%time%
                text = self.regexReplace("\\\\" + replace["key"], text, replace["key"])
        return text
    
    
    
    """Replaces the stuff in between $, $....$"""            
    def replaceText(self, text, nick, host, msgType, channel, msg, server, nickColor="01", nick1="", nickColor1="01"):
        import re
        m = re.finditer("\\{.+?\\}", text)
        #When the length of text changes you need to change the matches index's
        plusIndex = 0
        minusIndex = 0
        #Loop through the matches
        for match in m:
            lenBeforeReplace = len(text) #Length of text before the text is replaced
            #----------
            matchText = match.group(0).replace("{","").replace("}","")
            leftText = text[:(match.start(0) - minusIndex) + plusIndex]
            rightText = text[(match.end(0) - minusIndex) + plusIndex:]
            
            if matchText.startswith("n"):
                #Nyx replace(class? i don't know what to call it lol)
                matchText = matchText[1:]
                #Now what to replace this with.
                
                if matchText.lower() == "n":
                    text = leftText + nick + rightText
                elif matchText.lower() == "h":
                    text = leftText + host + rightText
                elif matchText.lower() == "t":
                    text = leftText + msgType + rightText
                elif matchText.lower() == "c":
                    text = leftText + channel + rightText
                elif matchText.lower() == "m":
                    text = leftText + msg + rightText
                elif matchText.lower() == "nc":
                    text = leftText + nickColor + rightText   
                elif matchText.lower() == "n1":
                    text = leftText + nick1 + rightText   
                elif matchText.lower() == "c1":
                    text = leftText + nickColor1 + rightText   
                    
                
            elif matchText.startswith("s"):
                #Server
                matchText = matchText[1:]
                #Now what to replace this with.
                
                if matchText.lower() == "n":
                    text = leftText + server.cNick + rightText
            
                    
            elif matchText.startswith("t"):
                matchText = matchText[1:]
                #Time
                from time import localtime, strftime
                text = leftText + strftime("%" + matchText, localtime()) + rightText

            #TODO:Add more default replaces
            #----------
            lenAfterReplace = len(text) #Length of text after the text is replaced
            if lenAfterReplace > lenBeforeReplace:
                plusIndex += lenAfterReplace - lenBeforeReplace
            else:
                minusIndex += lenBeforeReplace - lenAfterReplace
    
        return text
                
                
        

import inspect
debugInfo=True
def pDebug(txt):
    if debugInfo:
        func = str(inspect.getframeinfo(inspect.currentframe().f_back).function)
        filename = str(inspect.getframeinfo(inspect.currentframe().f_back).filename);filename = filename.split("/")[len(filename.split("/"))-1]
        print "[\033[1;34m"+str(inspect.currentframe().f_back.f_lineno).rjust(3, '0')+"\033[1;m, " + filename +"(" + func + ")]\n    " + str(txt)
