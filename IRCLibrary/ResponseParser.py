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
import IRC,PongStuff

#Parses response data from a server and outputs it in a nice structure.
#data=string(The response from the server), server=boolean(whether it's a server response, or a general while loop response(a user joining or a msg)
def parse(data,server, motd):
    #The response from the server after connecting
    """
    :next.SpotChat.org NOTICE AUTH :*** Looking up your hostname...\r\n
    :next.SpotChat.org NOTICE AUTH :*** Found your hostname (cached)\r\n
    :next.SpotChat.org NOTICE AUTH :*** Checking ident...\r\n
    """
    if server == True:
        if motd == True:
            return parseMOTD(data)
        else:
            return parseServer(data)    
    else:
        pass


#Parses server responses, after connecting etc.Used by parse()
def parseServer(data):
    if data[:1] == "'": #If the first char of data is a ' remove it.
        data = data[1:]
    elif data[-1:] == "'": #If the last char of data is a ' remove it.
        data = data[:-1]
    
    mList = []
    splitData = string.split(data,"\n")

    for i in splitData:
        try:
            if "NOTICE AUTH" in i:
                m = serverMsg()
                #First method of parsing, NOTICE AUTH way(command has two :)       
                
                msg=re.search("(:)[^:]*$",i).group(0)[1:]
                m.msg = msg #The message(the last : and the string after, and the [1:] to delete the :) *** Looking up your hostname...
        
                firstPart = i.replace(msg,"") #The server "next.SpotChat.org" and the code "NOTICE AUTH" ([1:] get's rid of the : )
                sFirstPart=string.split(firstPart) #Split the "server"(next.spotchat.org) and the "code"(NOTICE AUTH)
                m.server=sFirstPart[0]
                m.code = sFirstPart[1]

                mList.append(m)
            else:        
                m = serverMsg()
                #Second method of parsing, used if the command doesn't have a : when the message starts(only has : at the beggining) 
                #Well it's actually used when there is no NOTICE AUTH in the message                

                splitI = string.split(i) #Split the command with " "
                #print splitI
                if len(splitI) > 0:
                    hSplitI=0 #The position in the splitI where the message starts(-1)
                    try:
                        m.server = splitI[0] #The server, next.spotchat.org
                        m.code = splitI[1] #The code, 001
                        m.nick = splitI[2] #The nick, usually your own nick, vIRC
                        try:
                            m.channel = splitI[3]
                            hSplitI=3
                        except:
                            hSplitI=2

                        if m.code in PongStuff.numericCode():
                            hSplitI=2
                        
                    except:#If there is an exception in the above code, try this without getting the server info(i think..)
                        traceback.print_exc()
                        m.code = splitI[0]
                        m.nick = splitI[1]
                        hSplitI=1
                
                    count=0
                    for i in splitI:#Add all the parts of the message, to the m.msg
                        if count > hSplitI:
                            m.msg = m.msg + " " + i
                        count=count+1
                
                    mList.append(m)
        except:
            #traceback.print_exc()
            print "Error in parseServer. " + i
    
    #for i in mList:
        #print i.msg    


    return mList

#I'm forced to do this, the MOTD needs a seperate parser, a one that retains spaces.
def parseMOTD(data):
    if data[:1] == "'": #If the first char of data is a ' remove it.
        data = data[1:]
    elif data[-1:] == "'": #If the last char of data is a ' remove it.
        data = data[:-1]

    mList = []
    splitData = string.split(data,"\n")
    
    for i in splitData:
        try:
            m = serverMsg()
            i = i[1:]
            #print i
            for g in re.finditer("(:)[^:]+", i):#Get the last : and the text after it
                m.msg += unicode(g.group(0), 'utf-8') 

            #print m.msg            
            mList.append(m)


        except:
            #traceback.print_exc()
            print "Error in parseMOTD -):" + i

    #for i in mList:
        #print i.msg


    return mList

#Parses PRIVMSG
def parseMsg(data):
    #:ikey!~hserver@my.fancy.host PRIVMSG vIRC :VERSION
    try:
    # :dom96!~dom96@SpotChat-12E750B3.range86-131.btcentralplus.com PRIVMSG #geek :k
        splitMsg = string.split(data)
    # :dom96!~dom96@SpotChat-12E750B3.range86-131.btcentralplus.com
    # PRIVMSG
    # #geek
    # :k
        msgInt = 2
        #print splitMsg
        m = privMsg()
        m.nick = string.strip(string.split(splitMsg[0],"!")[0],":")
        m.host = string.strip(string.split(splitMsg[0],"!")[1],":")
        m.typeMsg = string.strip(splitMsg[1],":")
        try:
            m.channel = string.strip(splitMsg[2],":").replace(" ","")        
            if splitMsg[2].startswith(":"):
                msgInt = msgInt - 1

        except:        
            msgInt = msgInt - 1

        for i in range(len(splitMsg)):
            if i > msgInt:
                if i != msgInt+1:
                    m.msg += unicode(splitMsg[i], 'utf-8') + " "
                elif i == msgInt+1 and splitMsg[i].startswith(":"):
                    m.msg += unicode(splitMsg[i][1:], 'utf-8') + " "
        
        m.msg = m.msg[:-1]

        #print "In parsePrivMsg " + m.msg
    
    except:
        print "Error in parseMsg"
        traceback.print_exc()
        return False  

    return m

#Parses the user list.
def parseUsers(data,server,nChannel):
    print "parseUsers"
    #User List Started ?
    UserLstStart=False
    UserLstCmds=""
    #Parse the data returned(This should have the users and topic in it)-This has gotten pretty complicated
    splitData = string.split(data,"\r")
   # print splitData, "\n\n\n\n"
    for i in splitData:
        
        #!--Parse as Server msg--!#
        servResp = parseServer(i)
        
        #Check if the servResp isnot nothing
        if len(servResp) > 0:
            
            #!--332 Topic message--#!
            if servResp[0].code == "332":
                nChannel.cTopic = servResp[0].msg
                print "servPars: " + servResp[0].msg
            #!--332 Topic message END--#!
            #!--353 User list message--#!
            if servResp[0].code == "353":
                UserLstStart=True
                UserLstCmds += "\n" + i
            #!--353 User list message END--!#
            #!--366 User END message--!#
            if servResp[0].code == "366":
                UserLstStart=False
                #print UserLstCmds
            #!--366 User END message END--!#
        if len(servResp) > 0:
            if UserLstStart==True and servResp[0].code != "353":
                UserLstCmds += i
    
    UsersList = []
    #Now add the users to a nice tuple(list)
    splitUsers=string.split(UserLstCmds,"\n")
    #print splitUsers
    for i in splitUsers:
        indexOf = i.rfind(":") #Get the last index of :
        users=i[indexOf + 1:]
        spUsr=string.split(users)
        
        for usr in spUsr:
            UsersList.append(usr)


    return UsersList
    
def parseKick(data):
    #:dom96!~dom96@SpotChat-35F85EEE.range217-43.btcentralplus.com KICK #python dom96 :for nyx
    try:
        # :dom96!~dom96@SpotChat-35F85EEE.range217-43.btcentralplus.com KICK #python dom96 :for nyx
        splitMsg = string.split(data)
        # :dom96!~dom96@SpotChat-35F85EEE.range217-43.btcentralplus.com
        # KICK
        # #python
        # dom96
        # :for nyx
        msgInt = 2
        #print splitMsg
        m = privMsg()
        m.nick = string.strip(string.split(splitMsg[0],"!")[0],":")
        m.host = string.strip(string.split(splitMsg[0],"!")[1],":")
        m.typeMsg = string.strip(splitMsg[1],":")
        m.channel = string.strip(splitMsg[2],":").replace(" ","")
        m.nick += "," + splitMsg[3]
        
          

        for i in range(len(splitMsg)):
            if i > msgInt:
                if i != msgInt+1:
                    m.msg += unicode(splitMsg[i], 'iso8859_2') + " "
                elif i == msgInt+1 and splitMsg[i].startswith(":"):
                    m.msg += unicode(splitMsg[i][1:], 'iso8859_2') + " "


    
    except:
        traceback.print_exc()
        return False  

    return m

#Parses PRIVMSG
def parseMode(data):
        #:ChanServ!services@ArcherNet.net MODE ## +o Nyx1
    try:
        splitMsg = string.split(data)
        # :ChanServ!services@ArcherNet.net
        # MODE
        # ##
        # +o 
        # Nyx1
        msgInt = 2
        #print splitMsg
        m = privMsg()
        m.nick = string.strip(string.split(splitMsg[0],"!")[0],":")
        m.host = string.strip(string.split(splitMsg[0],"!")[1],":")
        m.typeMsg = string.strip(splitMsg[1],":")
        try:
            m.channel = string.strip(splitMsg[2],":").replace(" ","")        
            if splitMsg[2].startswith(":"):
                msgInt = msgInt - 1

        except:        
            msgInt = msgInt - 1

        for i in range(len(splitMsg)):
            if i > msgInt:
                if i != msgInt:
                    m.msg += unicode(splitMsg[i], 'iso8859_2') + " "
        
        m.msg = m.msg[:-1]
    except:
        print "Error in parseMode"
        traceback.print_exc()
        return False  

    return m


#A structure of a message(response from a server)
class serverMsg():
    server="" #the server address
    code="" #the code, for example [001,002]
    msg="" #The msg...
    nick="" #Not present in NOTICE AUTH, usually your own nick.
    channel="" #Sometimes present, the channel.

#A structure of a message(PRIVMSG)
class privMsg():
    nick=""
    host=""
    typeMsg=""
    channel=""
    msg=""






