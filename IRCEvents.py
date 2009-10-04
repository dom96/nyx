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
"""
onMotdMsg
When a MOTD Message is received.
"""
from time import localtime, strftime
import gtk

def onMotdMsg(cResp,cServer):#When a MOTD message is received and parsed.
    pDebug("onMotdMsg")
    nickTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
    timeTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey 
    highlightTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.highlightColor)#Red
    motdTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.motdColor)#Greyish

    for m in cResp:
        if m.msg != "":
            mSplit=m.msg.split("\n")
            for i in mSplit:
                cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
                cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter()," >",highlightTag)
                cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),"!",nickTag)
                cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),"< ",highlightTag)
                cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),m.msg + "\n",motdTag)
                pDebug("\033[1;35m" + i + "\033[1;m")

    scrollTxtViewColorTItem(cServer, cServer, cServer.settings.statusTColor)

"""
onServerMsg
When a server message is received.
"""
def onServerMsg(cResp,cServer):#When a server msg is received and parsed.
    destTxtBuff = cServer
    for i in cResp:
        if i.channel != "":
            for ch in cServer.channels:
                if ch.cName.lower() == i.channel.lower():
                    destTxtBuff = ch


    serverMsgTag = destTxtBuff.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.serverColor)#Orange
    nickTag = destTxtBuff.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
    timeTag = destTxtBuff.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey 
    highlightTag = destTxtBuff.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.highlightColor)#Red

    for m in cResp:
        if m.msg != "":
            destTxtBuff.cTextBuffer.insert_with_tags(destTxtBuff.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
            destTxtBuff.cTextBuffer.insert_with_tags(destTxtBuff.cTextBuffer.get_end_iter()," >",highlightTag)
            destTxtBuff.cTextBuffer.insert_with_tags(destTxtBuff.cTextBuffer.get_end_iter(),"!",nickTag)
            destTxtBuff.cTextBuffer.insert_with_tags(destTxtBuff.cTextBuffer.get_end_iter(),"< ",highlightTag)
            destTxtBuff.cTextBuffer.insert_with_tags(destTxtBuff.cTextBuffer.get_end_iter(),m.msg + "\n",serverMsgTag)

    """---------------------"""
    #This is if the serverMsg is for a server
    try:
        change=True
        try:
            if type(destTxtBuff.cAddress) ==  str:
                change=True
        except:
            change=False

        if change==True:
            destTxtBuff.cName=destTxtBuff.cAddress
    except:
        pDebug("\033[1;40m\033[1;33mMaking destTxtBuff.cName=destTxtBuff.cAddress failed.\033[1;m\033[1;m")
    """----------------------"""
    scrollTxtViewColorTItem(destTxtBuff, cServer, cServer.settings.statusTColor)


"""
onPrivMsg
When a PRIVMSG message is received, this includes an ACTION message.(And CTCP)
"""
def onPrivMsg(cResp,cServer):#When a normal msg is received and parsed.
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    #If the "Channel" in the cResp is your nick, add it to the users 'channel' buffer..
    if cResp.channel.lower() == cServer.cNick.lower():
        """For NICKS, which are EXEMPT from creating a new 'channel' for them."""
        #Get the server first, this way.....umm for when i have nicks which aren't suppose to have their own 'channels'
        rChannel = cServer
        #Get the selected iter(FOR NICKS WITH AN EXCEPTION(NickServ, ChanServ etc)
        #TODO So far that's not implemented<<<(The exception users)
        model, selected = cServer.listTreeView.get_selection().get_selected()
        treeiterSelected = cServer.listTreeStore.get_value(selected, 0)
        for ch in cServer.channels:
            if ch.cName.lower() == treeiterSelected.lower():
                rChannel = ch
            """For NICKS END!"""
            if ch.cName.lower() == cResp.nick.lower():
                rChannel = ch
                break

    nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
    timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey 
    highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.highlightColor)#Red    

    colorToUse = None #The color to change the TreeIter to
    #Get the color for the nick, that sent the message
    import mIRCColors
    newNickTagColor = mIRCColors.mIRCColors.get(mIRCColors.canonicalColor(cResp.nick)[0])
    newNickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=newNickTagColor)

    if "ACTION" in cResp.msg:
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >",highlightTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"!",nickTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"<",highlightTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," " + cResp.nick,newNickTag)
        rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter(),cResp.msg.replace("ACTION","").replace("","") + "\n")
        colorToUse = cServer.settings.talkTColor #Set the correct color for the TreeIter
    elif "" in cResp.msg:
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >",highlightTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"!",nickTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"<",highlightTag)
        rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter()," Received CTCP " + cResp.msg.replace("","") + " from " + cResp.nick + "\n")
        pDebug(rChannel)
        colorToUse = cServer.settings.statusTColor #Set the correct color for the TreeIter
    else:
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)

        #If it's a Private Message to you, not the channel.
        if cResp.channel == cServer.cNick:
            #If there is not a TreeIter with this user
            if rChannel.cName.startswith("#"):
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," =",highlightTag)
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick,nickTag)
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"= ",highlightTag)
                colorToUse = cServer.settings.talkTColor #Set the correct color for the TreeIter
            #If there is a TreeIter with this user
            else:
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," " + cResp.nick + ": ",newNickTag)
                colorToUse = cServer.settings.talkTColor #Set the correct color for the TreeIter

            #Make Nyx blink in the taskbar
            if cServer.w.focused==False:
                cServer.w.set_urgency_hint(True)
                colorToUse = cServer.settings.highlightTColor #Set the correct color for the TreeIter
        #If it's a message to the channel
        else:
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," " + cResp.nick + ": ",newNickTag)
            colorToUse = cServer.settings.talkTColor #Set the correct color for the TreeIter

        #Make a tag for the message
        msgTag = rChannel.cTextBuffer.create_tag(None)
        if cServer.cNick.lower() in cResp.msg.lower():
            msgTag.set_property("foreground-gdk",cServer.settings.highlightColor)
            if cServer.w.focused==False:
                cServer.w.set_urgency_hint(True)
                colorToUse = cServer.settings.highlightTColor #Set the correct color for the TreeIter
        #URLs-----------------------------------------------------
        import re
        m = re.findall("(https?://([-\w\.]+)+(:\d+)?(/([\w/_\-\.]*(\?\S+)?)?)?)",cResp.msg)
        endMark=rChannel.cTextBuffer.get_end_iter()
        lineOffsetBAddMsg=endMark.get_line_offset()
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.msg + "\n",msgTag)
        if m != None:
            import pango
            for i in m:
                urlTag = rChannel.cTextBuffer.create_tag(None,underline=pango.UNDERLINE_SINGLE)
                urlTag.connect("event",urlTextTagEvent,i[0])
                endMark=rChannel.cTextBuffer.get_end_iter()
                startIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1, lineOffsetBAddMsg + cResp.msg.index(i[0]))
                endIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1,lineOffsetBAddMsg + (cResp.msg.index(i[0]) + len(i[0])))
                rChannel.cTextBuffer.apply_tag(urlTag,startIter,endIter)
        #URLs END-------------------------------------------------
        #File Paths-----------------------------------------------------
        import re
        m = re.findall("(^[/|~][A-Za-z/.0-9]+)",cResp.msg)

        if m != None:
            import pango
            for i in m:
                fileTag = rChannel.cTextBuffer.create_tag(None,underline=pango.UNDERLINE_SINGLE)
                fileTag.connect("event",fileTextTagEvent,i)
                endMark=rChannel.cTextBuffer.get_end_iter()
                startIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1, lineOffsetBAddMsg + cResp.msg.index(i))
                endIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1,lineOffsetBAddMsg + (cResp.msg.index(i) + len(i)))
                pDebug(str(lineOffsetBAddMsg + cResp.msg.index(i)) + "--" + str(lineOffsetBAddMsg + (cResp.msg.index(i) + len(i))))
                rChannel.cTextBuffer.apply_tag(fileTag,startIter,endIter)
        #File Paths END-------------------------------------------------


    """---------------------
    #This is just for when a user PM's you...
    try:
        change=True
        try:
            if type(rChannel.cAddress) ==  str:
                change=False
        except:
            change=True

        if change==True:
            rChannel.cName=rChannel.cNick 
    except:
        pDebug("\033[1;40m\033[1;33mMaking rChannel.cName=rChannel.cNick failed.\033[1;m\033[1;m")
    ----------------------"""
    pDebug("About to scroll, PRIVMSG")
    scrollTxtViewColorTItem(rChannel, cServer, colorToUse)

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
        os.system(url)
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

def TextView_populatePopup(textview,menu):
    global newTextViewMenu
    pDebug("TextView_populatePopup")
    pDebug(newTextViewMenu)
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
def onJoinMsg(cResp,cServer):#When a user joins a channel
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        pDebug(ch.cName + cResp.channel)
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
    timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey    
    successTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.joinColor)#Green

    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," -->" + " ",nickTag)
    #If your NOT the one joining 
    if cResp.nick != cServer.cNick:
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " has joined " + cResp.channel + "\n",successTag)
    #If your the one joining        
    else:
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"You have joined " + cResp.channel + "\n",successTag)
        #Expand the server TreeIter
        serverIterPath = cServer.listTreeStore.get_path(cServer.cTreeIter)
        cServer.listTreeView.expand_row(serverIterPath,False)
        #Select the channel TreeIter
        selection = cServer.listTreeView.get_selection()
        selection.select_iter(rChannel.cTreeIter)

    scrollTxtViewColorTItem(rChannel, cServer, cServer.settings.statusTColor)

"""
onQuitMsg
When a QUIT message is received.(When a user quits server)
"""
def onQuitMsg(cResp,cServer):
    #Loop through each channel's users to see if the user who quit is in the channel
    for ch in cServer.channels:
        for user in ch.cUsers:
            if cResp.nick.lower() == user.cNick.lower():
                rChannel = ch

                pDebug("Found channel: \033[1;35m" + rChannel.cName + "\033[1;m")

                nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
                timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey    
                partTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.partColor)#Green

                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," <--" + " ",nickTag)
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " has quit " + rChannel.cName + " (" + cResp.msg + ")" + "\n",partTag)

                scrollTxtViewColorTItem(rChannel, cServer, cServer.settings.statusTColor)

"""
onPartMsg
When a PART message is received.(A user leaves a channel)
"""                     
def onPartMsg(cResp,cServer):
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
    timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey    
    partTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.partColor)#Green

    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," <--" + " ",nickTag)
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " has left " + cResp.channel + " (" + cResp.msg + ")" + "\n",partTag)

    if cResp.nick.lower() == cServer.cNick.lower():
        pDebug("The user who parted is you, removing all the users...")
        for usr in rChannel.cUsers:
            rChannel.UserListStore.remove(usr.cTreeIter)
        rChannel.cUsers = []

    scrollTxtViewColorTItem(rChannel, cServer, cServer.settings.statusTColor)

"""
onNoticeMsg
When a NOTICE message is received.
"""
def onNoticeMsg(cResp,cServer):
    try:
        #Get the selected iter
        model, selected = cServer.listTreeView.get_selection().get_selected()
        newlySelected = cServer.listTreeStore.get_value(selected, 0)
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            if ch.cName.lower() == newlySelected.lower():
                rChannel = ch

        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey    
        highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.highlightColor)#red

        import mIRCColors
        newNickTagColor = mIRCColors.mIRCColors.get(mIRCColors.canonicalColor(cResp.nick)[0])
        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=newNickTagColor)

        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >",highlightTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick,nickTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"<" + " ",highlightTag)
        rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter(),cResp.msg + "\n")

        scrollTxtViewColorTItem(rChannel, cServer, cServer.settings.talkTColor)

    except:#If a channel isn't selected print the text in the server TextBuffer
        cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),"timeTag")
        cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter()," >","highlightTag")
        cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),cResp.nick,"nickTag")  
        cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),"<" + " ","highlightTag")   
        cServer.cTextBuffer.insert(cServer.cTextBuffer.get_end_iter(),cResp.msg + "\n")

        scrollTxtViewColorTItem(cServer, cServer, cServer.settings.talkTColor)

"""
onKickMsg
When a KICK message is received.(When a operator kicks another user from a channel)
"""
def onKickMsg(cResp,cServer):
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
    timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey    
    highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.highlightColor)#Green

    personWhoKicked = cResp.nick.split(",")[0]
    personWhoWasKicked = cResp.nick.split(",")[1]

    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," <-- ",highlightTag)
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),personWhoKicked,nickTag)
    rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," has kicked " + personWhoWasKicked + "(" + cResp.msg + ")\n",highlightTag)

    #Remove the users from the TreeView
    if cResp.nick.split(",")[1].lower() == cServer.cNick.lower():
        pDebug("The person who got kicked is you, removing all the users from the channels userlist")
        for usr in rChannel.cUsers:
            rChannel.UserListStore.remove(usr.cTreeIter)
        rChannel.cUsers = []

    scrollTxtViewColorTItem(rChannel, cServer, cServer.settings.statusTColor)

    if personWhoWasKicked == cServer.cNick:
        from IRCLibrary import IRCHelper
        IRCHelper.join(cServer,rChannel.cName,cServer.listTreeStore)
        #TODO:Maybe blink the TaskBar, and make the TreeIter color highlight

"""
onNickChange
When a NICK message is received.(When a user changes his nick or someone else(like a service) changes a users nick)
"""
def onNickChange(cResp,cServer):

    pDebug("OnNickChange")
    try:#If a channel isn't selected...
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            for usr in ch.cUsers:
                if usr.cNick.lower() == cResp.msg.lower():
                    rChannel = ch

        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey    
        highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.highlightColor)#Green
        partTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.partColor)#Dark Blue

        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >",highlightTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"!",nickTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"<" + " ",highlightTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " is now known as " + cResp.msg + "\n",partTag)

        scrollTxtViewColorTItem(rChannel, cServer, cServer.settings.statusTColor)

    except:
        #import traceback;traceback.print_exc()
        partTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.partColor)#Dark Blue

        cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),"timeTag")
        cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter()," >","highlightTag")
        cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),"!","nickTag")  
        cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),"<" + " ","highlightTag")   
        cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),cResp.nick + " is now known as " + cResp.msg + "\n",partTag)

        scrollTxtViewColorTItem(cServer, cServer, cServer.settings.statusTColor)

"""
onModeChange
When a user changes his/her/someones MODE 
"""
def onModeChange(cResp,cServer):
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
    timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey    
    highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.highlightColor)#Green

    pDebug("cResp.msg=" + cResp.msg)
    mode = cResp.msg.split()[0]
    personModeChange=""
    try:
        if len(cResp.msg.split()) > 1:
            #Loop, if there is more then one users mode being changed they will all be added
            #TODO: "+aop dom96 dom96 dom96" wouldn't work, make it work
            count=0
            for usr in cResp.msg.replace(cResp.msg.split()[0] + " ","").split(" "):
                if count == len(cResp.msg.replace(cResp.msg.split()[0] + " ","").split(" ")) - 2:
                    #If it's the one before the last one add a " and " to the end
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

    scrollTxtViewColorTItem(rChannel, cServer, cServer.settings.statusTColor)

"""
onUsersChange
When the list of users are changed(When joining a channel
"""
def onUsersChange(cChannel,cServer):
    noUserIcons = False
    # * = Founder and ~ = Founder
    # ! = Admin / Protected and & = Admin
    # @ = Op
    # % = HalfOp
    # + = Voice
            
    #Clear the users in the treeview
    #itr = cServer.listTreeStore.iter_children(cChannel.cTreeIter)
    #while itr:
        #cServer.listTreeStore.remove(itr)
        #itr = cServer.listTreeStore.iter_next(itr)

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
                    if noUserIcons==False:
                        cUsr.cTreeIter = cChannel.UserListStore.append([user,lookupIcon("founder")])
                    else:
                        cUsr.cTreeIter = cChannel.UserListStore.append([user,None])
    #Add the admins, to the list of users
    for user in admins:
        for cUsr in cChannel.cUsers:
            if cUsr.cNick == user:
                if itrContainsString(cUsr.cNick,cChannel.UserListStore.iter_children(cChannel.cTreeIter),cChannel.UserListStore) == False:
                    if noUserIcons==False:
                        cUsr.cTreeIter = cChannel.UserListStore.append([user,lookupIcon("admin")])
                    else:
                        cUsr.cTreeIter = cChannel.UserListStore.append([user,None])
    #Add the operators, to the list of users
    for user in ops:
        for cUsr in cChannel.cUsers:
            if cUsr.cNick == user:
                if itrContainsString(cUsr.cNick,cChannel.UserListStore.iter_children(cChannel.cTreeIter),cChannel.UserListStore) == False:
                    if noUserIcons==False:
                        cUsr.cTreeIter = cChannel.UserListStore.append([user,lookupIcon("op")])
                    else:
                        cUsr.cTreeIter = cChannel.UserListStore.append([user,None])
    #Add the half operators, to the list of users
    for user in hops:
        for cUsr in cChannel.cUsers:
            if cUsr.cNick == user:
                if itrContainsString(cUsr.cNick,cChannel.UserListStore.iter_children(cChannel.cTreeIter),cChannel.UserListStore) == False:
                    if noUserIcons==False:
                        cUsr.cTreeIter = cChannel.UserListStore.append([user,lookupIcon("hop")])
                    else:
                        cUsr.cTreeIter = cChannel.UserListStore.append([user,None])
    #Add the voices, to the list of users
    for user in vs:
        for cUsr in cChannel.cUsers:
            if cUsr.cNick == user:
                if itrContainsString(cUsr.cNick,cChannel.UserListStore.iter_children(cChannel.cTreeIter),cChannel.UserListStore) == False:
                    if noUserIcons==False:
                        cUsr.cTreeIter = cChannel.UserListStore.append([user,lookupIcon("voice")])
                    else:
                        cUsr.cTreeIter = cChannel.UserListStore.append([user,None])
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
            if noUserIcons==False:
                cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,lookupIcon("founder")])
            else:
                cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,None])
            return
        elif "!" in cUsr.cMode or "&" in cUsr.cMode:
            pDebug("!"+str(cIndex))
            if noUserIcons==False:
                cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,lookupIcon("admin")])
            else:
                cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,None])
            return
        elif "@" in cUsr.cMode:
            pDebug("@"+str(cIndex))
            if noUserIcons==False:
                cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,lookupIcon("op")])
            else:
                cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,None])
            return
        elif "%" in cUsr.cMode:
            pDebug("%"+str(cIndex))
            if noUserIcons==False:
                cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,lookupIcon("hop")])
            else:
                cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,None])
            return
        elif "+" in cUsr.cMode:
            pDebug("+"+str(cIndex))
            if noUserIcons==False:
                try:
                    cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,lookupIcon("voice")])
                except:
                    import traceback;traceback.print_exc()

            else:
                cUsr.cTreeIter = cChannel.UserListStore.insert(cIndex,[cUsr.cNick,None])
            return

"""
onUserRemove
When a user either QUIT's ,PART's(from a channel) or is KICKed, provides the iter to remove
"""
def onUserRemove(cChannel,cServer,cTreeIter,usr):
    pDebug("onUserRemove")
    pDebug(cChannel.cName)
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
onTopicChange
When a channels topic changes
"""
def onTopicChange(cResp,cServer):
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    try:
        cResp.typeMsg = cResp.code
    except:
        pDebug("\033[1;40m\033[1;33mMaking cResp.typeMsg = cResp.code failed\033[1;m\033[1;m") 

    #The text in TopicTextBox get's set in MainForm.py

    nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
    timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey    
    highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.highlightColor)#Red

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

    scrollTxtViewColorTItem(rChannel, cServer, cServer.settings.statusTColor)

"""
onChannelModeChange
When a channels mode changes.
"""
def onChannelModeChange(cResp,cServer):
    #Get the textbuffer for the right channel.
    for ch in cServer.channels:
        if ch.cName.lower() == cResp.channel.lower():
            rChannel = ch

    pDebug(cResp.code)

    nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
    timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey    
    highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.highlightColor)#Red

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

    scrollTxtViewColorTItem(rChannel, cServer, cServer.settings.statusTColor)

def onServerDisconnect(cServer):
    #Get the textbuffer for each channel
    for ch in cServer.channels:
        nickTag = ch.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
        timeTag = ch.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey    
        highlightTag = ch.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.highlightColor)#Red
        #!!!
        ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter()," !",highlightTag)
        ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(),"!",nickTag)
        ch.cTextBuffer.insert_with_tags(ch.cTextBuffer.get_end_iter(),"! ",highlightTag)
        ch.cTextBuffer.insert(ch.cTextBuffer.get_end_iter(), "Connection to cServer lost!\n")
        scrollTextView(ch, cServer, cServer.settings.statusTColor)

    nickTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.nickColor)#Blue-ish
    timeTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.timeColor)#Grey    
    highlightTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=cServer.settings.highlightColor)#Red
    #!!!
    cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),"!",highlightTag)
    cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),"!",nickTag)
    cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),"! ",highlightTag)
    cServer.cTextBuffer.insert(cServer.cTextBuffer.get_end_iter(), "Connection to server lost!\n")
    scrollTxtViewColorTItem(cServer, cServer, cServer.settings.statusTColor)

#!--IRC EVENTS END--!#
def scrollTxtViewColorTItem(ch, cServer, color):
    #Get the selected iter
    model, selected = cServer.listTreeView.get_selection().get_selected()
    newlySelected = cServer.listTreeStore.get_value(selected, 0)
    #Check to see if this channel is selected, and scroll the TextView if it is.
    #If i don't do this the TextView will scroll even when you have another channel/server selected
    #which is a bit annoying
    from IRCLibrary import IRC
    if ch.cType == "channel":
        pDebug(newlySelected + " " + ch.cName)
        if newlySelected == ch.cName:
            #Scroll the TextView to the bottom...                                   
            endMark = ch.cTextBuffer.create_mark(None, ch.cTextBuffer.get_end_iter(), True)
            cServer.chatTextView.scroll_to_mark(endMark, 0)
        elif color != None and newlySelected != ch.cName:
            cServer.listTreeStore.set_value(ch.cTreeIter, 2, color) #Set the channels this message was sent to, TreeIter color.
    elif ch.cType == "server":
        pDebug(newlySelected + " " + ch.cAddress)
        if newlySelected == ch.cAddress:#TODO: It should be ch.cName(server.cName), the mainForm uses cAddress though...CHANGE!
            #Scroll the TextView to the bottom...                                   
            endMark = ch.cTextBuffer.create_mark(None, ch.cTextBuffer.get_end_iter(), True)
            cServer.chatTextView.scroll_to_mark(endMark, 0)
        elif color != None and newlySelected != ch.cName:
            cServer.listTreeStore.set_value(ch.cTreeIter, 2, color) #Set the channels this message was sent to, TreeIter color.


import inspect
debugInfo=True
def pDebug(txt):
    if debugInfo:
        func = str(inspect.getframeinfo(inspect.currentframe().f_back).function)
        filename = str(inspect.getframeinfo(inspect.currentframe().f_back).filename);filename = filename.split("/")[len(filename.split("/"))-1]
        print "[\033[1;34m"+str(inspect.currentframe().f_back.f_lineno).rjust(3, '0')+"\033[1;m, " + filename +"(" + func + ")]\n    " + str(txt)
