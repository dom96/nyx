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
import gobject
import sys
from time import *
#Own imports
import IRC
import ResponseParser
import IRCHelper

USERS = ""

MOTDStarted = False
MOTD = ""

#!--MODE CHANGE--!#
def modeResp(server,i):
    #:ChanServ!services@ArcherNet.net MODE ## +o Nyx1
    if "MODE" in i:
        m=ResponseParser.parseMode(i)
        if m is not False:
            if m.typeMsg == "MODE":
                for event in IRC.eventFunctions:
                    if event.eventName == "onModeChange" and event.cServer == server:
                        gobject.idle_add(event.aFunc,m,server)

#!--MODE CHANGE END--!#
#!--servResp Stuff--!#
def servResp(server,i):
    #Split into new lines \n
    splitNewLines = i.split("\n")
    for m in splitNewLines:
        splitI = i.split(" ")
    try:
        if (splitI[1] in numericCode() or splitI[1]+splitI[2] == "NOTICEAUTH"):
            datParsed = ResponseParser.parse(i,True,False)
            for event in IRC.eventFunctions:
                if event.eventName == "onServerMsg" and event.cServer == server:
                    gobject.idle_add(event.aFunc,datParsed,server)
    except:
        print "Index out of range-servResp"

def numericCode():
    #Make a list of Numeric Codes...001,002,003,004,005,006,007,008,009...099
    #200,201,....300
    #This might not be such a good idea, might get slow on slow computers.
    """Consider a alternative"""
    numericCode=[]

    count=0
    while(count<99):
        count+=1
        if len(str(count))==1:
            numericCode.append("00"+str(count))
        else:    
            numericCode.append("0"+str(count))
    count=199
    while(count<300):
        count+=1
        numericCode.append(str(count))
    return numericCode
#!--Serv resp stuff END--!#

def nickResp(server,i):
    if "NICK" in i:
        m = ResponseParser.parseMsg(i)
        if m is not False:
            if m.typeMsg == "NICK":
                #If the person who changed their nick is you, change the nick in the server.
                if m.nick == server.cNick:
                    server.cNick = m.msg

                print "NICK----"
                for event in IRC.eventFunctions:
                    if event.eventName == "onNickChange" and event.cServer == server:
                        gobject.idle_add(event.aFunc,m,server)


def kickResp(server,i):
    if "KICK" in i:
        m = ResponseParser.parseKick(i)
        if m is not False:
            if m.typeMsg == "KICK":
                for event in IRC.eventFunctions:
                    if event.eventName == "onKickMsg" and event.cServer == server:
                        gobject.idle_add(event.aFunc,m,server)


def noticeResp(server,i):
    if "NOTICE" in i:
        m = ResponseParser.parseMsg(i)
        if m is not False:
            if m.typeMsg == "NOTICE":
                for event in IRC.eventFunctions:
                    if event.eventName == "onNoticeMsg" and event.cServer == server:
                        gobject.idle_add(event.aFunc,m,server)
                        #event.aFunc(m,server)


def userStuff(server,i):#The user list.
    global USERS
    #!--USERS STUFF--!#
    if ("353" in i and "PRIVMSG" not in i and "NOTICE" not in i):
        if i.startswith(":"):
            USERS += "\n"
            USERS += i
    if ("366" in i and "PRIVMSG" not in i and "NOTICE" not in i):
        USERS += i
        m = ResponseParser.parseServer(i)
        for channel in server.channels:
            if channel.cName == m[0].channel:
                #Add the users correctly.
                print "\033[1;34m" + m[0].channel + "\033[1;m"
                channel.cUsers = []
                
                for user in ResponseParser.parseUsers(USERS,server,channel):
                    usr = IRC.user()
                    #Get the user mode.
                    userF=user
                    while(userF.startswith("*") or userF.startswith("!") or userF.startswith("@") or userF.startswith("%") 
or userF.startswith("+") or userF.startswith("~") or userF.startswith("&")):
                        usr.cMode += userF[:1]
                        userF=userF[1:]
                    #Get the nickname.
                    usr.cNick = user.replace(usr.cMode,"").replace(" ","")
                    channel.cUsers.append(usr)
                    print "\033[1;31mAdded " + usr.cNick + " to " + channel.cName + " users list " + " with mode " + usr.cMode + "\033[1;m"

                for us in channel.cUsers:                
                    print "\033[1;32m" + us.cNick + "(Mode " + us.cMode + ")" + "\033[1;m"

                for event in IRC.eventFunctions:
                    if event.eventName == "onUsersChange" and event.cServer == server:
                        event.aFunc(channel,server)



#!--USERS STUFF END--!#

def quitResp(server,i):#The quit message
    #!--QUIT MSG--!#
    if "QUIT" in i:
        m = ResponseParser.parseMsg(i)
        if m is not False:
            #Make sure it's a QUIT msg.
            if m.typeMsg == "QUIT":
                for event in IRC.eventFunctions:
                    if event.eventName == "onQuitMsg" and event.cServer == server:
                        gobject.idle_add(event.aFunc,m,server)

                #Delete the user from the list of users.
                for ch in server.channels:
                    for usr in ch.cUsers:
                        if usr.cNick.lower()==m.nick.lower():
                            ch.cUsers.remove(usr)

                            #Call the onUsersChange event
                            for event in IRC.eventFunctions:
                                if event.eventName == "onUsersChange" and event.cServer == server:
                                    gobject.idle_add(event.aFunc,ch,server)

    #!--QUIT MSG END--!#

def joinResp(server,i):#The join message
    global USERS
    #!--JOIN MSG--!#
    if "JOIN" in i:
        m = ResponseParser.parseMsg(i)
        if m is not False:
            #Make sure it's a JOIN msg.
            if m.typeMsg == "JOIN":
                if m.nick == server.cNick:
                    addNewUser=True

                    for ch in server.channels:
                        if ch.cName == m.channel:
                            addNewUser=False

                    if addNewUser==True:
                        nChannel = IRC.channel()
                        nChannel.cName = m.channel
                        nChannel.cTextBuffer = gtk.TextBuffer()
                        nChannel.cTreeIter = server.listTreeStore.append(server.listTreeStore.get_iter(0),[m.channel,None])
                        #Add the newly JOINed channel to the Servers channel list
                        server.channels.append(nChannel)
                else:
                    #Add the user who joined to the list of users
                    for ch in server.channels:
                        if ch.cName == m.channel:
                            usr=IRC.user()
                            usr.cNick=m.nick
                            ch.cUsers.append(usr)

                            #Call the onUsersChange event
                            for event in IRC.eventFunctions:
                                if event.eventName == "onUsersChange" and event.cServer == server:
                                    gobject.idle_add(event.aFunc,ch,server)

                for event in IRC.eventFunctions:
                    if event.eventName == "onJoinMsg" and event.cServer == server:
                        gobject.idle_add(event.aFunc,m,server)

                

    #!--JOIN MSG END--!#
def partResp(server,i):#The part message
    #!--PART MSG--!#
    if "PART" in i:
        m = ResponseParser.parseMsg(i)
        if m is not False:
            #Make sure it's a PART msg.
            if m.typeMsg == "PART":
                for event in IRC.eventFunctions:
                    if event.eventName == "onPartMsg" and event.cServer == server:
                        gobject.idle_add(event.aFunc,m,server)

                #Delete the user from the list of users.
                for ch in server.channels:
                    if ch.cName.lower() == m.channel.lower():
                        for usr in ch.cUsers:
                            if usr.cNick.lower()==m.nick.lower():
                                ch.cUsers.remove(usr)

                                #Call the onUsersChange event
                                for event in IRC.eventFunctions:
                                    if event.eventName == "onUsersChange" and event.cServer == server:
                                        gobject.idle_add(event.aFunc,ch,server)

    #!--PART MSG END--!#
def privmsgResp(server,i):#the private msg(Normal message)
    #!--PRIVMSG STUFF START--!#
    if "PRIVMSG" in i:
        m = ResponseParser.parseMsg(i)
        if m is not False:

            #!--CTCP VERSION--!#
            if m.msg.startswith("VERSION"):
                IRCHelper.sendNotice(server,m.nick,"Nyx 0.1 Revision 040809 Copyleft 2009 Mad Dog software - http://sourceforge.net/projects/nyxirc/")
            #!--CTCP VERSION END--!#
            #!--CTCP TIME--!#
            if m.msg.startswith("TIME"):
                IRCHelper.sendNotice(server,m.nick,strftime("%b %d %H:%M:%S %Z", localtime()))
                #Aug 02 12:56:09 BST
            #!--CTCP TIME END--!#
            #!--CTCP PING--!#
            if m.msg.startswith("PING"):
                IRCHelper.sendNotice(server,m.nick,m.msg)
                #PING 123456789
            #!--CTCP PING END--!#
            
            #Call all the onPrivMsg events
            for event in IRC.eventFunctions:
                if event.eventName == "onPrivMsg" and event.cServer == server:
                    gobject.idle_add(event.aFunc,m,server)
    #!--PRIVMSG STUFF END--!#
def motdStuff(server,i):#MOTD stuff
    global MOTDStarted
    global MOTD    
    
    #!--MOTD STUFF--!#
    if ("375" in i and "PRIVMSG" not in i and "NOTICE" not in i): #MOTD Start code, now i need to add the whole MOTD to a one string until the MOTD END(376)
        MOTDStarted = True
    elif ("376" in i and "PRIVMSG" not in i and "NOTICE" not in i):#Make sure it's a 376 message and that the message doesn't contain PRIVMSG or NOTICE, couse if the PRIVMSG or notice contains 376 it's gonna print the MOTD again
        MOTDStarted = False
        MOTD += "\n" + i
        pResp = ResponseParser.parse(MOTD,True,True)
        #Call all the onMotdMsg events
        for event in IRC.eventFunctions:
            if event.eventName == "onMotdMsg" and event.cServer == server:
                gobject.idle_add(event.aFunc,pResp,server)

    #If MOTD is started and the code is 372, add the motd to the MOTD string.                        
    if MOTDStarted == True:
        if i.startswith(":"):
            MOTD += "\n"                                
        MOTD += i
    #!--MOTD STUFF END--!#







