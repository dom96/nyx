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
    print "Connecting to:" + address
    server.cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Make a new socket
    server.cSocket.connect((address, port)) #Connect to the server
    data = server.cSocket.recv(1024) #Receive the response
    print data
    datParsed = ResponseParser.parse(data,True,False)
    for event in eventFunctions:
        if event.eventName == "onServerMsg" and event.cServer == server:
            event.aFunc(datParsed,server)
    print "Sending NICK"
    #Send the "NICK" command, to the server, this is the third command to be sent to the server.And last step to connect.
    server.cSocket.send('NICK ' + nick + ' \r\n') # NICK >nick< CR-LF
    #Don't wait for responses to the NICK command

    print "Sending USER"
    #Send the "USER" command, to the server, this is the second command to be sent to the server.
    server.cSocket.send("USER " + nick + " " + nick + " " + address + " :" + realname + "\r\n") # USER >nick< >nick< >address< :>realname< CR-LF 
    #server.cSocket.send("USER %s %s %s :%s \r\n" %
              #(nick, "8", "*", realname))
    data = server.cSocket.recv(1024) #Receive the response
    print data
    datParsed = ResponseParser.parse(data,True,False)
    for event in eventFunctions:
        if event.eventName == "onServerMsg" and event.cServer == server:
            event.aFunc(datParsed,server)



    #Add all the info of the server.
    server.cAddress = address
    server.cNick = nick
    server.cRealname = realname
    server.cPort = port
    server.cName = address
    
    #Start the while loop, in another thread, so that i can return the server.
    gtk.gdk.threads_enter()
    thread.start_new(pingPong,(server,))
    gtk.gdk.threads_leave()

    
    #queue.put(server)
    #return server

def pingPong(server):
    MOTDStarted = False
    MOTD=""

    UsersStarted = False
    USERS=""
    while(True):
        try:
            data = server.cSocket.recv(4096)
            msg = data
            if msg !="":
                print "Raw received data from server:" + msg
                if msg.startswith("PING"): #If the server sends a PING command...
                    print "Received PING( " + msg + " ), Replying with PONG \n"
                    server.cSocket.send("PONG " + msg.split(":")[1] + " \n") #Reply with a PONG command, to keep the connection alive.
                    print "Replied to Ping with: " + "PONG " + msg.split(":")[1] + " \n"
                else:
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

      
        except:
            traceback.print_exc()   



#A connection to a server
class server():
    cAddress="" #The address of this server.
    cNick="" #The nick that is used on this server.
    cRealname="" #The Real name that is being used on this server.
    cPort=0 #The port being used, on this server.
    cName="" #Name of this server.
    cSocket=socket.socket(socket.AF_INET, socket.SOCK_STREAM) #The socket being used by this server.
    cTextBuffer=gtk.TextBuffer() #The TextBuffer, with the server messages.
    channels=[] #A tuple(List) of channel(), these are all of the channels currently connected on his server.
    listTreeStore=gtk.TreeStore #The treestore, for easy access

#A channel connection, on a server.
class channel():
    cName="" #Name of this channel, e.g:#channel
    cTopic="" #The topic of this channel. e.g:"All ubuntu fans here|Obey the ops"
    cUsers=[] #A tuple(list) of users(Class user()) in this channel.(Get's updated every nickchange, exit,part,join,modechange and i think that's it...)
    cTreeIter=gtk.TreeIter #The treeiter, for easy access of the channels iter.
    cTextBuffer=gtk.TextBuffer() #The TextBuffer, with all of the messages, said by users etc.
    
#A user connected to a channel.
class user():
    cNick="" #Nick of the user.
    cRealName="" #Real name of the user.        
    cMode="" #The user mode of the user, ex.+,@,!,%,!@
    cUser="" #What XChat calls "user" of a user(lol), e.g: ~dom96@SpotChat-74E2DEB3.range86-131.btcentralplus.com, HOST ? appropriate name ?
    cServer="" #Usually something like: next.spotchat.org
    cTreeIter=gtk.TreeIter #The TreeIter, for easy access of the users iter.

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
    

