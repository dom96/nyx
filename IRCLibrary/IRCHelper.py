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
import gobject

#JOIN, Joins a channel.
def join(server,cChannel,listTreeStore):
    server.cSocket.send("JOIN " + cChannel + "\r\n")
#sendMsg, Sends a PRIVMSG(message) to the channel specified.
def sendMsg(server,cChannel,msg,buffMsg):
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

        #Loops through the parts of the message(the split message)
        for i in range(0,len(msgSplit)):
            import time
            msgBuff=IRC.msgBuffer()
            msgBuff.msg=msgSplit[i]
            nonInsta=0 #How many messages with sendInstantly equal to False there is.
            #Loops through the channels to find the right channel, to append the new msgBuffer
            for ch in server.channels:
                if ch.cName == cChannel:
                    channel=ch       
                    #Loops through the msgBuffers and counts how many non sendInstantly messages there is. 
                    for mBuff in ch.cMsgBuffer:
                        if mBuff.sendInstantly != True:
                            nonInsta+=1
            #If this message is the 5th message to be sent in a row, then add >the number of sendInstantly equal to False msgBuffers< * 3
            #(So it waits 3 times the number of non instantly sent messages, to send this message.)
            if i >= 5:
                time=time.time() + (3*(nonInsta+1))
            #Else, this is a message to be sent instantly.
            else:
                time=time.time()
                msgBuff.sendInstantly=True

            msgBuff.sendTimestamp=time
            channel.cMsgBuffer.append(msgBuff)
            #Call all the onByteSendChange events
            for event in IRC.eventFunctions:
                if event.eventName == "onByteSendChange" and event.cServer == server:
                    gobject.idle_add(event.aFunc,server,len(channel.cMsgBuffer))

    else:
        for ch in server.channels:
            if ch.cName == cChannel:
                #If it's not a message originating from IRC.sendMsgBuffer
                if buffMsg == False:
                    #If the msgBuffer(msg queue) has no messages waiting to be sent, send this message right now.
                    if len(ch.cMsgBuffer) == 0:
                        print "\033[1;34mPRIVMSG " + cChannel + " :" + msg + "\\r\\n\033[1;m"
                        server.cSocket.send("PRIVMSG " + cChannel + " :" + msg + "\r\n") 
                    #If the msgBuffer(msg queue) has messages waiting, add this new message to the end of the queue.
                    else:
                        import time
                        msgBuff=IRC.msgBuffer()
                        #If this message is the 5th message to be sent in a row, then add >the number of sendInstantly equal to False msgBuffers< * 3
                        #(So it waits 3 times the number of non instantly sent messages, to send this message.)
                        if len(ch.cMsgBuffer) >= 5:
                            time=time.time() + (3*(len(ch.cMsgBuffer)+1))
                        #Else, this is a message to be sent instantly.
                        else:
                            time=ch.cMsgBuffer[len(ch.cMsgBuffer)-1].sendTimestamp
                            msgBuff.sendInstantly=True

                        msgBuff.msg=msg
                        msgBuff.sendTimestamp=time
                        ch.cMsgBuffer.append(msgBuff)

                        #Call all the onByteSendChange events
                        for event in IRC.eventFunctions:
                            if event.eventName == "onByteSendChange" and event.cServer == server:
                                gobject.idle_add(event.aFunc,server,len(ch.cMsgBuffer))


                #If it is originating from IRC.sendMsgBuffer
                else:
                    print "\033[1;34mPRIVMSG " + cChannel + " :" + msg + "\\r\\n\033[1;m"
                    server.cSocket.send("PRIVMSG " + cChannel + " :" + msg + "\r\n") 


#sendNotice, Sends a NOTICE to the channel specified.
def sendNotice(server,cChannel,msg):
    server.cSocket.send("NOTICE " + cChannel + " :" + msg + " \r\n") 







