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
import IRC
import IRCHelper

def onServerMsg(m):
    print "Event" + m

def onMOTDMsg(m,cServer):
    IRCHelper.join(cServer,"#botplay")
def onJoinMsg(m,cServer):
    print m.nick
    

#IRCLibraryTesting app.
print "IRCLibrary testing app 0.1"

server = IRC.server()
IRC.connectEvent("serverMsg",onServerMsg,server)
IRC.connectEvent("onMotdMsg",onMOTDMsg,server)
IRC.connectEvent("onPartMsg",onJoinMsg,server)

server = IRC.connect("irc.spotchat.org","vIRC","vIRC",6667,server)
print server.cNick
#server2 = IRC.server()
#IRC.connectEvent("serverMsg",onServerMsg,server2)
#IRC.connectEvent("onMotdMsg",onMOTDMsg,server2)
#server = IRC.connect("irc.freenode.net","vIRC","vIRC",8001,server2)

while(True):
    pass





