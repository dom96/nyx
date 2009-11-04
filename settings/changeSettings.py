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
def changeTheme(name):
    #Get this themes('name') path
    import os, xml.dom.minidom, os.path, sys, XmlHelper
    path=""
    for f in os.listdir("../themes"):
        if f.endswith(".xml"):
            themeXmlDoc=xml.dom.minidom.parse("../themes/" + f)
            nameElement = themeXmlDoc.getElementsByTagName("name")[0]
            tName = XmlHelper.getText(nameElement.childNodes)
            if tName.lower() == name.lower():
                path =  "/themes/" + f

    if path == "": return ""


    #Parse the settings.xml file...os.path.abspath(os.path.dirname(sys.argv[0])) get's the scripts directory
    xmlDoc=xml.dom.minidom.parse(os.path.abspath(os.path.dirname(sys.argv[0])) + "/settings.xml")
    try:
        themeElement = xmlDoc.getElementsByTagName("theme")[0]
    except:
        pDebug("theme element was not found in settings.xml, creating one.")
        themeElement = xmlDoc.createElement("theme")
        themeElement.setAttribute("name", name)
        themeElement.setAttribute("path", path)
        xmlDoc.documentElement.appendChild(themeElement)
        
        f = open(os.path.abspath(os.path.dirname(sys.argv[0])) + "/settings.xml","w").write(xmlDoc.toxml())
        return True

    themeElement.setAttribute("name", name)
    themeElement.setAttribute("path", path)
    f = open(os.path.abspath(os.path.dirname(sys.argv[0])) + "/settings.xml","w").write(xmlDoc.toxml())
    return True












import inspect
debugInfo=True
def pDebug(txt):
    if debugInfo:
        func = str(inspect.getframeinfo(inspect.currentframe().f_back).function)
        filename = str(inspect.getframeinfo(inspect.currentframe().f_back).filename);filename = filename.split("/")[len(filename.split("/"))-1]
        print "[\033[1;34m"+str(inspect.currentframe().f_back.f_lineno).rjust(3, '0')+"\033[1;m, " + filename +"(" + func + ")]\n    " + str(txt)
