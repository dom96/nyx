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
import pygtk
import gtk
import gobject
import thread
from time import localtime, strftime
import traceback
import pango
import time
import sys
#For errors
#sys.stderr = open("Messages", "a")
#sys.stdout = open("Messages","a")
#IRCLibrary, Import
from IRCLibrary import IRC,IRCHelper

from settings import settings

import IRCEvents
#!--End of Import--!#

gobject.threads_init() 

servers = [] #List of Servers, server()

#Colors for TextView
serverMsgTagColor = gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)#Black
motdMsgTagColor = gtk.gdk.Color(red=70 * 257,green=70 * 257 ,blue=70 * 257,pixel=0)#Orange
nickTagColor = gtk.gdk.Color(red=50 * 257, green=150 * 257, blue=255 * 257, pixel=0)#Blue-ish
timeTagColor = gtk.gdk.Color(red=124 * 257,green=124 * 257 ,blue=124 * 257,pixel=0)#Grey 
partTagColor = gtk.gdk.Color(red=0,green=6 * 257 ,blue=119 * 257,pixel=0)#Dark Blue
successTagColor = gtk.gdk.Color(red=0,green=184 * 257 ,blue=22 * 257,pixel=0)#Green
highlightTagColor = gtk.gdk.Color(red=255 * 257,green=0,blue=0,pixel=0)#Red

normalChannelColor = gtk.gdk.Color(red=0,green=0,blue=0,pixel=0)#Black
highlightChannelColor = gtk.gdk.Color(red=255 * 257,green=0,blue=0,pixel=0)#Red
talkChannelColor = gtk.gdk.Color(red=0,green=128 * 257,blue=255 * 257,pixel=0)#Blue
statusChannelColor = gtk.gdk.Color(red=0,green=200 * 257,blue=255 * 257,pixel=0)#Light Blue

class MainForm:
    def __init__(self):
        print "Nyx 0.1 Alpha"
        print "Initializing window"

        self.listTreeStore = gtk.TreeStore(str, str, gtk.gdk.Color, str) #Name #Icon #Color #Determines whether it's a channel or a User
        self.UserListTreeStore = gtk.ListStore(str, str)

        self.w = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.w.set_title("Nyx 0.1 Alpha")
        self.w.connect("delete_event",self.delete_event)
        self.w.connect("map-event",self.window_focus)
        self.w.connect("focus-in-event",self.window_focus)
        self.w.connect("focus-out-event",self.window_unfocus)

        self.w.set_default_size(750, 450)

        #Load the settings and the theme
        self.settings = settings.loadSettings()
        self.theme = settings.theme()
        self.theme.loadTheme(self.settings.themePath)

        #Setup the form
        from Form import form_stuff
        form_stuff.setup_form(self)
        
        self.w.show()
        #Setup the form END
        
        for server in self.settings.servers:
            if server.autoconnect == True:
                from Form import form_stuff
                form_stuff.connect_server(self, server, IRC, servers)

    def delete_event(self, widget, event=None, data=None):
        for serv in servers:
            if serv.connected == True: 
                serv.cSocket.send("QUIT :Nyx IRC Client, visit http://sourceforge.net/projects/nyxirc/\r\n")
        gtk.main_quit()
        return False

    def window_focus(self,widget,event):
        widget.set_urgency_hint(False)
        widget.focused = True

    def window_unfocus(self,widget,event):
        widget.focused = False

    def chatEntry_Activate(self,widget):
        if widget.get_text() != "":
            dest = ""
            serv = self.get_server()
            #Get the current channel...
            if len(serv.channels) != 0:
                #Loop through all of the channels
                for i in serv.channels:
                    selection = self.TreeView1.get_selection()
                    model, selected = selection.get_selected()
                    sl = self.listTreeStore.get_value(selected, 0).replace(" ","")
                    if sl.startswith("#"):
                        #Select the one that is selected in the treeview
                        if sl == i.cName:
                            dest = i.cName
                    else:
                        if sl == i.cName:
                            dest = i.cName

            wText = widget.get_text()
            if wText.startswith(" "):
                wText = wText[1:]

            #Add what you said to the TextView
            import sendMsg
            if sendMsg.entryBoxCheck(self, wText, serv, self.TreeView1, dest, servers, IRC) == False:

                IRCHelper.sendMsg(serv,dest,wText)

            widget.set_text("")

    """TREEVIEW EVENTS!!!!"""
    #When a server, chanel or a user gets selected in the treeview
    def TreeView_OnSelectionChanged(self,selection):
        #Get the selected iter
        model, selected = selection.get_selected()
        newlySelected = self.listTreeStore.get_value(selected, 0)
        newlySelectedType = self.listTreeStore.get_value(selected, 3)

        serv = self.get_server()

        if newlySelectedType == "channel":
            for i in serv.channels:
                if i.cName == newlySelected:
                    #Set this channels color(In the TreeView) to Black(The default 'normal' color)
                    self.listTreeStore.set_value(i.cTreeIter, 2, normalChannelColor)
                    #Set the TextViews buffer
                    self.chatTextView.set_buffer(i.cTextBuffer)
                    
                    #Set the Userlist TreeView's 'model'
                    self.UserTreeView.set_model(i.UserListStore)
                    self.UserTreeView.show()
                    
                    pDebug("NewTextBuffer Channel = " + i.cName)
                    #Set the topic
                    self.TopicEntryBox.set_text(i.cTopic)
                    self.pingLabel.set_text(str(int(round(serv.lag))) + " ms")
                    
        elif newlySelectedType == "user":
            for i in serv.channels:
                if i.cName.lower() == newlySelected.lower():
                    #Set this users color(In the TreeView) to Black(The default 'normal' color)
                    self.listTreeStore.set_value(i.cTreeIter, 2, normalChannelColor)
                    #Set the TextViews buffer
                    self.chatTextView.set_buffer(i.cTextBuffer)
                    #Hide the Userlist TreeView
                    self.UserTreeView.hide()
                    
                    pDebug("NewTextBuffer User = " + i.cName)
                    #Set the topic to the ident of the user
                    self.TopicEntryBox.set_text(i.cTopic)
                    self.pingLabel.set_text(str(int(round(serv.lag))) + " ms")
                    break
                    
        elif newlySelectedType == "server":
            i = self.get_server(newlySelected)
            #Set this servers color(In the TreeView) to Black(The default 'normal' color)
            self.listTreeStore.set_value(i.cTreeIter, 2, normalChannelColor)
            #Set the TextViews buffer
            self.chatTextView.set_buffer(i.cTextBuffer)
            
            pDebug("NewTextBuffer Server = " + i.cAddress.cAddress)
            
            #Hide the Userlist TreeView
            self.UserTreeView.hide()
            #Set the topic EntryBox's text to the address of this server
            self.TopicEntryBox.set_text(i.cAddress.cAddress)
            self.pingLabel.set_text(str(int(round(serv.lag))) + " ms")

        #Scroll the TextView to the bottom...
        endMark = self.chatTextView.get_buffer().create_mark(None, self.chatTextView.get_buffer().get_end_iter(), True)
        self.chatTextView.scroll_to_mark(endMark,0)

    def TreeView_focusInEvent(self,widget,event):
        self.chatEntry.grab_focus()

    def TreeView_ButtonPressEvent(self, treeview, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor(path, col, 0)
                menu = gtk.Menu()

                TreeIter = self.listTreeStore.get_iter(path)
                TreeIterValue = self.listTreeStore.get_value(TreeIter,0)

                ServerIter = self.listTreeStore.iter_parent(TreeIter)
                ServerIterValue = self.listTreeStore.get_value(ServerIter,0)
                parentServer = object
                for server in servers:
                    if server.cName == ServerIterValue:
                        parentServer = server
                selectedChannel=object
                for ch in parentServer.channels:
                    if ch.cName == TreeIterValue:
                        selectedChannel = ch
                pDebug(parentServer.cName)
                pDebug(selectedChannel.cName)
                #Channel menu item
                channel_item = gtk.MenuItem(TreeIterValue)
                menu.append(channel_item)
                channel_item.show()
                #Create the channel submenu
                channel_submenu = gtk.Menu()
                channel_item.set_submenu(channel_submenu)

                #Channel Modes!!!
                #Topic Protection
                pDebug(ch.cMode)

                topicP_item = gtk.CheckMenuItem("Topic Protection[+t]")
                if "t" in ch.cMode:
                    topicP_item.set_active(True)
                channel_submenu.append(topicP_item)
                #Connect the correct event, if it's not checked then send MODE #channel +t
                if topicP_item.get_active() == False:
                    topicP_item.connect("activate", lambda x:parentServer.cSocket.send("MODE " + TreeIterValue + " +t \r\n"))
                #If it is then send MODE #channel -t
                else:
                    topicP_item.connect("activate", lambda x:parentServer.cSocket.send("MODE " + TreeIterValue + " -t \r\n"))
                topicP_item.show()
                #No Outside Messages
                noOutMsg_item = gtk.CheckMenuItem("No Outside Messages[+n]")
                if "n" in ch.cMode:
                    noOutMsg_item.set_active(True)
                channel_submenu.append(noOutMsg_item)
                #Connect the correct event, if it's not checked then send MODE #channel +n
                if noOutMsg_item.get_active() == False:
                    noOutMsg_item.connect("activate", lambda x:parentServer.cSocket.send("MODE " + TreeIterValue + " +n \r\n"))
                #If it is then send MODE #channel -n
                else:
                    noOutMsg_item.connect("activate", lambda x:parentServer.cSocket.send("MODE " + TreeIterValue + " -n \r\n"))
                noOutMsg_item.show()
                #Secret
                secret_item = gtk.CheckMenuItem("Secret[+s]")
                if "s" in ch.cMode:
                    secret_item.set_active(True)
                channel_submenu.append(secret_item)
                #Connect the correct event, if it's not checked then send MODE #channel +s
                if secret_item.get_active() == False:
                    secret_item.connect("activate", lambda x:parentServer.cSocket.send("MODE " + TreeIterValue + " +s \r\n"))
                #If it is then send MODE #channel -s
                else:
                    secret_item.connect("activate", lambda x:parentServer.cSocket.send("MODE " + TreeIterValue + " -s \r\n"))
                secret_item.show()
                #Invite Only
                invite_item = gtk.CheckMenuItem("Invite Only[+i]")
                if "i" in ch.cMode:
                    invite_item.set_active(True)
                channel_submenu.append(invite_item)
                #Connect the correct event, if it's not checked then send MODE #channel +i
                if invite_item.get_active() == False:
                    invite_item.connect("activate", lambda x:parentServer.cSocket.send("MODE " + TreeIterValue + " +i \r\n"))
                #If it is then send MODE #channel -i
                else:
                    invite_item.connect("activate", lambda x:parentServer.cSocket.send("MODE " + TreeIterValue + " -i \r\n"))
                invite_item.show()
                #Private
                private_item = gtk.CheckMenuItem("Private[+p]")
                if "p" in ch.cMode:
                    private_item.set_active(True)
                channel_submenu.append(private_item)
                #Connect the correct event, if it's not checked then send MODE #channel +p
                if private_item.get_active() == False:
                    private_item.connect("activate", lambda x:parentServer.cSocket.send("MODE " + TreeIterValue + " +p \r\n"))
                #If it is then send MODE #channel -p
                else:
                    private_item.connect("activate", lambda x:parentServer.cSocket.send("MODE " + TreeIterValue + " -p \r\n"))
                private_item.show()
                #Moderated
                moderated_item = gtk.CheckMenuItem("Moderated[+m]")
                if "m" in ch.cMode:
                    moderated_item.set_active(True)
                channel_submenu.append(moderated_item)
                #Connect the correct event, if it's not checked then send MODE #channel +m
                if moderated_item.get_active() == False:
                    moderated_item.connect("activate", lambda x:parentServer.cSocket.send("MODE " + TreeIterValue + " +m \r\n"))
                #If it is then send MODE #channel -m
                else:
                    moderated_item.connect("activate", lambda x:parentServer.cSocket.send("MODE " + TreeIterValue + " -m \r\n"))
                moderated_item.show()
                #Ban List
                moderated_item = gtk.MenuItem("Ban List")
                channel_submenu.append(moderated_item)
                moderated_item.show()

                #Close menu item
                close_item = gtk.MenuItem("Close")
                menu.append(close_item)
                close_item.show()
                close_item.connect("activate", self.closeChannelClick, path)

                TreeIter = self.listTreeStore.get_iter(path)
                TreeIterValue = self.listTreeStore.get_value(TreeIter,0)
                pDebug(TreeIterValue)

                if TreeIterValue.startswith("#"):
                    menu.popup(None, None, None, event.button, time)
                elif ServerIter != None:
                    #Hide the modes which are 'Channel only'
                    channel_item.hide()
                    menu.popup(None, None, None, event.button, time)

            return 1

    def closeChannelClick(self, widget, path):
        TreeIter = self.listTreeStore.get_iter(path)
        TreeIterValue = self.listTreeStore.get_value(TreeIter,0)
        TreeIterColor = self.listTreeStore.get_value(TreeIter,2)
        
        serv = self.get_server()
        
        for ch in serv.channels:
            if ch.cName == TreeIterValue:
                serv.channels.remove(ch)
                break

        self.listTreeStore.remove(TreeIter)
        if TreeIterColor == normalChannelColor and TreeIterValue.startswith("#"): #TODO: have to change the color of the channel when the user PARTs it.
            serv.cSocket.send("PART " + TreeIterValue + " :Leaving\r\n")

    """TREEVIEW EVENTS END!!!"""

    """_-USER-_TREEVIEW EVENTS START HERE!!!"""
    def UserTreeView_ButtonPressEvent(self, treeview, event):
        if event.button == 3:
            x = int(event.x)
            y = int(event.y)
            time = event.time
            pthinfo = treeview.get_path_at_pos(x, y)
            if pthinfo is not None:
                path, col, cellx, celly = pthinfo
                treeview.grab_focus()
                treeview.set_cursor(path, col, 0)

                serv = self.get_server()

                #Get the selected iter
                selection = TreeView1.get_selection()
                model, TIselected = selection.get_selected()
                selected = self.listTreeStore.get_value(TIselected, 0)
                selectedChannel = object
                for ch in serv.channels:
                    if ch.cName == selected:
                        selectedChannel = ch
                #Get the name of the user
                TreeIter = selectedChannel.UserListStore.get_iter(path)
                TreeIterValue = selectedChannel.UserListStore.get_value(TreeIter,0)
                clickedUser=object
                for usr in selectedChannel.cUsers:
                    if usr.cNick.lower() == TreeIterValue.lower():
                        clickedUser = usr

                #Create the menu to be shown.
                menu = gtk.Menu()
                #Info menu
                info_item = gtk.MenuItem("Info")
                menu.append(info_item)
                info_item.show()

                #Menu for the Info
                info_submenu = gtk.Menu()
                info_item.set_submenu(info_submenu)
                #--Users Mode

                info_user_item = gtk.MenuItem("Mode: " + clickedUser.cMode)
                info_submenu.append(info_user_item)
                info_user_item.show()
                #info_item.connect("activate", self.closeChannelClick, path)

                pDebug(TreeIterValue)
                menu.popup(None, None, None, event.button, time)
            return 1


    #||IRC Events||#

    """
    onLagChange
    When a PONG message is received with the timestamp(LAG1234567890.0)
    """
    def onLagChange(self,cResp,cServer):
        serverAddr = cServer.cAddress.cAddress
        
        lag=cResp[3].replace(":LAG","").replace("\r","").replace("\n","")
        import time
        #pDebug(str(time.time()) + " " + lag)
        lagInt=time.time() - float(lag)

        lagMS = lagInt * 1000
        #pDebug("onLagChange " + str(cResp[3].replace("\r","").replace("\n","")) + ";lag=" + str(lagInt) + ";lagInMS=" + str(lagMS))

        #Change the lag to 0 if it's -Something
        if lagMS < 0:
            lagMS = 0
        self.get_server(srvAddress=serverAddr).lag = lagMS
            
        if self.get_server() == self.get_server(srvAddress=serverAddr):    
            self.pingLabel.set_text(str(int(round(lagMS))) + " ms")

    """
    onByteSendChange
    When the amount of Bytes to send(which reside in the queue waiting to be sent) changes
    """
    def onByteSendChange(self,cServer,entriesLeft):
        #TODO:Make this only show for the currently selected channel
        self.queueLabel.set_text(str(entriesLeft) + " messages")

    """
    onOwnPrivMsg
    When the user sends a message to a nick or to a channel - Adds the message set to the correct TextBuffer
    """
    def onOwnPrivMsg(self,cResp,cServer):
        global timeTagColor
        global nickTagColor
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            if ch.cName.lower() == cResp.channel.lower():
                rChannel = ch
            if cResp.channel.lower().startswith("#") == False:
                for usr in ch.cUsers:
                    if usr.cNick.lower() == cResp.channel.lower():
                        rChannel = usr

        #If the "Channel" in the cResp is your nick, add it to the currently selected channel/server
        if cResp.channel.lower() == cServer.cNick.lower():
            #Get the server first, this way if the selected chanel isn't found it's not gonna generate an exception
            rChannel = cServer
            #Get the selected iter
            model, selected = self.TreeView1.get_selection().get_selected()
            treeiterSelected = self.listTreeStore.get_value(selected, 0)
            for ch in cServer.channels:
                if ch.cName.lower() == treeiterSelected.lower():
                    rChannel = ch

        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey 
        highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=highlightTagColor)#Red    

        if cResp.msg.startswith("ACTION"):
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >",highlightTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"!",nickTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"<",highlightTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," " + cResp.nick,nickTag)
            rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter(),cResp.msg.replace("ACTION","").replace("","") + "\n")
        elif "" in cResp.msg:
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >",highlightTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"!",nickTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"<",highlightTag)
            rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter()," Sent CTCP " + cResp.msg.replace("","") + " to " + cResp.channel + "\n")
        else:
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)

            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," " + cResp.nick + ": ",nickTag)

            #Make a tag for the message
            msgTag = rChannel.cTextBuffer.create_tag(None)

            #URLs-----------------------------------------------------
            import re
            m = re.findall("(https?://([-\w\.]+)+(:\d+)?(/([\w/_\-\.]*(\?\S+)?)?)?)",cResp.msg)
            endMark=rChannel.cTextBuffer.get_end_iter()
            lineOffsetBAddMsg=endMark.get_line_offset()
            #rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.msg + "\n",msgTag)
            msgNoMIRC = IRCEvents.format_insert_text(rChannel.cTextBuffer, endMark, cResp.msg + "\n")

            import re
            m = re.findall("(https?://([-\w\.]+)+(:\d+)?(/([\w/_\-\.]*(\?\S+)?)?)?)", msgNoMIRC)
            if m != None:
                import pango
                for i in m:
                    urlTag = rChannel.cTextBuffer.create_tag(None,underline=pango.UNDERLINE_SINGLE)
                    urlTag.connect("event",IRCEvents.urlTextTagEvent,i[0])
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
                    fileTag.connect("event",IRCEvents.fileTextTagEvent,i)
                    endMark=rChannel.cTextBuffer.get_end_iter()
                    startIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1, lineOffsetBAddMsg + msgNoMIRC.index(i))
                    endIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1,lineOffsetBAddMsg + (msgNoMIRC.index(i) + len(i)))
                    pDebug(str(lineOffsetBAddMsg + cResp.msg.index(i)) + "--" + str(lineOffsetBAddMsg + (msgNoMIRC.index(i) + len(i))))
                    rChannel.cTextBuffer.apply_tag(fileTag,startIter,endIter)
            #File Paths END-------------------------------------------------

        #Get the selected iter
        model, selected = self.TreeView1.get_selection().get_selected()
        newlySelected = self.listTreeStore.get_value(selected, 0)
        #Check to see if this channel is selected, and scroll the TextView if it is.
        #If i don't do this the TextView will scroll even when you have another channel/server selected
        #which is a bit annoying
        try:
            change=True
            try:
                if type(rChannel.cAddress.cAddress) ==  str:
                    change=False
            except:
                change=True

            if change==True:
                rChannel.cName=rChannel.cNick 
        except:
            pDebug("\033[1;40m\033[1;33mMaking rChannel.cName=rChannel.cNick failed.\033[1;m\033[1;m")
        """----------------------"""    
        
        if newlySelected == rChannel.cName:
            #Scroll the TextView to the bottom...                                   
            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
            self.chatTextView.scroll_to_mark(endMark,0)

    """
    onTopicChange
    When the topic is changed, change the text in TopicTextBox
    """
    def onTopicChange(self,cResp,cServer,otherStuff):
        try:
            cResp.typeMsg = cResp.code
        except:
            pDebug("\033[1;40m\033[1;33mMaking cResp.typeMsg = cResp.code failed\033[1;m\033[1;m") 

        #Change the topic in the TopicEntryBox, if the code is not 333
        pDebug(cResp.typeMsg)
        if cResp.typeMsg != "333":
            self.TopicEntryBox.set_text(cResp.msg)

    #||IRC Events end||#
    """---------------------------------------------"""
    """
    get_server
    Gets the server with the specified name, if srvName isn't passed as an arg
    It get's the selected server(or selected channels/users server)
    """
    def get_server(self, srvName=None, srvAddress=None):
        if srvName == None:
            #Get the selected iter
            model, selectedIter = self.TreeView1.get_selection().get_selected()
            selectedText = self.listTreeStore.get_value(selectedIter, 0)
            selectedType = self.listTreeStore.get_value(selectedIter, 3)

            if selectedType == "server":
                srvName = selectedText
            else:
                ServerIter = self.listTreeStore.iter_parent(selectedIter)
                srvName = self.listTreeStore.get_value(ServerIter,0)

        if srvAddress == None:
            for server in servers:
                if server.cName.lower() == srvName.lower():
                    return server
        else:
            pDebug(srvAddress)
            for server in servers:
                if server.cAddress.cAddress.lower() == srvAddress.lower():
                    return server
        
        
           
        return None
    
    
import inspect
debugInfo=True
def pDebug(txt):
    if debugInfo:
        func = str(inspect.getframeinfo(inspect.currentframe().f_back).function)
        filename = str(inspect.getframeinfo(inspect.currentframe().f_back).filename);filename = filename.split("/")[len(filename.split("/"))-1]
        print "[\033[1;34m"+str(inspect.currentframe().f_back.f_lineno).rjust(3, '0')+"\033[1;m, " + filename +"(" + func + ")]\n    " + str(txt)

def main():
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave() 
    
if __name__ == "__main__":
    Initialize = MainForm()
    main()


