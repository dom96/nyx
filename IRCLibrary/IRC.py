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
import thread
#Own imports
import ResponseParser
import IRCHelper
import PongStuff

import gobject

gobject.threads_init()

eventFunctions = [] #A list of all the connected events(eventDef() class)


#Connects to a server(Starts everything)
#Address=string,nick=string,realname=string,port=integer,server=server class,queue()

def connect(address, nick, realname,port,server):
    #License....
    print "IRCLibrary Copyright (C) 2009 Mad Dog Software"
    print "This program comes with ABSOLUTELY NO WARRANTY."
    print "This is free software, and you are welcome to redistribute it"
    print "under certain conditions; look at the license for more details."    
    #License End
    #Connect to the server with a socket.
    pDebug("Connecting to:" + address)
    server.cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Make a new socket
    server.cSocket.connect((address, port)) #Connect to the server

    #Start the while loop, in another thread, so that i can return the server.
    gtk.gdk.threads_enter()
    thread.start_new(pingPong,(server,))
    gtk.gdk.threads_leave()
    """
    I've put it here, because now it gets the server responses too.
    This let's it not hang, on servers when there is no reply to the USER message or the NICK message.        
    """

    #data = server.cSocket.recv(1024) #Receive the response
    #print data
    #datParsed = ResponseParser.parse(data,True,False)
    #for event in eventFunctions:
        #if event.eventName == "onServerMsg" and event.cServer == server:
            #event.aFunc(datParsed,server)

    pDebug("Sending NICK")
    #Send the "NICK" command, to the server, this is the third command to be sent to the server.And last step to connect.
    server.cSocket.send('NICK ' + nick + ' \r\n') # NICK >nick< CR-LF
    #Don't wait for responses to the NICK command
    #data = server.cSocket.recv(1024) #Receive the response
    #print data
    #datParsed = ResponseParser.parse(data,True,False)
    #for event in eventFunctions:
        #if event.eventName == "onServerMsg" and event.cServer == server:
            #event.aFunc(datParsed,server)


    pDebug("Sending USER")
    #Send the "USER" command, to the server, this is the second command to be sent to the server.
    server.cSocket.send("USER " + nick + " " + nick + " " + address + " :" + realname + "\r\n") # USER >nick< >nick< >address< :>realname< CR-LF 
    #data = server.cSocket.recv(1024) #Receive the response
    #print data
    #datParsed = ResponseParser.parse(data,True,False)
    #for event in eventFunctions:
        #if event.eventName == "onServerMsg" and event.cServer == server:
            #event.aFunc(datParsed,server)

    #Add all the info of the server.
    server.cAddress = address
    server.cNick = nick
    server.cRealname = realname
    server.cPort = port
    server.cName = address


    gtk.gdk.threads_enter()
    thread.start_new(pingServer,(server,))
    gtk.gdk.threads_leave()

    gtk.gdk.threads_enter()
    thread.start_new(sendMsgBuffer,(server,))
    gtk.gdk.threads_leave()

def pingPong(server):
    MOTDStarted = False
    MOTD=""

    UsersStarted = False
    USERS=""

    msg = ""
    while(True):
        try:
            data = server.cSocket.recv(8192)
            msg += data
            if msg !="":
                pDebug("Raw received data from server:\n \033[1;32m" + data + " \033[1;m")
                if msg.startswith("PING"): #If the server sends a PING command...
                    pDebug("Received PING( \033[1;32m" + msg + "\033[1;m )")
                    #Reply with a PONG command, to keep the connection alive.
                    server.cSocket.send("PONG :" + msg.split(":")[1] + " \r\n") 
                    pDebug("Replied to Ping with: \033[1;34m" + "PONG :" + msg.split(":")[1] + " \\r\\n\033[1;m")
                    msg=""
                else:
                    #If the message ends with \n (Carriage Return) then that means that the command is a full command
                    #If not then that means that the last line of msg is a uncompletely received command. 
                    if msg.endswith("\n"):
                        for i in string.split(msg,"\n"):
                            #!--MOTD STUFF--!#
                            PongStuff.motdStuff(server,i)
                            #!--MOTD STUFF END--!#
                            #!--PRIVMSG STUFF START--!#
                            PongStuff.privmsgResp(server,i)
                            #!--PRIVMSG STUFF END--!#
                            #!--PART MSG--!#
                            PongStuff.partResp(server,i)
                            #!--PART MSG END--!#
                            #!--JOIN MSG--!#
                            PongStuff.joinResp(server,i)
                            #!--JOIN MSG END--!#
                            #!--QUIT MSG--!#
                            PongStuff.quitResp(server,i)
                            #!--QUIT MSG END--!#
                            #!--USERS STUFF--!#
                            PongStuff.userStuff(server,i)
                            #!--USERS STUFF END--!#
                            #!--NOTICE MSG--!#
                            PongStuff.noticeResp(server,i)
                            #!--NOTICE MSG END--!#
                            #!--KICK MSG--!#
                            PongStuff.kickResp(server,i)
                            #!--KICK MSG END--!#
                            #!--NICK MSG--!#
                            PongStuff.nickResp(server,i)
                            #!--NICK MSG END--!#
                            #!--SERVER MSG--!#
                            PongStuff.servResp(server,i)
                            #!--SERVER MSG END--!#
                            #!--MODE MSG--!#
                            PongStuff.modeResp(server,i)
                            #!--MODE MSG END--!#
                            #!--PING MSG--!#
                            PongStuff.pongResp(server,i)
                            #!--PING MSG END--!#
                            #Reset the msg after parsing
                            msg=""
        except:
            pass
            #traceback.print_exc()   

def pingServer(server):
    while(True):
        import time
        server.cSocket.send("PING LAG" + str(time.time()) + "\r\n")
        time.sleep(15)

def sendMsgBuffer(server):
    while(True):
        import time
        time.sleep(1)
        for i in server.channels:
            if len(i.cMsgBuffer) != 0:
                for msgBuff in i.cMsgBuffer:
                    currentTime=time.time()
                    if currentTime >= msgBuff.sendTimestamp:
                        i.cMsgBuffer.remove(msgBuff)
                        pDebug("sendMsgBuffer, " + i.cName)
                        IRCHelper.cmdSendMsg(server,msgBuff.dest,msgBuff.msg)
                        pDebug("Entries in buffer left:"+str(len(i.cMsgBuffer)))

                        #Call all the onByteSendChange events
                        for event in eventFunctions:
                            if event.eventName == "onByteSendChange" and event.cServer == server:
                                gobject.idle_add(event.aFunc,server,len(i.cMsgBuffer))
                        break

#A connection to a server
class server():
    cAddress="" #The address of this server.
    cNick="" #The nick that is used on this server.
    cRealname="" #The Real name that is being used on this server.
    cPort=0 #The port being used, on this server.
    cName="" #Name of this server.
    cSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #The socket being used by this server.
    cTextBuffer=gtk.TextBuffer() #The TextBuffer, with the server messages.
    channels=[] #A List of channel(), these are all of the channels currently connected on his server.
    listTreeStore=gtk.TreeStore #The treestore, for easy access
    cTreeIter=gtk.TreeIter #The treeiter, for easy access of the servers iter.

#A channel connection, on a server.
class channel():
    cName="" #Name of this channel, e.g:#channel
    cTopic="" #The topic of this channel. e.g:"All ubuntu fans here|Obey the ops"
    cUsers=[] #A list of users(Class user()) in this channel.(Get's updated every nickchange, exit,part,join,modechange and i think that's it...)
    cTreeIter=gtk.TreeIter #The treeiter, for easy access of the channels iter.
    cTextBuffer=gtk.TextBuffer() #The TextBuffer, with all of the messages, said by users etc.
    cMsgBuffer=[] #A list of messages waiting to be sent(class msgBuffer())
    UserListStore=gtk.ListStore(str,str) #The liststore, for the users of this channel

#A user connected to a channel.
class user():
    cNick="" #Nick of the user.
    cRealName="" #Real name of the user.        
    cMode="" #The user mode of the user, ex.+,@,!,%,!@
    cUser="" #What XChat calls "user" of a user(lol), e.g: ~dom96@SpotChat-74E2DEB3.range86-131.btcentralplus.com, HOST ? appropriate name ?
    cServer="" #Usually something like: next.spotchat.org
    cTreeIter=gtk.TreeIter #The TreeIter, for easy access of the users iter.
    cTextBuffer=gtk.TextBuffer() #The TextBuffer with the conversation with this user.
    cChannel=channel() #The channel this user belongs to

#A buffer for messages in the queue which are waiting to be sent.
class msgBuffer():
    msg="" #Msg which is waiting to be sent.
    sendTimestamp=0.0 #Timestamp(Seconds since the unix epoch) when this message is mean to be sent.
    dest="" #The destination can be either a user or a channel

#Event stuff(event=string,function=def)
def connectEvent(event,function,aServer):
    global eventFunction
    evt=eventDef()
    evt.aFunc=function
    evt.eventName=event
    evt.cServer=aServer
    eventFunctions.append(evt)

class eventDef():
    aFunc=object
    cServer=server()
    eventName="" #Name of the event.

import inspect
debugInfo=True
def pDebug(txt):
    if debugInfo:
        func = str(inspect.getframeinfo(inspect.currentframe().f_back).function)
        filename = str(inspect.getframeinfo(inspect.currentframe().f_back).filename);filename = filename.split("/")[len(filename.split("/"))-1]
        print "[\033[1;34m"+str(inspect.currentframe().f_back.f_lineno).rjust(3, '0')+"\033[1;m, " + filename +"(" + func + ")]\n    " + str(txt)
    

