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
import socket
import string
import traceback
import re
import thread
import IRC
import ResponseParser

#JOIN, Joins a channel.
def join(server,cChannel,listTreeStore):
    server.cSocket.send("JOIN " + cChannel + "\r\n")
#sendMsg, Sends a PRIVMSG(message) to the channel specified.
def sendMsg(server,cChannel,msg):
    server.cSocket.send("PRIVMSG " + cChannel + " :" + msg + " \r\n") 
#sendNotice, Sends a NOTICE to the channel specified.
def sendNotice(server,cChannel,msg):
    server.cSocket.send("NOTICE " + cChannel + " :" + msg + " \r\n") 







