#!/usr/bin/env python
"""
Nyx - A powerful IRC Client
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
import gobject

#JOIN, Joins a channel.
def join(server,cChannel,listTreeStore):
    server.cSocket.send("JOIN " + cChannel + "\r\n")
#sendMsg, checks if the message is bigger then 400 characters or contains newlines and sends it immediately or adds it to the msgBuffer
def sendMsg(server,cChannel,msg):
    if "\n" in msg or len(msg) > 400:
        #If there are new lines in the msg
        if "\n" in msg:
            #Just split it into new lines.
            msgSplit=msg.split("\n")
        #Else, if the message is bigger then 400 characters
        else:
            #split the message into 400 characters
            msgSplit=[]
            iMsg=msg
            while (len(iMsg) > 400):
                msgSplit.append(iMsg[:400])
                iMsg=iMsg[400:]
            msgSplit.append(iMsg)

        newMsgSplit=[]
        #Loop through the msgSplit to see if any of the messages are more then 400 characters
        for i in range(0,len(msgSplit)):
            if len(msgSplit[i]) > 400:
                #If this message is bigger then 400 characters then split it.
                iMsg=msgSplit[i]
                while (len(iMsg) > 400):
                    newMsgSplit.append(iMsg[:400])
                    iMsg=iMsg[400:]
                newMsgSplit.append(iMsg)
            else:
                #If this message is not bigger then 400 characters, then add it to the new list without spliting it.
                newMsgSplit.append(msgSplit[i])
        msgSplit=newMsgSplit

        #Loops through the parts of the message(the split message)
        for i in range(0,len(msgSplit)):
            if msgSplit[i] != "":
                import time
                instantMsg=False #If this is set to true the message won't be added to the msg buffer.
                #Loops through the channels to find the right channel, to append the new msgBuffer
                for ch in server.channels:
                    usrDest=IRC.user() #Made it not None, it couses a bug with or ch.cName == usrDest.cChannel.cName, so i changed it to this...
                    if cChannel.startswith("#") == False:
                        for usr in ch.cUsers:
                            if usr.cNick == cChannel:
                                usrDest=usr
                    if ch.cName == cChannel or ch.cName == usrDest.cChannel.cName:
                        channel=ch       
                        pDebug("Setting channel to " + ch.cName)

                #If this message is the 5th message to be sent in a row, then add >the number of sendInstantly equal to False msgBuffers< * 3
                #(So it waits 3 times the number of non instantly sent messages, to send this message.)
                if i >= 5:
                    time=time.time() + (3*(len(channel.cMsgBuffer)+1))
                elif i < 5 and len(channel.cMsgBuffer) != 0:
                    time=time.time() + (3*(len(channel.cMsgBuffer)+1))
                #Else, this is a message to be sent instantly.
                else:
                    cmdSendMsg(server,cChannel,msgSplit[i])
                    instantMsg=True

                if instantMsg != True:
                    msgBuff=IRC.msgBuffer()
                    msgBuff.msg=msgSplit[i]
                    msgBuff.sendTimestamp=time
                    msgBuff.dest=cChannel

                    channel.cMsgBuffer.append(msgBuff)
                    #Call all the onByteSendChange events
                    for event in IRC.eventFunctions:
                        if event.eventName == "onByteSendChange" and event.cServer == server:
                            gobject.idle_add(event.aFunc,server,len(channel.cMsgBuffer))


    else:
        msgSent = False
    
        for ch in server.channels:
            usrDest=IRC.user() #Made it not None, it couses a bug with or ch.cName == usrDest.cChannel.cName, so i changed it to this...
            if cChannel.startswith("#") == False:
                for usr in ch.cUsers:
                    if usr.cNick == cChannel:
                        usrDest=usr

            if ch.cName == cChannel or ch.cName == usrDest.cChannel.cName:
                #If the msgBuffer(msg queue) has no messages waiting to be sent, send this message right now.
                if len(ch.cMsgBuffer) == 0:
                    cmdSendMsg(server,cChannel,msg)
                    msgSent = True
                    break
                #If the msgBuffer(msg queue) has messages waiting, add this new message to the end of the queue.
                else:
                    import time
                    instantMsg=False #If this is set to true the message won't be added to the msg buffer.
                    #If this message is the 5th message to be sent in a row, then add >the number of sendInstantly equal to False msgBuffers< * 3
                    #(So it waits 3 times the number of non instantly sent messages, to send this message.)
                    if len(ch.cMsgBuffer) >= 5:
                        time=time.time() + (3*(len(ch.cMsgBuffer)+1))
                    #Else, this is a message to be sent instantly.
                    else:
                        cmdSendMsg(server, ch.cName, msg)
                        instantMsg = True
                        msgSent = True

                    if instantMsg != True:
                        msgBuff=IRC.msgBuffer()
                        msgBuff.msg=msg
                        msgBuff.sendTimestamp=time
                        msgBuff.dest=cChannel
                        ch.cMsgBuffer.append(msgBuff)
                        pDebug("\033[1;31mAdded to " + ch.cName)
                        #Call all the onByteSendChange events
                        for event in IRC.eventFunctions:
                            if event.eventName == "onByteSendChange" and event.cServer == server:
                                gobject.idle_add(event.aFunc,server,len(ch.cMsgBuffer))

                    break
                    
        #If you can't find a message buffer for a channel or a user, just send the message
        #TODO: Maybe make it add to the server buffer ??
        if msgSent == False:
            cmdSendMsg(server, cChannel, msg)

#A cleaner one function way to send a message
def cmdSendMsg(server,cChannel,msg):
    pDebug("\033[1;34mPRIVMSG " + cChannel + " :" + msg + "\\r\\n\033[1;m")
    server.cSocket.send("PRIVMSG " + cChannel + " :" + msg + "\r\n")

    cResp = ResponseParser.privMsg()
    cResp.nick = server.cNick
    cResp.host = ""
    cResp.typeMsg = "PRIVMSG"
    cResp.channel = cChannel
    cResp.msg = msg
    #Call all the onOwnPrivMsg events
    for event in IRC.eventFunctions:
        if event.eventName == "onOwnPrivMsg" and event.cServer == server:
            gobject.idle_add(event.aFunc,cResp,server)

#sendNotice, Sends a NOTICE to the channel specified.
def sendNotice(server,cChannel,msg):
    pDebug("\033[1;34mNOTICE " + cChannel + " :" + msg + "\\r\\n\033[1;m")
    server.cSocket.send("NOTICE " + cChannel + " :" + msg + " \r\n") 

import inspect
debugInfo=True
def pDebug(txt):
    if debugInfo:
        func = str(inspect.getframeinfo(inspect.currentframe().f_back).function)
        filename = str(inspect.getframeinfo(inspect.currentframe().f_back).filename);filename = filename.split("/")[len(filename.split("/"))-1]
        print "[\033[1;34m"+str(inspect.currentframe().f_back.f_lineno).rjust(3, '0')+"\033[1;m, " + filename +"(" + func + ")]\n    " + str(txt)




