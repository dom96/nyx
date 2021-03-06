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


"""I THINK THIS WHOLE FUNCTION IS OBSOLETE????"""
#Parses server responses, after connecting etc.Used by parse()
def parseServer(data):
    mList = []
    splitData = string.split(data,"\n")

    for i in splitData:
        try:
            #TODO:REMOVE?? THIS IS KIND OF OBSOLETE, since the 'NOTICE AUTH' is handled by the NOTICE Resp
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
                if len(splitI) > 0:
                    hSplitI=0 #The position in the splitI where the message starts(-1)
                    try:
                        m.server = splitI[0] #The server, next.spotchat.org
                        m.code = splitI[1] #The code, 001
                        m.nick = splitI[2] #The nick, usually your own nick, Nyx
                        try:
                            m.channel = splitI[3]
                            hSplitI=3
                        except:
                            hSplitI=2

                        if m.code in PongStuff.numericCode():
                            hSplitI=2
                    #If there is an exception in the above code, try this without getting the server info
                    except:
                        traceback.print_exc()
                        m.code = splitI[0]
                        m.nick = splitI[1]
                        hSplitI=1
                    #---------------------------------------------------Get the MSG
                    count=0
                    for i in splitI:
                        #Add all the parts of the message, to the m.msg
                        if count > hSplitI:
                            if m.msg != "":
                                m.msg = m.msg + " " + i
                            else:
                                if i[1:] == ":":
                                    m.msg = i[1:]
                                else:
                                    m.msg = i
                        count=count+1
                    #--------------------------------------------------Get the MSG END


                    #import re
                    #pDebug(data[1:])
                    #reMatch = re.search(":.+",data[1:])
                    #try:
                        #m.msg = reMatch.group(0)[1:]
                    #except:
                        #pDebug("\033[1;40m\033[1;33mNo match for the message\033[1;m\033[1;m")                
                    mList.append(m)
        except:
            #traceback.print_exc()
            pDebug("Error in parseServer. " + i)


    return mList

def parseServerRegex1(data):
    mList = []
    splitData = string.split(data,"\n")
    for i in splitData:
        m = serverMsg()

        import re
        reMatch = re.search("(^:.+?\s)(.+?\s)(.+?\s)(.+?\s)(.+)",i)

        try:
            m.server = reMatch.group(1).replace(" ","");pDebug("m.server="+m.server)
            m.code = reMatch.group(2).replace(" ","");pDebug("m.code="+m.code)
            m.nick = reMatch.group(3).replace(" ","");pDebug("m.nick="+m.nick)
            m.channel = reMatch.group(4).replace(" ","");pDebug("m.channel=" + m.channel)
            m.msg = reMatch.group(5)
            if m.msg[:1] == ":":
                m.msg = m.msg[1:]
            pDebug("m.msg=" + m.msg)
        except:
            pDebug("\033[1;40m\033[1;33mNo match for the response\033[1;m\033[1;m")
        mList.append(m)

    return mList
    
def parseServerRegex(data):
    mList = []
    splitData = string.split(data,"\n")
    for i in splitData:
        m = serverMsg()
        
        import re
        reMatch = re.search("([^:].+?\s)(.+?\s)(.+?\s)(.+)", i)
        
        try:
            m.server = reMatch.group(1).replace(" ","")#;pDebug("m.server="+m.server)
            m.code = reMatch.group(2).replace(" ","")#;pDebug("m.code="+m.code)
            m.nick = reMatch.group(3).replace(" ","")#;pDebug("m.nick="+m.nick)
            m.channel = reMatch.group(3).replace(" ","")#;pDebug("m.channel="+m.nick)
            
            m.msg = reMatch.group(4)
            if m.msg.startswith("#"): #TODO: This might cause problems for channels which don't start with # ?
                m.channel = m.msg.split(" ")[0]
                m.msg = m.msg[len(m.channel) + 1:] #+1 for the ' '(space)          
            
            if m.msg[:1] == ":":
                m.msg = m.msg[1:]
            #pDebug("m.msg=" + m.msg)
        except:
            pDebug("\033[1;40m\033[1;33mNo match for the response\033[1;m\033[1;m")
        mList.append(m)
        
    return mList



#I'm forced to do this, the MOTD needs a seperate parser, a one that retains spaces.
def parseMOTD(data):
    if data[:1] == ":": #If the first char of data is a : remove it.
        data = data[1:]

    mList = []
    splitData = string.split(data,"\n")
    
    for i in splitData:
        try:
            m = serverMsg()

            if i[:1] == ":":
                i = i[1:]
            for g in re.finditer("(:)[^:]+", i):#Get the last : and the text after it
                #m.msg += unicode(g.group(0), 'utf-8')
                #If decoding from utf-8 fails
                #Decode from iso8859, and then to utf-8
                try:
                    m.msg += g.group(0).decode("utf-8", "strict")
                except:
                    m.msg += g.group(0).decode("iso8859").encode("utf-8")


            if m.msg[:1] == ":":
                m.msg = m.msg[1:]
            #print m.msg            
            mList.append(m)


        except:
            #traceback.print_exc()
            pDebug("Error in parseMOTD -):" + i)

    #for i in mList:
        #print i.msg


    return mList

#Parses PRIVMSG
def parseMsg(data,noUnicode=False):
    #:ikey!~hserver@my.fancy.host PRIVMSG Nyx :VERSION
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
        try:
            m.nick = string.strip(string.split(splitMsg[0],"!")[0],":")
            m.host = string.strip(string.split(splitMsg[0],"!")[1],":")
        except:
            if splitMsg[0].startswith(":"):
                m.nick = splitMsg[0][1:]
            else:
                m.nick = splitMsg[0]

        m.typeMsg = string.strip(splitMsg[1],":")
        try:
            m.channel = string.strip(splitMsg[2],":").replace(" ","")        
            if splitMsg[2].startswith(":"):
                msgInt = msgInt - 1

        except:        
            msgInt = msgInt - 1

        import re
        reMatch = re.search(":.+",data[1:])
        try:
            m.msg = reMatch.group(0)[1:]

            if noUnicode == False:
                #If decoding from utf-8 fails
                #Decode from iso8859, and then to utf-8
                try:
                    m.msg = m.msg.decode("utf-8", "strict")#.encode("utf-8")
                except:
                    m.msg = m.msg.decode("iso8859").encode("utf-8")

        except:
            reMatch = re.search("(.+?)\s(.+?)\s(.+)",data[1:])
            try:
                m.msg = reMatch.group(3)

                if noUnicode == False:
                    #If decoding from utf-8 fails
                    #Decode from iso8859, and then to utf-8
                    try:
                        m.msg = m.msg.decode("utf-8", "strict")#.encode("utf-8")
                    except:
                        m.msg = m.msg.decode("iso8859").encode("utf-8")
            except:
                pDebug("\033[1;40m\033[1;33mNo match for the message\033[1;m\033[1;m")

    except:
        pDebug("\033[1;40m\033[1;33mError in parseMsg\033[1;m\033[1;m")
        import traceback;traceback.print_exc()
        return False  

    return m

#Parses the user list.
def parseUsers(data,server,nChannel):
    pDebug("parseUsers")
    #User List Started ?
    UserLstStart=False
    UserLstCmds=""
    #Parse the data returned(This should have the users and topic in it)-This has gotten pretty complicated
    splitData = string.split(data,"\n")
    print splitData, "\n\n\n\n"
    for i in splitData:
        
        #!--Parse as Server msg--!#
        servResp = parseServer(i)
        
        #Check if the servResp isnot nothing
        if len(servResp) > 0:
            
            #!--332 Topic message--#!
            if servResp[0].code == "332":
                nChannel.cTopic = servResp[0].msg
                pDebug("servPars: " + servResp[0].msg)
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

        import re
        #pDebug(data[1:])
        reMatch = re.search(":.+",data[1:])
        try:
            m.msg = reMatch.group(0)[1:]
        except:
            pDebug("\033[1;40m\033[1;33mNo match for the KICK message\033[1;m\033[1;m")
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
        if "!" in splitMsg[0]:        
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
                    #If decoding from utf-8 fails
                    #Decode from iso8859, and then to utf-8
                    try:
                        m.msg += splitMsg[i].decode("utf-8", "strict") + " "
                    except:
                        m.msg += splitMsg[i].decode("iso8859").encode("utf-8") + " "
        if m.msg[-1:] == " ":
            m.msg = m.msg[:-1]
        
    except:
        pDebug("\033[1;40m\033[1;33mError in parseMode\033[1;m\033[1;m")
        traceback.print_exc()
        return False  

    return m


#A structure of a message(response from a server)
class serverMsg():
    server="" #the server address
    code="" #the code, for example [001,002]
    msg="" #The msg...
    nick="" #usually your own nick.
    channel="" #Sometimes present, the channel.

#A structure of a message(PRIVMSG)
class privMsg():
    nick=""
    host=""
    typeMsg=""
    channel=""
    msg=""


import inspect
debugInfo=True
def pDebug(txt):
    if debugInfo:
        func = str(inspect.getframeinfo(inspect.currentframe().f_back).function)
        filename = str(inspect.getframeinfo(inspect.currentframe().f_back).filename);filename = filename.split("/")[len(filename.split("/"))-1]
        print "[\033[1;34m"+str(inspect.currentframe().f_back.f_lineno).rjust(3, '0')+"\033[1;m, " + filename +"(" + func + ")]\n    " + str(txt)



