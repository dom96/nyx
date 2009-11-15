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

"""
onMotdMsg
When a MOTD Message is received.
"""
from time import localtime, strftime
import gtk

def onMotdMsg(cResp,cServer,otherStuff):#When a MOTD message is received and parsed.
    
    for m in cResp:
        if m.msg != "":
            mSplit=m.msg.split("\n")
            for i in mSplit:
                output = otherStuff.theme.parseStyle("motd", m.nick, "", m.code, m.channel, m.msg, cServer)
                
                if output != False:
                    format_insert_text(cServer.cTextBuffer, cServer.cTextBuffer.get_end_iter(), output + "\n")
                else:
                    #Output the 'default' format(In case there isn't a style for this...)
                    format_insert_text(cServer.cTextBuffer, cServer.cTextBuffer.get_end_iter(),"30" + strftime("[%H:%M:%S]", localtime()) + "")
                    format_insert_text(cServer.cTextBuffer, cServer.cTextBuffer.get_end_iter(),"21 >28!21< ")
                    format_insert_text(cServer.cTextBuffer, cServer.cTextBuffer.get_end_iter(), m.msg + "\n")

    scrollTxtViewColorTItem(cServer, cServer, otherStuff.settings.statusTColor)

"""
onServerMsg
When a server message is received.
"""
def onServerMsg(cResp, cServer, otherStuff):#When a server msg is received and parsed.
    destTxtBuff = cServer
    for i in cResp:
        if i.channel != "":
            for ch in cServer.channels:
                if ch.cName.lower() == i.channel.lower():
                    destTxtBuff = ch
    for m in cResp:
        if m.msg != "":
            output = otherStuff.theme.parseStyle("server", m.nick, "", m.code, m.channel, m.msg, cServer)
        
            if output != False:
                format_insert_text(cServer.cTextBuffer, cServer.cTextBuffer.get_end_iter(), output + "\n")
            else:
                #Output the 'default' format(In case there isn't a style for this...)
                format_insert_text(destTxtBuff.cTextBuffer, destTxtBuff.cTextBuffer.get_end_iter(),"30" + strftime("[%H:%M:%S]", localtime()) + "")
                format_insert_text(destTxtBuff.cTextBuffer, destTxtBuff.cTextBuffer.get_end_iter(),"21 >28!21< ")
                format_insert_text(destTxtBuff.cTextBuffer, destTxtBuff.cTextBuffer.get_end_iter(), m.msg + "\n")


    scrollTxtViewColorTItem(destTxtBuff, cServer, otherStuff.settings.statusTColor)


"""
onPrivMsg
When a PRIVMSG message is received, this includes an ACTION message.(And CTCP)
"""
def onPrivMsg(cResp, cServer, otherStuff):#When a normal msg is received and parsed.
    rChannel = None    
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    if rChannel == None and cResp.channel.lower() != cServer.cNick.lower(): return    

    #If the "Channel" in the cResp is your nick, add it to the users 'channel' buffer..
    if cResp.channel.lower() == cServer.cNick.lower():
        #Get the server first, just in case i guess
        rChannel = cServer

        model, selected = cServer.listTreeView.get_selection().get_selected()
        treeiterSelected = cServer.listTreeStore.get_value(selected, 0)
        for ch in cServer.channels:
            if ch.cName.lower() == treeiterSelected.lower():
                rChannel = ch

            if ch.cName.lower() == cResp.nick.lower():
                rChannel = ch
                break
                
    colorToUse = None #The color to change the TreeIter to
    #Get the color for the nick, that sent the message
    import mIRCColors
    nickColor = mIRCColors.canonicalColor(cResp.nick)[0]
    newNickTagColor = mIRCColors.mIRCColors.get(mIRCColors.canonicalColor(cResp.nick)[0])
    newNickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=newNickTagColor)
    
    #An ACTION
    if cResp.msg.startswith("ACTION"):
        filteredMsg = cResp.msg.replace("ACTION ","").replace("","") #No ACTION in the message
        
        if cServer.cNick.encode("utf-8").lower() in filteredMsg.lower():
            output = otherStuff.theme.parseStyle("privmsgactionhighlight", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, filteredMsg, cServer, str(nickColor))
        else:
            output = otherStuff.theme.parseStyle("privmsgaction", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, filteredMsg, cServer, str(nickColor))

        if output != False:
            format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), output + "\n")
        else:
            #Fallback
            defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " "
            defaultString += "21>28!21< "
            defaultString += "" + str(nickColor) + cResp.nick + " "
            if cServer.cNick.encode("utf-8").lower() in filteredMsg.lower():
                format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), defaultString + "21" + filteredMsg + "\n")
            else:
                format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), defaultString + filteredMsg + "\n")
        
        colorToUse = otherStuff.settings.talkTColor #Set the correct color for the TreeIter
        
    #A CTCP
    elif "" in cResp.msg:
        filteredMsg = cResp.msg.replace("","")
        
        output = otherStuff.theme.parseStyle("ctcp", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, filteredMsg, cServer, str(nickColor))
        
        if output != False:
            format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), output + "\n")
        else:
            #Fallback
            defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " "
            defaultString += "21>28!21<" + " Received a CTCP " + filteredMsg + " from " + cResp.nick

            if cResp.channel.lower() == cServer.cNick.lower():
                format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), defaultString + "\n")
            else:
                format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), defaultString + " (" + cResp.channel + ")" + "\n")

        colorToUse = otherStuff.settings.statusTColor #Set the correct color for the TreeIter
        
    #A normal message
    else:

        if cResp.channel == cServer.cNick:
            """Private Message, to you."""
            #If there is not a TreeIter with this user
            if rChannel.cType == "channel":
                endMark=rChannel.cTextBuffer.get_end_iter()
                lineOffsetBAddMsg=endMark.get_line_offset()
                
                defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " "
                defaultString += "21<" + str(nickColor) + cResp.nick + "21> "
                
                #Add the message to the TextView
                msgNoMIRC = format_insert_text(rChannel.cTextBuffer, endMark, defaultString + cResp.msg + "\n")
                
            #If there is a TreeIter with this user
            elif rChannel.cType == "chanusr":
                endMark=rChannel.cTextBuffer.get_end_iter()
                lineOffsetBAddMsg=endMark.get_line_offset()
                
                #Get the style from the theme.
                output = otherStuff.theme.parseStyle("privmsguser", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, cResp.msg, cServer, str(nickColor))
                
                if output != False:
                    #Add the message to the TextView
                    msgNoMIRC = format_insert_text(rChannel.cTextBuffer, endMark, output + "\n")
                else:
                    #Fallback style
                    defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " "
                    defaultString += "" + str(nickColor) + cResp.nick + ": "

                    #Add the message to the TextView
                    msgNoMIRC = format_insert_text(rChannel.cTextBuffer, endMark, defaultString + cResp.msg + "\n")

            #Make Nyx blink in the taskbar
            if cServer.w.focused==False:
                cServer.w.set_urgency_hint(True)
            colorToUse = otherStuff.settings.highlightTColor #Set the correct color for the TreeIter
                
        else:
            """Message to the channel"""
            endMark=rChannel.cTextBuffer.get_end_iter()
            lineOffsetBAddMsg=endMark.get_line_offset()
            
            #If the nickname used is mentioned in the message, use the 'highlight' style.
            if cServer.cNick.encode("utf-8").lower() in cResp.msg.lower():
                output = otherStuff.theme.parseStyle("privmsghighlight", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, cResp.msg, cServer, str(nickColor))
            else:
                #Get the style from the theme
                output = otherStuff.theme.parseStyle("privmsg", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, cResp.msg, cServer, str(nickColor))
            
            if output != False:
                msgNoMIRC = format_insert_text(rChannel.cTextBuffer, endMark, output + "\n")
            else:
                #Add the message using the 'fallback style', when you can't retrieve the style from the theme
                defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " "
                defaultString += "" + str(nickColor) + cResp.nick + ": "
                if cServer.cNick.encode("utf-8").lower() in cResp.msg.lower():
                    msgNoMIRC = format_insert_text(rChannel.cTextBuffer, endMark, defaultString + "21" + cResp.msg + "\n")
                else:
                    msgNoMIRC = format_insert_text(rChannel.cTextBuffer, endMark, defaultString + cResp.msg + "\n")
            
            colorToUse = otherStuff.settings.talkTColor #Set the correct color for the TreeIter
        
            if cServer.cNick.encode("utf-8").lower() in cResp.msg.lower():
                if cServer.w.focused==False:
                    cServer.w.set_urgency_hint(True)
                    colorToUse = otherStuff.settings.highlightTColor #Set the correct color for the TreeIter
        
        
        applyTags(lineOffsetBAddMsg, endMark, rChannel, msgNoMIRC)#Change urls etc. into clickable links

    #Scroll the TextView and color the TreeIter in the TreeView(If that channel/user isn't selected)
    scrollTxtViewColorTItem(rChannel, cServer, colorToUse)

def applyTags(lineOffsetBAddMsg, endMark, rChannel, msgNoMIRC):
    #URLs-----------------------------------------------------
    import re
    m = re.findall("(https?://([-\w\.]+)+(:\d+)?(/([\w/_\-\.]*(\?\S+)?)?)?)", msgNoMIRC)
    if m != None:
        import pango
        for i in m:
            urlTag = rChannel.cTextBuffer.create_tag(None,underline=pango.UNDERLINE_SINGLE)
            urlTag.connect("event",urlTextTagEvent,i[0])
            endMark=rChannel.cTextBuffer.get_end_iter()
            startIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1, lineOffsetBAddMsg + msgNoMIRC.index(i[0]))
            endIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1,lineOffsetBAddMsg + (msgNoMIRC.index(i[0]) + len(i[0])))
            rChannel.cTextBuffer.apply_tag(urlTag,startIter,endIter)
    #URLs END-------------------------------------------------
    #File Paths-----------------------------------------------------
    import re
    m = re.findall("(^[/|~][A-Za-z/.0-9]+)",msgNoMIRC)

    if m != None:
        import pango
        for i in m:
            fileTag = rChannel.cTextBuffer.create_tag(None,underline=pango.UNDERLINE_SINGLE)
            fileTag.connect("event",fileTextTagEvent,i)
            endMark=rChannel.cTextBuffer.get_end_iter()
            startIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1, lineOffsetBAddMsg + msgNoMIRC.index(i))
            endIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1,lineOffsetBAddMsg + (msgNoMIRC.index(i) + len(i)))
            pDebug(str(lineOffsetBAddMsg + cResp.msg.index(i)) + "--" + str(lineOffsetBAddMsg + (msgNoMIRC.index(i) + len(i))))
            rChannel.cTextBuffer.apply_tag(fileTag,startIter,endIter)
    #File Paths END-------------------------------------------------

newTextViewMenu = []
"""URL TextTag---------------------------------------------------"""
def urlTextTagEvent(texttag,widget,event,textiter,url):
    global newTextViewMenu
    if event.type == gtk.gdk.BUTTON_PRESS:
        if event.button == 3:
            pDebug("BTN PRESS")
            seperator = gtk.SeparatorMenuItem()
            open_item = gtk.MenuItem("Open in default web browser")
            open_item.connect("activate", urlTextTagMenu_Activate,url)
            newTextViewMenu = []
            newTextViewMenu.append(seperator)
            newTextViewMenu.append(open_item)

def urlTextTagMenu_Activate(widget,url):
    import os
    if os.name != "nt":
        os.system("firefox" + " \"" + url + "\"")
    else:
        os.system(url) #TODO: ???
"""URL TextTag END-----------------------------------------------"""
"""FILE TextTag -------------------------------------------------"""
def fileTextTagEvent(texttag,widget,event,textiter,path):
    global newTextViewMenu
    if event.type == gtk.gdk.BUTTON_PRESS:
        if event.button == 3:
            pDebug("BTN PRESS")
            if len(newTextViewMenu) == 0:
                seperator = gtk.SeparatorMenuItem()
                open_item = gtk.MenuItem("Open")
                openR_item = gtk.MenuItem("Open as root")
                open_item.connect("activate", fileTextTagMenu_Activate,path)
                openR_item.connect("activate", fileTextTagMenuR_Activate,path)
                newTextViewMenu.append(seperator)
                newTextViewMenu.append(open_item)
                newTextViewMenu.append(openR_item)
#When the TextView is right clicked
#Add any other Items to the Context Menu
def TextView_populatePopup(textview,menu):
    global newTextViewMenu
    
    if len(newTextViewMenu) != 0:
        for i in newTextViewMenu:
            menu.append(i)
            i.show()
        newTextViewMenu = []

def fileTextTagMenu_Activate(widget,path):
    import os
    os.system("gnome-open " + path)

def fileTextTagMenuR_Activate(widget,path):
    import os
    os.system("gksudo 'gnome-open %s'" % path)
"""FILE TextTag END----------------------------------------------"""

"""
onJoinMsg
When a JOIN message is received.(When a user joins a channel)
"""
def onJoinMsg(cResp,cServer,otherStuff):#When a user joins a channel
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    #Get the color for the nick, that sent the message
    import mIRCColors
    nickColor = mIRCColors.canonicalColor(cResp.nick)[0]
    
    output = otherStuff.theme.parseStyle("join", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, cResp.msg, cServer, str(nickColor))

    if output != False:
        format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), output + "\n")
    else:
        defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " 28--> "
        if cResp.nick != cServer.cNick:
            defaultString += "" + str(nickColor) + cResp.nick + "19 has joined " + cResp.channel + ""
        else:
            defaultString += "19 you have joined " + cResp.channel + ""
    
        format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), defaultString + "\n")
            
    #If your the one joining select the channel TreeIter
    if cResp.nick == cServer.cNick:        
        #Expand the server TreeIter
        serverIterPath = cServer.listTreeStore.get_path(cServer.cTreeIter)
        cServer.listTreeView.expand_row(serverIterPath, False)
        #Select the channel TreeIter
        selection = cServer.listTreeView.get_selection()
        selection.select_iter(rChannel.cTreeIter)

    scrollTxtViewColorTItem(rChannel, cServer, otherStuff.settings.statusTColor)

"""
onQuitMsg
When a QUIT message is received.(When a user quits server)
"""
def onQuitMsg(cResp,cServer,otherStuff):
    #Loop through each channel's users to see if the user who quit is in the channel
    for ch in cServer.channels:
        for user in ch.cUsers:
            if cResp.nick.lower() == user.cNick.lower():
                rChannel = ch

                pDebug("Outputing QUIT in \033[1;35m" + rChannel.cName + "\033[1;m")

                #Get the color for the nick, that quit
                import mIRCColors
                nickColor = mIRCColors.canonicalColor(cResp.nick)[0]

                output = otherStuff.theme.parseStyle("quit", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, cResp.msg, cServer, str(nickColor))

                if output != False:
                    format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), output + "\n")
                else:
                    defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " 28<-- "
                    defaultString += "18" + cResp.nick + " has quit (" + cResp.msg + ")"

                    format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), defaultString + "\n")

                scrollTxtViewColorTItem(rChannel, cServer, otherStuff.settings.statusTColor)

"""
onPartMsg
When a PART message is received.(A user leaves a channel)
"""                     
def onPartMsg(cResp,cServer,otherStuff):
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    #Get the color for the nick, that sent the message
    import mIRCColors
    nickColor = mIRCColors.canonicalColor(cResp.nick)[0]
    
    output = otherStuff.theme.parseStyle("part", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, cResp.msg, cServer, str(nickColor))

    if output != False:
        format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), output + "\n")
    else:
        defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " 28<-- "
        defaultString += "18" + cResp.nick + " has left " + cResp.channel + " (" + cResp.msg + ")"

        format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), defaultString + "\n")

    if cResp.nick.lower() == cServer.cNick.lower():
        pDebug("The user who parted is you, clearing the userlist")
        rChannel.UserListStore.clear()
        rChannel.cUsers = []

    scrollTxtViewColorTItem(rChannel, cServer, otherStuff.settings.statusTColor)

"""
onNoticeMsg
When a NOTICE message is received.
"""
def onNoticeMsg(cResp, cServer, otherStuff):
    rChannel = None
    #Get the selected iter
    model, selected = cServer.listTreeView.get_selection().get_selected()
    newlySelected = cServer.listTreeStore.get_value(selected, 0)
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == newlySelected.lower():
            rChannel = ch
            
    import mIRCColors
    nickColor = mIRCColors.canonicalColor(cResp.nick)[0]
    if rChannel != None and cResp.nick != cServer.cAddress.cAddress:
        output = otherStuff.theme.parseStyle("notice", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, cResp.msg, cServer, str(nickColor))

        if output != False:
            format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), output + "\n")
        else:
            defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " "
            defaultString += "-" + str(nickColor) + cResp.nick + "- " + cResp.msg

            format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), defaultString + "\n")

        scrollTxtViewColorTItem(rChannel, cServer, otherStuff.settings.talkTColor)

    else:
        #If a channel isn't selected print the text in the server TextBuffer
        
        #If the message is NOTICE AUTH, then use the server formatting
        if cResp.nick != cServer.cAddress.cAddress:
            output = otherStuff.theme.parseStyle("notice", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, cResp.msg, cServer, str(nickColor))
        else:
            output = otherStuff.theme.parseStyle("server", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, cResp.msg, cServer, str(nickColor))

        if output != False:
            format_insert_text(cServer.cTextBuffer, cServer.cTextBuffer.get_end_iter(), output + "\n")
        else:
            #TODO: Make it look like the server message when the message is NOTICE AUTH
            defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " "
            defaultString += "-" + str(nickColor) + cResp.nick + "- " + cResp.msg

            format_insert_text(cServer.cTextBuffer, cServer.cTextBuffer.get_end_iter(), defaultString + "\n")

        scrollTxtViewColorTItem(cServer, cServer, otherStuff.settings.talkTColor)

"""
onKickMsg
When a KICK message is received.(When a operator kicks another user from a channel)
"""
def onKickMsg(cResp, cServer, otherStuff):
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    personWhoKicked = cResp.nick.split(",")[0]
    personWhoWasKicked = cResp.nick.split(",")[1]

    import mIRCColors
    nickColor = mIRCColors.canonicalColor(personWhoKicked)[0]
    nickColor1 = mIRCColors.canonicalColor(personWhoWasKicked)[0]

    output = otherStuff.theme.parseStyle("kick", personWhoKicked, cResp.host, cResp.typeMsg, cResp.channel, cResp.msg, cServer, \
    str(nickColor), personWhoWasKicked, str(nickColor1))

    if output != False:
        format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), output + "\n")
    else:
        #Fallback style
        defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " 28<-- "
        defaultString += "23" + personWhoKicked + " has kicked " + personWhoWasKicked +  " from " + cResp.channel + " (" + cResp.msg + ")"

        format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), defaultString + "\n")
    #Remove the users from the TreeView
    if cResp.nick.split(",")[1].lower() == cServer.cNick.lower():
        pDebug("The person who got kicked is you, removing all the users from the channels userlist")
        rChannel.UserListStore.clear()
        rChannel.cUsers = []

    scrollTxtViewColorTItem(rChannel, cServer, otherStuff.settings.statusTColor)

    if personWhoWasKicked == cServer.cNick:
        from IRCLibrary import IRCHelper
        IRCHelper.join(cServer,rChannel.cName,cServer.listTreeStore)
        #TODO: Maybe blink the TaskBar, and make the TreeIter color highlight

"""
onNickChange
When a NICK message is received.(When a user changes his nick or someone else(like a service) changes a users nick)
"""
def onNickChange(cResp, cServer, otherStuff):

    pDebug("OnNickChange")
    try:#If a channel isn't selected...
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            for usr in ch.cUsers:
                if usr.cNick.lower() == cResp.msg.lower():
                    rChannel = ch
        
        import mIRCColors
        nickColor = mIRCColors.canonicalColor(cResp.nick)[0]
        nickColor1 = mIRCColors.canonicalColor(cResp.msg)[0]
        
        output = otherStuff.theme.parseStyle("nick", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, cResp.msg, cServer, \
        str(nickColor), "", str(nickColor1))
        
        if output != False:
            format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), output + "\n")
        else:
            #Fallback style
            defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " 18<-- "
            defaultString += "18" + cResp.nick + " is now known as " + cResp.msg + ""

            format_insert_text(rChannel.cTextBuffer, rChannel.cTextBuffer.get_end_iter(), defaultString + "\n")
            
        scrollTxtViewColorTItem(rChannel, cServer, otherStuff.settings.statusTColor)

    except:
        import mIRCColors
        nickColor = mIRCColors.canonicalColor(cResp.nick)[0]
        nickColor1 = mIRCColors.canonicalColor(cResp.msg)[0]
        
        output = otherStuff.theme.parseStyle("nick", cResp.nick, cResp.host, cResp.typeMsg, cResp.channel, cResp.msg, cServer, \
        str(nickColor), None, str(nickColor1))
        
        if output != False:
            format_insert_text(cServer.cTextBuffer, cServer.cTextBuffer.get_end_iter(), output + "\n")
        else:
            #Fallback style
            defaultString = "30" + strftime("[%H:%M:%S]", localtime()) + " 18<-- "
            defaultString += "18" + cResp.nick + " is now known as " + cResp.msg + ""

            format_insert_text(cServer.cTextBuffer, cServer.cTextBuffer.get_end_iter(), defaultString + "\n")
            
        scrollTxtViewColorTItem(cServer, cServer, otherStuff.settings.statusTColor)

"""
onModeChange
When a user changes his/her/someones MODE 
"""
def onModeChange(cResp, cServer, otherStuff):
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.nickColor)#Blue-ish
    timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.timeColor)#Grey    
    highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.highlightColor)#Green

    mode = cResp.msg.split()[0]
    personModeChange=""
    try:
        if len(cResp.msg.split()) > 1:
            #Loop, if there is more then one users mode being changed they will all be added
            count=0
            for usr in cResp.msg.replace(cResp.msg.split()[0] + " ","").split(" "):
                if count == len(cResp.msg.replace(cResp.msg.split()[0] + " ","").split(" ")) - 2:
                    #If it's the one before the last one add a " and " to the end
                    #And check if it's not the last one...

                    personModeChange += str(usr) + " and "
                    count+=1
                else:
                    personModeChange += str(usr)
                    count+=1
                    #If this isn't the last user add a ", " after it.
                    if count != len(cResp.msg.replace(cResp.msg.split()[0] + " ","").split(" ")):
                        personModeChange += ", "

                #This should format like this, dom96 sets mode +vvvv for dom96, curtis, Nyx and Amrykid
    except:
        import traceback;traceback.print_exc()
        pDebug("\033[1;40m\033[1;33mThe cResp didn't have a person who's mode got changed(possibly)\033[1;m\033[1;m")


    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
    #>!<
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >",highlightTag)
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"!",nickTag)
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"< ",highlightTag)

    #nick
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick,nickTag)
    #"dom96 sets mode +o for dom96" - user mode change
    if personModeChange != "" and "k" not in mode and "l" not in mode:
        rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter()," sets mode " + mode + " for " + personModeChange + "\n")
    #Channel mode change
    else:
        rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter()," sets mode " + mode + " in channel " + cResp.channel + "\n")

    scrollTxtViewColorTItem(rChannel, cServer, otherStuff.settings.statusTColor)

"""
onUsersChange
When the list of users are changed(When a response to the NAMES command is received)
"""
def onUsersChange(cChannel,cServer):
    noUserIcons = False
    # * = Founder and ~ = Founder
    # ! = Admin / Protected and & = Admin
    # @ = Op
    # % = HalfOp
    # + = Voice
            
    #Clear the users in the treeview
    #itr = cChannel.UserListStore.get_iter_first()
    #while itr:
        #cChannel.UserListStore.remove(itr)
        #itr = cChannel.UserListStore.iter_next(itr)
    cChannel.UserListStore.clear()

    #Sort the users.
    owners = []
    for user in cChannel.cUsers:
        if "*" in user.cMode or "~" in user.cMode:
            pDebug("Adding " + user.cNick + " to Founders(With mode " + user.cMode + ")")
            owners.append(user.cNick)
    owners.sort(key=str.lower)              
    admins = []
    for user in cChannel.cUsers:
        if "!" in user.cMode or "&" in user.cMode:
            pDebug("Adding " + user.cNick + " to Admins(With mode " + user.cMode + " )")
            admins.append(user.cNick)
    admins.sort(key=str.lower)
    ops = []
    for user in cChannel.cUsers:
        if "@" in user.cMode:
            pDebug("Adding " + user.cNick + " to OPs(With Mode " + user.cMode + " )")
            ops.append(user.cNick)
    ops.sort(key=str.lower)
    hops = []
    for user in cChannel.cUsers:
        if "%" in user.cMode:
            pDebug("Adding " + user.cNick + " to HOPs")
            hops.append(user.cNick)
    hops.sort(key=str.lower)
    vs = []
    for user in cChannel.cUsers:
        if "+" in user.cMode:
            pDebug("Adding " + user.cNick + " to V ")
            vs.append(user.cNick)
    vs.sort(key=str.lower)
    others = []
    for user in cChannel.cUsers:
        if ("*" not in user.cMode and "!" not in user.cMode and "@" not in user.cMode and "%" not in user.cMode and
"+" not in user.cMode and "~" not in user.cMode and "&" not in user.cMode):
            pDebug("Adding " + user.cNick + " to Others(With mode " + user.cMode + ")")
            others.append(user.cNick)
    others.sort(key=str.lower)
    
    import sys
    register_iconsets([("founder", sys.path[0] + "/images/Founder.png"),("admin", sys.path[0] + "/images/Admin.png"),
    ("op", sys.path[0] + "/images/op.png"),("hop", sys.path[0] + "/images/hop.png"),("voice", sys.path[0] + "/images/voice.png")])

    pDebug(others+hops+ops+admins+owners)
    #Add the Owners, to the list of users.
    for user in owners:
        for cUsr in cChannel.cUsers:
            if cUsr.cNick == user:
                if itrContainsString(cUsr.cNick,cChannel.UserListStore.iter_children(cChannel.cTreeIter),cChannel.UserListStore) == False:
                    cUsr.cTreeIter = cChannel.UserListStore.append([user,lookupIcon("founder")])
    #Add the admins, to the list of users
    for user in admins:
        for cUsr in cChannel.cUsers:
            if cUsr.cNick == user:
                if itrContainsString(cUsr.cNick,cChannel.UserListStore.iter_children(cChannel.cTreeIter),cChannel.UserListStore) == False:
                    cUsr.cTreeIter = cChannel.UserListStore.append([user,lookupIcon("admin")])
    #Add the operators, to the list of users
    for user in ops:
        for cUsr in cChannel.cUsers:
            if cUsr.cNick == user:
                if itrContainsString(cUsr.cNick,cChannel.UserListStore.iter_children(cChannel.cTreeIter),cChannel.UserListStore) == False:
                    cUsr.cTreeIter = cChannel.UserListStore.append([user,lookupIcon("op")])
    #Add the half operators, to the list of users
    for user in hops:
        for cUsr in cChannel.cUsers:
            if cUsr.cNick == user:
                if itrContainsString(cUsr.cNick,cChannel.UserListStore.iter_children(cChannel.cTreeIter),cChannel.UserListStore) == False:
                    cUsr.cTreeIter = cChannel.UserListStore.append([user,lookupIcon("hop")])
    #Add the voices, to the list of users
    for user in vs:
        for cUsr in cChannel.cUsers:
            if cUsr.cNick == user:
                if itrContainsString(cUsr.cNick,cChannel.UserListStore.iter_children(cChannel.cTreeIter),cChannel.UserListStore) == False:
                    cUsr.cTreeIter = cChannel.UserListStore.append([user,lookupIcon("voice")])
    #Add the rest, to the list of users
    for user in others:
        for cUsr in cChannel.cUsers:
            if cUsr.cNick == user:
                if itrContainsString(cUsr.cNick,cChannel.UserListStore.iter_children(cChannel.cTreeIter),cChannel.UserListStore) == False:
                    cUsr.cTreeIter = cChannel.UserListStore.append([user,None])



def itrContainsString(string,itr,treestore):
    try:
        while itr:
            if treestore.get_value(itr, 0) == string:
                return True
            itr = treestore.iter_next(itr)

        return False
    except:
        return True
        traceback.print_exc()

def register_iconsets(icon_info):
    iconfactory = gtk.IconFactory()
    stock_ids = gtk.stock_list_ids()
    for stock_id, file in icon_info:
        # only load image files when our stock_id is not present
        if stock_id not in stock_ids:
            pixbuf = gtk.gdk.pixbuf_new_from_file(file)
            iconset = gtk.IconSet(pixbuf)
            iconfactory.add(stock_id, iconset)
        iconfactory.add_default()

#Looks up an icon in the stock list
def lookupIcon(icon):
    try:
        stock_ids = gtk.stock_list_ids()
        for stock in stock_ids:
            if stock == icon:
                return stock
    except:
        pDebug("Error Looking up icon")
        return None

"""
onUserJoin
When a user joins a channel, provides the user and the index of where to add the user
"""
def onUserJoin(cChannel,cServer,cIndex,cUsr):
    if cUsr.cMode == "":
        try:
            cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,None])
        except:
            import traceback;traceback.print_exc()
    else:
        pDebug("onUserJoin, " + cUsr.cMode)
        if "*" in cUsr.cMode or "~" in cUsr.cMode:
            pDebug("*"+str(cIndex))
            cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,lookupIcon("founder")])
            return
        elif "!" in cUsr.cMode or "&" in cUsr.cMode:
            pDebug("!"+str(cIndex))
            cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,lookupIcon("admin")])
            return
        elif "@" in cUsr.cMode:
            pDebug("@"+str(cIndex))
            cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,lookupIcon("op")])
            return
        elif "%" in cUsr.cMode:
            pDebug("%"+str(cIndex))
            cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,lookupIcon("hop")])

            return
        elif "+" in cUsr.cMode:
            pDebug("+"+str(cIndex))
            #if noUserIcons==False:
            try:
                cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,lookupIcon("voice")])
            except:
                import traceback;traceback.print_exc()
            return

"""
onUserRemove
When a user either QUIT's ,PART's(from a channel) or is KICKed, provides the iter to remove
"""
def onUserRemove(cChannel,cServer,cTreeIter,usr):
    if usr != None:
        cChannel.cUsers.remove(usr)
    else:
        pDebug("\033[1;31mAn error occured while trying to remove user from the user list, received " + str(usr) + " onUserRemove\033[1;m")

    try:
        cChannel.UserListStore.remove(cTreeIter)
        pDebug("\033[1;32mSuccesfully removed %s\033[1;m" % (str(cTreeIter)))
    except:
        pDebug("\033[1;31mError removing user from TreeStore, onUserRemove\033[1;m")
        import traceback;traceback.print_exc()

"""
onUserOrderUpdate
When a users order(index) is updated.(For example mode change or nick change)
"""
def onUserOrderUpdate(cChannel, cServer, cIndex, cUsr):
    from IRCLibrary import PongStuff
    pDebug(cUsr.cNick)

    if cIndex == 0:
        cChannel.UserListStore.move_before(cUsr.cTreeIter, cChannel.UserListStore.get_iter(cIndex))
    else:
        cChannel.UserListStore.move_after(cUsr.cTreeIter, cChannel.UserListStore.get_iter(cIndex - 1))

    if cUsr.cMode == "":
        pDebug(cIndex)
        cChannel.UserListStore.set_value(cUsr.cTreeIter, 1, None)
    else:
        r = False
        if "*" in cUsr.cMode or "~" in cUsr.cMode:
            pDebug("*"+str(cIndex))
            cChannel.UserListStore.set_value(cUsr.cTreeIter, 1, lookupIcon("founder"))
            r = True
        elif "!" in cUsr.cMode or "&" in cUsr.cMode and r == False: # If r is True then the icon has already been set
            pDebug("!"+str(cIndex))
            cChannel.UserListStore.set_value(cUsr.cTreeIter, 1, lookupIcon("admin"))
            r = True
        elif "@" in cUsr.cMode and r == False: # If r is True then the icon has already been set
            pDebug("@"+str(cIndex))
            cChannel.UserListStore.set_value(cUsr.cTreeIter, 1, lookupIcon("op"))
            r = True
        elif "%" in cUsr.cMode and r == False: # If r is True then the icon has already been set
            pDebug("%"+str(cIndex))
            cChannel.UserListStore.set_value(cUsr.cTreeIter, 1, lookupIcon("hop"))
            r = True
        elif "+" in cUsr.cMode and r == False: # If r is True then the icon has already been set
            pDebug("+"+str(cIndex))
            cChannel.UserListStore.set_value(cUsr.cTreeIter, 1, lookupIcon("voice"))
            r = True



"""
onTopicChange
When a channels topic changes
"""
def onTopicChange(cResp, cServer, otherStuff):
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    try:
        cResp.typeMsg = cResp.code
    except:
        pDebug("\033[1;40m\033[1;33mMaking cResp.typeMsg = cResp.code failed\033[1;m\033[1;m") 

    #The text in TopicTextBox get's set in MainForm.py

    nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.nickColor)#Blue-ish
    timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.timeColor)#Grey    
    highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.highlightColor)#Red

    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
    #>!<
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >",highlightTag)
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"!",nickTag)
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"< ",highlightTag)
   
    #Code 333 is the time when the topic was last changed.
    if cResp.typeMsg != "333":
        if cResp.nick != cServer.cNick:
            rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " has changed the topic on " + cResp.channel + " to: " + cResp.msg + "\n")
        else:
            rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter(),"Topic on " + cResp.channel + " is: " + cResp.msg + "\n")
    else:
        import time
        t = time.strftime("%a, %d %b %Y %H:%M:%S %Z",time.gmtime(int(cResp.msg.split(" ")[1])))
        rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter(),"Topic on " + cResp.channel + " was set by " + cResp.msg.split(" ")[0] + " on " + t + "\n")

    scrollTxtViewColorTItem(rChannel, cServer, otherStuff.settings.statusTColor)

"""
onChannelModeChange
When a channels mode changes.
"""
def onChannelModeChange(cResp, cServer, otherStuff):
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    pDebug(cResp.code)

    nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.nickColor)#Blue-ish
    timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.timeColor)#Grey    
    highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.highlightColor)#Red

    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
    #>!<
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >",highlightTag)
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"!",nickTag)
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"< ",highlightTag)

    if cResp.code == "324":
        if cResp.nick != cServer.cNick:
            rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " has changed the mode on " + cResp.channel + " to: " + cResp.msg + "\n")
        else:
            rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter(),"Mode on " + cResp.channel + " is: " + cResp.msg + "\n")
    elif cResp.code == "329" and cResp.nick == cServer.cNick:
        import time
        t = time.strftime("%a, %d %b %Y %H:%M:%S %Z",time.gmtime(int(cResp.msg)))
        rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter(),"Channel " + cResp.channel + " was created on " + t + "\n")

    scrollTxtViewColorTItem(rChannel, cServer, otherStuff.settings.statusTColor)

"""
onServerDisconnect
When the client is disconnected from the server or when a 'ERROR' message is received.
"""
def onServerDisconnect(cServer, otherStuff, error=""):
    #Get the textbuffer for each channel
    for ch in cServer.channels:
        nickTag = ch.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.nickColor)#Blue-ish
        timeTag = ch.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.timeColor)#Grey    
        highlightTag = ch.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.highlightColor)#Red


        ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
        if error == "":
            #!!!
            ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter()," !",highlightTag)
            ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(),"!",nickTag)
            ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(),"! ",highlightTag)
            ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(), "Connection to server lost!\n",highlightTag)
        else:
            ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter()," >",highlightTag)
            ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(),"!",nickTag)
            ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(),"< ",highlightTag)
            ch.cTextBuffer.insert(ch.cTextBuffer.get_end_iter(), error.replace("ERROR :","") + "\n")

        scrollTxtViewColorTItem(ch, cServer, otherStuff.settings.statusTColor)

    nickTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.nickColor)#Blue-ish
    timeTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.timeColor)#Grey    
    highlightTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.highlightColor)#Red
    cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
    if error == "":
        #!!!
        cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter()," !",highlightTag)
        cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),"!",nickTag)
        cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),"! ",highlightTag)
        cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(), "Connection to server lost!\n",highlightTag)
    else:
        cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter()," >",highlightTag)
        cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),"!",nickTag)
        cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),"< ",highlightTag)
        cServer.cTextBuffer.insert(cServer.cTextBuffer.get_end_iter(), error.replace("ERROR :","") + "\n")

    scrollTxtViewColorTItem(cServer, cServer, otherStuff.settings.statusTColor)

"""
onKillMsg
When a kill message is received.
"""
def onKillMsg(cResp, cServer, otherStuff):
    #Get the textbuffer for each channel
    for ch in cServer.channels:
        nickTag = ch.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.nickColor)#Blue-ish
        timeTag = ch.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.timeColor)#Grey    
        highlightTag = ch.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.highlightColor)#Red


        ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
        ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(), " >",highlightTag)
        ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(), "!",nickTag)
        ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(), "< ",highlightTag)
        ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(), cResp.nick + " has disconnected/killed you from the server\n",highlightTag)

        scrollTxtViewColorTItem(ch, cServer, otherStuff.settings.statusTColor)

    nickTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.nickColor)#Blue-ish
    timeTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.timeColor)#Grey    
    highlightTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=otherStuff.settings.highlightColor)#Red
    cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)

    cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter()," >",highlightTag)
    cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),"!",nickTag)
    cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),"< ",highlightTag)
    cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(), cResp.nick + " has disconnected/killed you from the server\n",highlightTag)

    scrollTxtViewColorTItem(cServer, cServer, otherStuff.settings.statusTColor)



#!--IRC EVENTS END--!#
"""
Scrolls the textView and colors the TreeView item
"""
def scrollTxtViewColorTItem(ch, cServer, color):
    #Get the selected iter
    model, selected = cServer.listTreeView.get_selection().get_selected()
    newlySelected = cServer.listTreeStore.get_value(selected, 0)
    #Check to see if this channel is selected, and scroll the TextView if it is.
    #If i don't do this the TextView will scroll even when you have another channel/server selected
    #which is a bit annoying
    from IRCLibrary import IRC
    if ch.cType == "channel" or ch.cType == "chanusr":
        if newlySelected == ch.cName:
            #Scroll the TextView to the bottom...                                   
            endMark = ch.cTextBuffer.create_mark(None, ch.cTextBuffer.get_end_iter(), True)
            cServer.chatTextView.scroll_to_mark(endMark, 0)
        elif color != None and newlySelected != ch.cName:
            cServer.listTreeStore.set_value(ch.cTreeIter, 2, color) #Set the channels this message was sent to, TreeIter color.
    elif ch.cType == "server":
        if newlySelected.lower() == ch.cName.lower():
            #Scroll the TextView to the bottom...                                   
            endMark = ch.cTextBuffer.create_mark(None, ch.cTextBuffer.get_end_iter(), True)
            cServer.chatTextView.scroll_to_mark(endMark, 0)
        elif color != None and newlySelected != ch.cName:
            cServer.listTreeStore.set_value(ch.cTreeIter, 2, color) #Set the channels this message was sent to, TreeIter color.

"""
Formats text into mIRC colors(also bold and italics) and also (TODO) HTML Colors(Like conspire does it)
returns the text with no mIRC crap in it
"""
def format_insert_text(TextBuffer, textIter, text):

    newText = text.replace("\n","").replace("\r","")
    endMark=textIter
    lineOffsetBAddMsg=endMark.get_line_offset()
    import re
    import mIRCParser
    #txtNoMIrcStuff = re.sub("\x03(\d+(,\d+|\d+)|)","",text).replace("\x02","").replace("","").replace("","")
    txtNoMIrcStuff = mIRCParser.removeFormatting(text)

    #pDebug(txtNoMIrcStuff)
    TextBuffer.insert(textIter, txtNoMIrcStuff)

    m = mIRCParser.parse(newText)
    #pDebug(m)
    if len(m) != 0:
        for i in m:
            #pDebug(i)
            #Colors
            if i[2].startswith("\x03"):
                #Check if it's a Hex color or a mIRC color
                if i[2][1:].startswith("#"):
                    #TODO:Hex colors
                    pass
                else:
                    #mIRC Colors
                    try:
                        match = re.search("\x03((\d+|)(,\d+|\d+)|)", i[2])
                        if "," not in match.group(0):
                            mIRCTxtColor = match.group(0).replace("\x03", "")
                            if len(mIRCTxtColor) > 2: mIRCTxtColor = mIRCTxtColor[:2]
                            import mIRCColors
                            mIRCGdkColor = mIRCColors.mIRCColors.get(int(mIRCTxtColor))
                            textTag = TextBuffer.create_tag(None,foreground_gdk=mIRCGdkColor)
                        else:
                            fg, bg = match.group(0).replace("\x03","").split(",")
                            import mIRCColors
                            fgC, bgC = None, None
                            if fg != '':
                                fgC = mIRCColors.mIRCColors.get(int(fg))
                            if bg != '':
                                bgC = mIRCColors.mIRCColors.get(int(bg))

                            textTag = TextBuffer.create_tag(None, foreground_gdk=fgC, background_gdk=bgC)
                    except:
                        import traceback;traceback.print_exc()
                        pDebug("Error getting mIRC color.." + mIRCTxtColor + " " + i[2])
                        return
            #Colors END
            #Bold
            if i[2].startswith("\x02"):
                import pango
                textTag = TextBuffer.create_tag(None, weight=pango.WEIGHT_BOLD)
            #Underline
            if i[2].startswith(""):
                import pango
                textTag = TextBuffer.create_tag(None, underline=pango.UNDERLINE_SINGLE)
                
            endMark=TextBuffer.get_end_iter()

            if text.endswith("\n"):
                startIter=TextBuffer.get_iter_at_line_offset(endMark.get_line() - 1, lineOffsetBAddMsg + i[0])
            else:
                startIter=TextBuffer.get_iter_at_line_offset(endMark.get_line(), lineOffsetBAddMsg + i[0])

            if text.endswith("\n"):
                endIter=TextBuffer.get_iter_at_line_offset(endMark.get_line() - 1, lineOffsetBAddMsg + i[1])
            else:
                endIter=TextBuffer.get_iter_at_line_offset(endMark.get_line(), lineOffsetBAddMsg + i[1])
            TextBuffer.apply_tag(textTag, startIter, endIter)
            
    return txtNoMIrcStuff


import inspect
debugInfo=True
def pDebug(txt):
    if debugInfo:
        func = str(inspect.getframeinfo(inspect.currentframe().f_back).function)
        filename = str(inspect.getframeinfo(inspect.currentframe().f_back).filename);filename = filename.split("/")[len(filename.split("/"))-1]
        print "[\033[1;34m"+str(inspect.currentframe().f_back.f_lineno).rjust(3, '0')+"\033[1;m, " + filename +"(" + func + ")]\n    " + str(txt)
