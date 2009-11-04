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

otherStuff = object

#Connects to a server(Starts everything)
#Address=string,nick=string,realname=string,port=integer,server=server class,queue()

def connect(server):
    #License....
    print "IRCLibrary Copyright (C) 2009 Mad Dog Software"
    print "This program comes with ABSOLUTELY NO WARRANTY."
    print "This is free software, and you are welcome to redistribute it"
    print "under certain conditions; look at the license for more details."    
    #License End
    if server.cAddress.cSsl==True:
        try:
            import ssl
        except:
            pDebug("ERROR!!! NO SSL FOUND")

    #Connect to the server with a socket.
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Make a new socket
    s.settimeout(5)

    if server.cAddress.cSsl==True:
        server.cSocket = ssl.wrap_socket(s)
    else:
        server.cSocket = s

    pDebug("Connecting to:" + server.cAddress.cAddress + " on port " + str(server.cAddress.cPort))
    try:
        server.cSocket.connect((server.cAddress.cAddress, server.cAddress.cPort)) #Connect to the server
        server.connected=True
    except Exception as err:
        pDebug("\033[1;31m" + str(err) + "\033[1;m")
        #If you can't connect to the server, due to a timeout or something else..
        cycleToNextAddress(server)
        return 

    #Set the timeout to None, i.e No timeout error
    server.cSocket.settimeout(None)

    #Check for messages incoming.
    gtk.gdk.threads_enter()
    thread.start_new(pingPong,(server,))
    gtk.gdk.threads_leave()

    #Commands which are used to register the connection
    if server.cAddress.cPass !="":
        pDebug("Sending PASS")
        pDebug("\033[1;34mPASS " + server.cAddress.cPass + "\\r\\n\033[1;m")
        #Send the "PASS" command, to the server, this is the first(if there is a password) command to be sent to the server
        server.cSocket.send('PASS ' + server.cAddress.cPass + '\r\n') # PASS >pass< CR-LF

    pDebug("Sending NICK")
    pDebug("\033[1;34mNICK " + server.cNick + "\\r\\n\033[1;m")
    #Send the "NICK" command, to the server, this is the first(or second) command to be sent to the server.And last step to connect.
    server.cSocket.send('NICK ' + server.cNick + '\r\n') # NICK >nick< CR-LF

    pDebug("Sending USER")
    pDebug("\033[1;34mUSER " + server.cUsername + " " + server.cUsername + " " + server.cAddress.cAddress + " :" + server.cRealname + "\\r\\n\033[1;m")
    #Send the "USER" command, to the server, this is the second(or third) command to be sent to the server.
    # USER >username< >username< >address< :>realname< CR-LF
    server.cSocket.send("USER " + server.cUsername + " " + server.cUsername + " " + server.cAddress.cAddress + " :" + server.cRealname + "\r\n")  

    #Pings the server..
    thread.start_new(pingServer,(server,))

    #Used for sending messages, it queues messages
    #so that you don't get killed for Excess Flood
    thread.start_new(sendMsgBuffer,(server,))

def pingPong(server):

    ERROR = "" #ERROR :Closing link: (dom96@host) [Quit: MSG]

    msg = ""
    while server.connected:
        try:
            data = server.cSocket.recv(1024)
            msg += data
            if msg !="":
                pDebug("Raw received data from server:\n \033[1;32m" + data + " \033[1;m")

                #If the message ends with \n (Carriage Return) then that means that the command is a full command
                #If not then that means that the last line of msg is a uncompletely received command,
                #Which means i have to wait, for the rest of the command before parsing.
                if msg.endswith("\r\n"):
                    for i in string.split(msg,"\r\n"):
                        if i.startswith("PING"): #If the server sends a PING command...
                            pingMsg = i.replace("\n","").replace("\r","")
                            pDebug("Received PING( \033[1;32m" + pingMsg + "\033[1;m )")
                            #Reply with a PONG command, to keep the connection alive.
                            server.cSocket.send("PONG :" + pingMsg.split(":")[1] + "\r\n") 
                            pDebug("Replied to Ping with: \033[1;34m" + "PONG :" + pingMsg.split(":")[1] + "\\r\\n\033[1;m")
                            msg=""
                        elif i.startswith("ERROR"):
                            pDebug(ERROR)
                            if ERROR != "RECONNECT":
                                ERROR = i
                            else:
                                ERROR = ""
                            import IRC
                            for event in IRC.eventFunctions:
                                if event.eventName == "onServerDisconnect" and event.cServer == server:
                                    gobject.idle_add(event.aFunc, server, otherStuff, i)
                        else:
                            #!--MOTD STUFF--!#
                            PongStuff.motdStuff(server,i,otherStuff)
                            #!--PRIVMSG STUFF START--!#
                            PongStuff.privmsgResp(server,i,otherStuff)
                            #!--PART MSG--!#
                            PongStuff.partResp(server,i,otherStuff)
                            #!--JOIN MSG--!#
                            PongStuff.joinResp(server,i,otherStuff)
                            #!--QUIT MSG--!#
                            PongStuff.quitResp(server,i,otherStuff)
                            #!--USERS STUFF--!#
                            PongStuff.userStuff(server,i)
                            #!--NOTICE MSG--!#
                            PongStuff.noticeResp(server,i,otherStuff)
                            #!--KICK MSG--!#
                            PongStuff.kickResp(server,i,otherStuff)
                            #!--NICK MSG--!#
                            PongStuff.nickResp(server,i,otherStuff)
                            #!--SERVER MSG--!#
                            PongStuff.servResp(server,i,otherStuff)
                            #!--MODE MSG--!#
                            PongStuff.modeResp(server,i,otherStuff)
                            #!--PING MSG--!#
                            PongStuff.pongResp(server,i)
                            #!--TOPIC MSG--!#
                            PongStuff.topicStuff(server,i,otherStuff)
                            #!--Channel Mode Change MSG--#!
                            PongStuff.channelModeStuff(server,i,otherStuff)
                            #!--KILL MSG--#! - #If the message is
                            #KILL then it makes ERROR = "RECONNECT"
                            ERROR = PongStuff.killResp(server, i, ERROR, otherStuff)
                            #Reset the msg after parsing
                            msg=""
            else:
                pDebug(data)
                if data=="":
                    pDebug("\033[1;31mServer closed connection\033[1;m")
                    server.connected=False
                    import IRC
                    for event in IRC.eventFunctions:
                        if event.eventName == "onServerDisconnect" and event.cServer == server:
                            gobject.idle_add(event.aFunc, server, otherStuff)
                    server.cSocket.close()
                    if ERROR == "":
                        cycleToNextAddress(server)
                    else:
                        ERROR = ""


        except Exception as err:
            pDebug("\033[1;40m\033[1;33m" + str(err) + "\033[1;m\033[1;m")
            traceback.print_exc()

def cycleToNextAddress(server):
    #Reconnect to the server
    if server.connectRetries >= 2:
        #Cycle to the next server..
        for i in range(0,len(server.addresses)):
            if server.addresses[i].cAddress == server.cAddress.cAddress:
                if len(server.addresses) > i + 1:
                    pDebug(server.addresses[i+1].cAddress + server.addresses[i].cAddress)
                    server.cAddress = server.addresses[i+1]
                    break
                else:
                    #Go to the first address
                    pDebug("Cycling to the first address.")
                    server.cAddress = server.addresses[0]
                    break


        server.connectRetries = 0
        connect(server)
        return

    #Add one to connectRetries
    server.connectRetries += 1
    #Try connecting again
    connect(server)
    return 

def pingServer(server):
    while server.connected:
        import time
        if server.cMotd != None:
            server.cSocket.send("PING LAG" + str(time.time()) + "\r\n")
        time.sleep(15)

def sendMsgBuffer(server):
    while server.connected:
        import time
        time.sleep(1)
        for i in server.channels:
            if len(i.cMsgBuffer) != 0:
                for msgBuff in i.cMsgBuffer:
                    currentTime=time.time()
                    #TODO: Check the channel selected, and display only the number of messages to send on that channel
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
    def __init__(self):
        #User Stuff
        self.cNick="" #The nick that is used on this server.
        self.cRealname="" #The Real name that is being used on this server.
        self.cUsername="" #Your username
        #Server Stuff
        self.addresses=[] #The list of addresses, i.e when your unable to connect to the first server, cycle to the next one...
        self.cAddress=object #Current address(When connected)
        self.nicks=[] #List of nicks(The primary nick is the first one, the alternative nicks are the ones after)
        self.cName="" #Name of this server.
        self.cMotd=None #The MOTD Message

        self.connected=False #If this server instance is connected.
        self.connectRetries=0 #The number of times you tried connecting and it failed.
        self.cSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #The socket being used by this server.

        self.channels=[] #A List of channel(), these are all of the channels currently connected on this server.

        """Stuff which isn't really needed...Pretty much for IRCEvents.py(I should put this in something else...)"""
        self.cTextBuffer=gtk.TextBuffer() #The TextBuffer, with the server messages.
        self.listTreeStore=gtk.TreeStore #The treestore, for easy access
        self.cTreeIter=gtk.TreeIter #The treeiter, for easy access of the servers iter.

        #self.settings=object

        self.listTreeView = gtk.TreeView #TreeView with the channels and servers 
        self.UserListTreeView = gtk.TreeView #ListView with the users
        self.chatTextView = object #TextView for the chat

        self.w = object #The Window....gah this is gonna take up a shitload of memory

        self.cType="server"

#A channel connection, on a server.
class channel():
    cName="" #Name of this channel, e.g:#channel
    cMode="" #The mode of this channel, e.g: +ntr
    cTopic="" #The topic of this channel. e.g:"All ubuntu fans here|Obey the ops"
    cUsers=[] #A list of users(Class user()) in this channel.(Get's updated every nickchange, exit,part,join,modechange and i think that's it...)
    cTreeIter=gtk.TreeIter #The treeiter, for easy access of the channels iter.
    cTextBuffer=gtk.TextBuffer() #The TextBuffer, with all of the messages, said by users etc.
    cMsgBuffer=[] #A list of messages waiting to be sent(class msgBuffer())
    UserListStore=gtk.ListStore(str,str) #The liststore, for the users of this channel
    cType="channel"

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

#A class for other stuff to be passed with events...
class other():
    def __init__(self,settings,theme):
        self.settings = settings
        self.theme = theme



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
    

