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

def channelModeStuff(server,i):
    #:irc.archerseven.com 324 Nyx22 #ogame +nt
    #:irc.archerseven.com 329 Nyx22 #ogame 1253286530
    msgCode=i.split(" ")[1]
    
    if msgCode=="324":
        datParsed = ResponseParser.parseServerRegex(i)[0]
        for ch in server.channels:
            if ch.cName == datParsed.channel:
                ch.cMode = datParsed.msg

        for event in IRC.eventFunctions:
            if event.eventName == "onChannelModeChange" and event.cServer == server:
                gobject.idle_add(event.aFunc,datParsed,server)
    if msgCode=="329":
        datParsed = ResponseParser.parseServerRegex(i)[0]

        for event in IRC.eventFunctions:
            if event.eventName == "onChannelModeChange" and event.cServer == server:
                gobject.idle_add(event.aFunc,datParsed,server)


def topicStuff(server,i):
    #:irc.archerseven.com 332 Nyx28 #Nyx :The Nyx channel
    #:dom96!dom96@maddogsoftware.co.uk TOPIC #ogame :This is the ogame channel, talk about ogame battles and look for ogame help here....
    #:irc.archerseven.com 333 Nyx28 #ogame dom96 1252250064
    msgCode=i.split(" ")[1]

    if msgCode == "332":
        datParsed = ResponseParser.parseServerRegex(i)[0]
        for ch in server.channels:
            if ch.cName == datParsed.channel:
                ch.cTopic = datParsed.msg

        for event in IRC.eventFunctions:
            if event.eventName == "onTopicChange" and event.cServer == server:
                gobject.idle_add(event.aFunc,datParsed,server)
    elif msgCode == "333":
        datParsed = ResponseParser.parseServerRegex(i)[0]
        for event in IRC.eventFunctions:
            if event.eventName == "onTopicChange" and event.cServer == server:
                gobject.idle_add(event.aFunc,datParsed,server)

    elif "TOPIC" in i:
        m = ResponseParser.parseMsg(i,False)

        if m.typeMsg == "TOPIC":
            for ch in server.channels:
                if ch.cName == m.channel:
                    ch.cTopic = m.msg
            for event in IRC.eventFunctions:
                if event.eventName == "onTopicChange" and event.cServer == server:
                    gobject.idle_add(event.aFunc,m,server)

def pongResp(server,i):
    #:irc.archerseven.com PONG irc.archerseven.com :LAG1250452847.82
    try:
        if "PONG":
            m=i.split(" ")
            if m[1]=="PONG":
                for event in IRC.eventFunctions:
                    if event.eventName == "onLagChange" and event.cServer == server:
                        gobject.idle_add(event.aFunc,m,server)
    except:
        pass


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
                try:
                    nM = mLetters(m.msg.split()[0])
                    pDebug("Mode(Channel format)=" + nM)
                    usersWhoModeChanged=m.msg.replace(m.msg.split()[0] + " ","").split(" ")

                    #Check if it's a users mode being changed
                    if len(m.msg.split()) >= 2:
                        #Find the cTreeIter
                        for ch in server.channels:
                            if ch.cName.lower() == m.channel.lower():
                                for usr in ch.cUsers:
                                    for usrWMChange in usersWhoModeChanged:
                                        if usr.cNick.lower() == usrWMChange.lower():
                                            #And remove it(Because i have to change the position of it anyway)
                                            pDebug(str(usr.cTreeIter) + " " + usr.cNick + " " + m.msg + " " + ch.cName)
                                            cTreeIter = usr.cTreeIter
                                            for event in IRC.eventFunctions:
                                                if event.eventName == "onUserRemove" and event.cServer == server:
                                                    gobject.idle_add(event.aFunc,ch,server,cTreeIter,None)

                        for ch in server.channels:
                            if ch.cName.lower() == m.channel.lower():
                                for usr in ch.cUsers:
                                    for usrWMChange in usersWhoModeChanged:
                                        if usr.cNick.lower() == usrWMChange.lower():
                                            pDebug(usr.cMode)
                                            #Set the new MODE for the user.
                                            if nM.startswith("-"):
                                                for char in nM.replace("-",""):
                                                    usr.cMode = usr.cMode.replace(char,"")
                                                pDebug("usr.cMode = " + usr.cMode)
                                            else:
                                                usr.cMode += nM
    
                                            cIndex = findIndex(usr,server,ch)
                                            
                                            for event in IRC.eventFunctions:
                                                if event.eventName == "onUserJoin" and event.cServer == server:
                                                    event.aFunc(ch,server,cIndex,usr)#Might couse some random SEGFAULTS!!!!!!!!!!!!!!
                    #If it's not a user's mode being changed...It's most like a channels mode
                    else:
                        for ch in server.channels:
                            if ch.cName == m.channel:
                                #If the msg contains a -(Minus) then remove the mode from this channels cMode
                                if m.msg.startswith("-"):
                                    ch.cMode = ch.cMode.replace(m.msg.replace("-",""),"")
                                #If the msg has a +(plus) then append the mode to this channels cMode
                                else:
                                    ch.cMode += m.msg.replace("+","")

                except:
                    traceback.print_exc()


def mLetters(mode):
    #+q = Founder
    #+a = Admin
    #+o = op
    #+h = hop
    #+v = voice

    if mode.startswith("+"):
        nM=mode.replace("+","")
        nM=nM.replace("q","*")
        nM=nM.replace("a","!")
        nM=nM.replace("o","@")
        nM=nM.replace("h","%")
        nM=nM.replace("v","+")
    else:
        #If it's - then leave it there so
        #we can delete the mode.
        nM=mode.replace("q","*~")
        nM=nM.replace("a","!&")
        nM=nM.replace("o","@")
        nM=nM.replace("h","%")
        nM=nM.replace("v","+")

    return nM

#!--MODE CHANGE END--!#
#!--servResp Stuff--!#
def servResp(server,i):
    #Split into new lines \n
    splitNewLines = i.split("\n")
    for m in splitNewLines:
        splitI = i.split(" ")
    try:
        if (splitI[1] in numericCode() or splitI[1]+splitI[2] == "NOTICEAUTH" or "NOTICE AUTH" in m):
            datParsed = ResponseParser.parse(i,True,False)
            #pDebug("Considering this as a serverMsg: " + str(i))
            for event in IRC.eventFunctions:
                if event.eventName == "onServerMsg" and event.cServer == server:
                    gobject.idle_add(event.aFunc,datParsed,server)
    except:
        pDebug("\033[1;40m\033[1;33mIndex out of range-servResp\033[1;m\033[1;m")

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

    count=400
    while(count<599):
        count+=1
        numericCode.append(str(count))

    

    return numericCode
#!--Serv resp stuff END--!#

def nickResp(server,i):
    if "NICK" in i:
        m = ResponseParser.parseMsg(i,True)
        if m is not False:
            if m.typeMsg == "NICK":
                #If the person who changed their nick is you, change the nick in the server.
                if m.nick == server.cNick:
                    server.cNick = str(m.msg)

                for ch in server.channels:
                        for usr in ch.cUsers:
                            if usr.cNick.lower() == m.nick.lower():
                                pDebug(usr.cTreeIter)
                                cTreeIter = usr.cTreeIter
                                for event in IRC.eventFunctions:
                                    if event.eventName == "onUserRemove" and event.cServer == server:
                                        gobject.idle_add(event.aFunc,ch,server,cTreeIter,None)

                for ch in server.channels:
                        for usr in ch.cUsers:
                            if usr.cNick.lower() == m.nick.lower():
                                usr.cNick = m.msg
                                cIndex = findIndex(usr,server,ch)
                                for event in IRC.eventFunctions:
                                    if event.eventName == "onUserJoin" and event.cServer == server:
                                        event.aFunc(ch,server,cIndex,usr) #Might couse some random SEGFAULTS!!!!!!!!!!!!!!

                pDebug("NICK----" + m.nick + " = " + m.msg)
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

                try:
                    #Delete the user who got kicked.
                    for ch in server.channels:
                        if ch.cName.lower() == m.channel.lower():
                            for usr in ch.cUsers:
                                    
                                #m.nick is the nick that got kicked and the nick who kicked the user
                                #totally forgot...
                                personWhoWasKicked = m.nick.split(",")[1]
                                    
                                if usr.cNick.lower() == personWhoWasKicked.lower():
                                    pDebug("\033[1;32mRemoving %s from %s\033[1;m" % (personWhoWasKicked,ch.cName))
                                    cTreeIter = usr.cTreeIter
                                    ch.cUsers.remove(usr)
                                    #Call the onUserRemove event
                                    for event in IRC.eventFunctions:
                                        if event.eventName == "onUserRemove" and event.cServer == server:
                                            gobject.idle_add(event.aFunc,ch,server,cTreeIter,None)

                except:
                    traceback.print_exc()


def noticeResp(server,i):
    if "NOTICE" in i:
        m = ResponseParser.parseMsg(i,False)
        if m is not False:
            if m.typeMsg == "NOTICE":
                for event in IRC.eventFunctions:
                    if event.eventName == "onNoticeMsg" and event.cServer == server:
                        gobject.idle_add(event.aFunc,m,server)


def userStuff(server,i):#The user list.
    global USERS

    msgCode = i.split(" ")[1]
    #!--USERS STUFF--!#
    if ("353" == msgCode):
        if i.startswith(":"):
            USERS += "\n"
            USERS += i
    if ("366" == msgCode):
        USERS += i
        m = ResponseParser.parseServer(i)
        for channel in server.channels:
            if channel.cName == m[0].channel:
                #Add the users correctly.
                pDebug("\033[1;34m" + m[0].channel + "\033[1;m")
                channel.cUsers = []
                
                for user in ResponseParser.parseUsers(USERS,server,channel):
                    usr = IRC.user()
                    #Get the user mode.
                    userF=user
                    usr.cChannel=channel
                    usr.cTextBuffer=gtk.TextBuffer()
                    while(userF.startswith("*") or userF.startswith("!") or userF.startswith("@") or userF.startswith("%") 
or userF.startswith("+") or userF.startswith("~") or userF.startswith("&")):
                        usr.cMode += userF[:1]
                        userF=userF[1:]
                    #Get the nickname.
                    usr.cNick = user.replace(usr.cMode,"").replace(" ","")
                    channel.cUsers.append(usr)
                    pDebug("\033[1;32mAdded " + usr.cNick + " to " + channel.cName + " users list " + " with mode " + usr.cMode + "\033[1;m")

                for us in channel.cUsers:                
                    pDebug("\033[1;32m" + us.cNick + "(Mode " + us.cMode + ")" + "\033[1;m")

                USERS = ""

                for event in IRC.eventFunctions:
                    if event.eventName == "onUsersChange" and event.cServer == server:
                        event.aFunc(channel,server)



#!--USERS STUFF END--!#

def quitResp(server,i):#The quit message
    #!--QUIT MSG--!#
    if "QUIT" in i:
        m = ResponseParser.parseMsg(i,False)
        if m is not False:
            #Make sure it's a QUIT msg.
            #:Dredd!Dredd@admin.ikey.dynalias.com KILL gnome|nyx :ikey!admin.ikey.dynalias.com!Dredd (die whore)
            if m.typeMsg == "QUIT" or "KILL":
                for event in IRC.eventFunctions:
                    if event.eventName == "onQuitMsg" and event.cServer == server:
                        gobject.idle_add(event.aFunc,m,server)

                #Delete the user from the list of users.
                for ch in server.channels:
                    for usr in ch.cUsers:
                        if usr.cNick.lower()==m.nick.lower():
                            cTreeIter = usr.cTreeIter
                            #The user is removed from the userlist in the onUserRemove event

                            #Call the onUserRemove event
                            for event in IRC.eventFunctions:
                                if event.eventName == "onUserRemove" and event.cServer == server:
                                    gobject.idle_add(event.aFunc,ch,server,cTreeIter,usr)

    #!--QUIT MSG END--!#

def joinResp(server,i):#The join message
    global USERS
    #!--JOIN MSG--!#
    if "JOIN" in i:
        m = ResponseParser.parseMsg(i,False)
        if m is not False:
            #Make sure it's a JOIN msg.
            if m.typeMsg == "JOIN":
                #If it's you that JOINed
                if m.nick == server.cNick:
                    addNewUser=True

                    for ch in server.channels:
                        if ch.cName == m.channel:
                            addNewUser=False

                    if addNewUser==True:
                        nChannel = IRC.channel()
                        nChannel.cName = m.channel
                        nChannel.cTextBuffer = gtk.TextBuffer()
                        nChannel.UserListStore = gtk.ListStore(str,str)
                        try:
                            nChannel.cTreeIter = server.listTreeStore.append(server.listTreeStore.get_iter(0),[m.channel,None,gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)])
                        except:
                            import traceback; traceback.print_exc()
                        nChannel.cMsgBuffer = [] #This fixes the weird problem with the queue being in the wrong channel.
                        #Add the newly JOINed channel to the Servers channel list
                        server.channels.append(nChannel)

                    #Send the MODE message, to ask for the MODE of the channel.
                    server.cSocket.send("MODE " + m.channel + "\r\n")
                    server.cSocket.send("WHO " + m.channel + "\r\n")
                else:
                    #Add the user who JOINed to the list of users
                    for ch in server.channels:
                        if ch.cName == m.channel:
                            usr=IRC.user()
                            usr.cNick=m.nick
                            usr.cChannel=ch
                            usr.cTextBuffer = gtk.TextBuffer()
                            ch.cUsers.append(usr)
                            try:
                                cIndex=findIndex(usr,server,ch)
                            except:
                                import traceback;traceback.print_exc()

                            #Call the onUsersChange event
                            for event in IRC.eventFunctions:
                                if event.eventName == "onUserJoin" and event.cServer == server:
                                    #Set the users cTreeIter immediately
                                    event.aFunc(ch,server,cIndex,usr) #Might couse some random SEGFAULTS!!!!!!!!!!!!!!

                for event in IRC.eventFunctions:
                    if event.eventName == "onJoinMsg" and event.cServer == server:
                        gobject.idle_add(event.aFunc,m,server)

    #!--JOIN MSG END--!#
#!--FOR JOIN(And MODE) MSG, finds the index of where to insert the new user.--!#
def findIndex(usr,cServer,cChannel):
    if usr.cMode != "":
        pDebug(usr.cMode)
        #1.Check what mode the user contains.
        cISet=False

        fUsers=[] #Founder Users
        #Loop through the users.
        itr = cChannel.UserListStore.get_iter_first()
        while itr:
            if cChannel.UserListStore.get_value(itr, 1) == lookupIcon("founder"):
                fUsers.append(cChannel.UserListStore.get_value(itr,0))
            itr = cChannel.UserListStore.iter_next(itr)
        #Add the user to the list of users.
        if "*" in usr.cMode or "~" in usr.cMode:
            fUsers.append(usr.cNick)
        #Sort the list
        fUsers.sort(key=str.lower)
        #Find the index of where the user that JOINed is.
        if "*" in usr.cMode or "~" in usr.cMode:
            cIndex = fUsers.index(usr.cNick)
            cISet=True
        """--------------------------------------"""

        aUsers=[] #Admin Users
        #Loop through the users.
        itr = cChannel.UserListStore.get_iter_first()
        while itr:
            if cChannel.UserListStore.get_value(itr, 1) == lookupIcon("admin"):
                aUsers.append(cChannel.UserListStore.get_value(itr,0))
            itr = cChannel.UserListStore.iter_next(itr)
        #Add the user to the list of users.
        if "!" in usr.cMode or "&" in usr.cMode and cISet==False:
            aUsers.append(usr.cNick)
        #Sort the list
        aUsers.sort(key=str.lower)
        #Find the index of where the user that JOINed is.
        if "!" in usr.cMode or "&" in usr.cMode and cISet==False:
            cIndex = aUsers.index(usr.cNick) + len(fUsers)
            cISet=True
        """--------------------------------------"""

        oUsers=[] #Operator Users
        #Loop through the users.
        itr = cChannel.UserListStore.get_iter_first()
        while itr:
            if cChannel.UserListStore.get_value(itr, 1) == lookupIcon("op"):
                oUsers.append(cChannel.UserListStore.get_value(itr,0))
            itr = cChannel.UserListStore.iter_next(itr)
        #Add the user to the list of users.
        if "@" in usr.cMode and cISet==False:
            oUsers.append(usr.cNick)
        #Sort the list
        oUsers.sort(key=str.lower)
        #Find the index of where the user that JOINed is.
        if "@" in usr.cMode and cISet==False:
            pDebug(len(fUsers) + len(aUsers))
            cIndex = oUsers.index(usr.cNick) + len(fUsers) + len(aUsers)
            cISet=True
        """--------------------------------------"""
        
        hUsers=[] #Half operator Users
        #Loop through the users.
        itr = cChannel.UserListStore.get_iter_first()
        while itr:
            if cChannel.UserListStore.get_value(itr, 1) == lookupIcon("hop"):
                hUsers.append(cChannel.UserListStore.get_value(itr,0))
            itr = cChannel.UserListStore.iter_next(itr)
        #Add the user to the list of users.
        if "%" in usr.cMode and cISet==False:
            hUsers.append(usr.cNick)
        #Sort the list
        hUsers.sort(key=str.lower)
        #Find the index of where the user that JOINed is.
        if "%" in usr.cMode and cISet==False:
            cIndex = hUsers.index(usr.cNick) + len(fUsers) + len(aUsers) + len(oUsers)
            cISet=True
        """--------------------------------------"""

        vUsers=[] #voice Users
        #Loop through the users.
        itr = cChannel.UserListStore.get_iter_first()
        while itr:
            if cChannel.UserListStore.get_value(itr, 1) == lookupIcon("voice"):
                vUsers.append(cChannel.UserListStore.get_value(itr,0))
            itr = cChannel.UserListStore.iter_next(itr)
        #Add the user to the list of users.
        if "+" in usr.cMode and cISet==False:
            vUsers.append(usr.cNick)
        #Sort the list
        vUsers.sort(key=str.lower)
        #Find the index of where the user that JOINed is.
        if "+" in usr.cMode and cISet==False:
            cIndex = vUsers.index(usr.cNick) + len(fUsers) + len(aUsers) + len(oUsers) + len(hUsers)
            cISet=True
        """--------------------------------------"""

        #return the index
        return cIndex
        
        
    else:
        #1.Add the normal users, to a list. And the users with modes, to uNormUsers
        uNormUsrInt = 0
        normUsers=[]
        itr = cChannel.UserListStore.get_iter_first()
        while itr:
            if cChannel.UserListStore.get_value(itr, 1) == None:
                normUsers.append(cChannel.UserListStore.get_value(itr,0))
            else:
                uNormUsrInt+=1
                pDebug("Un-normal User adding..total:" + str(uNormUsrInt))
            itr = cChannel.UserListStore.iter_next(itr)
        #These should already be sorted alphabetically        
        #2.Add the user who JOINed, to the list.
        normUsers.append(usr.cNick)
        pDebug(usr.cNick)
        #3.Sort the list
        normUsers.sort(key=str.lower)
        #4.Find the index of where the nick that JOINed is.
        cIndex = normUsers.index(usr.cNick) + uNormUsrInt
        pDebug("Normal user, cIndex=" + str(cIndex))
        #5.Return the index.
        return cIndex

#Looks up an icon in the stock list
def lookupIcon(icon):
    stock_ids = gtk.stock_list_ids()
    for stock in stock_ids:
        if stock == icon:
            return stock
#!--FOR JOIN MSG END--!#

def partResp(server,i):#The part message
    #!--PART MSG--!#
    if "PART" in i:
        m = ResponseParser.parseMsg(i,False)
        if m is not False:
            #Make sure it's a PART msg.
            if m.typeMsg == "PART":
                for event in IRC.eventFunctions:
                    if event.eventName == "onPartMsg" and event.cServer == server:
                        gobject.idle_add(event.aFunc,m,server)
                if m.nick.lower() != server.cNick.lower():
                    #Delete the user from the list of users.
                    for ch in server.channels:
                        if ch.cName.lower() == m.channel.lower():
                            for usr in ch.cUsers:
                                if usr.cNick.lower()==m.nick.lower():
                                    cTreeIter = usr.cTreeIter #The TreeIter in the TreeStore to remove.
                                    ch.cUsers.remove(usr)
    
                                    #Call the onUserRemove event, which will remove the user from the TreeStore
                                    for event in IRC.eventFunctions:
                                        if event.eventName == "onUserRemove" and event.cServer == server:
                                            gobject.idle_add(event.aFunc,ch,server,cTreeIter,None)

    #!--PART MSG END--!#
def privmsgResp(server,i):#the private msg(Normal message)
    #!--PRIVMSG STUFF START--!#
    if "PRIVMSG" in i:
        m = ResponseParser.parseMsg(i,False)
        if m is not False:
            pDebug(m.msg)
            #!--CTCP VERSION--!#
            if m.msg.startswith("VERSION"):
                import platform
                IRCHelper.sendNotice(server,m.nick,"VERSION Nyx 0.1 Revision 260909 Copyleft 2009 Mad Dog software - http://sourceforge.net/projects/nyxirc/ - running on " + platform.platform() + "")
            #!--CTCP VERSION END--!#
            #!--CTCP TIME--!#
            if m.msg.startswith("TIME"):
                IRCHelper.sendNotice(server,m.nick,"TIME " + strftime("%b %d %H:%M:%S %Z", localtime()) + "")
                #TIME Aug 02 12:56:09 BST
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
    
    msgCode = i.split(" ")[1]

    #!--MOTD STUFF--!#
    #MOTD Start code, now i need to add the whole MOTD to one string until the MOTD END(376)
    if ("375" == msgCode): 
        MOTDStarted = True
    #Make sure it's a 376 message and that the message doesn't contain PRIVMSG or NOTICE, 
    #couse if the PRIVMSG or notice contains 376 it's gonna print the MOTD again
    elif ("376" == msgCode):
        MOTDStarted = False
        MOTD += "\n" + i
        pResp = ResponseParser.parse(MOTD,True,True)
        server.cMotd = pResp
        #Call all the onMotdMsg events
        for event in IRC.eventFunctions:
            if event.eventName == "onMotdMsg" and event.cServer == server:
                gobject.idle_add(event.aFunc,pResp,server)

    #If MOTD is started (--and the code is 372--), add the motd to the MOTD string.                        
    if MOTDStarted == True and msgCode == "372":
        if i.startswith(":"):
            MOTD += "\n"                                
        MOTD += i
    #!--MOTD STUFF END--!#




import inspect
debugInfo=True
def pDebug(txt):
    if debugInfo:
        func = str(inspect.getframeinfo(inspect.currentframe().f_back).function)
        filename = str(inspect.getframeinfo(inspect.currentframe().f_back).filename);filename = filename.split("/")[len(filename.split("/"))-1]
        print "[\033[1;34m"+str(inspect.currentframe().f_back.f_lineno).rjust(3, '0')+"\033[1;m, " + filename +"(" + func + ")]\n    " + str(txt)


