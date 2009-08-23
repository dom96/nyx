#!/usr/bin/env python
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
#sys.stderr = open("Errors.txt", "w")
#IRCLibrary, Import
from IRCLibrary import IRC,IRCHelper
#!--End of Import--!#

gobject.threads_init() 

chatTextView = gtk.TextView()#The TextView for the chat


listTreeStore = gtk.TreeStore(str,str)#For the list of servers,channels,users
listTreeView = gtk.TreeView

#Info
serverAddr = "irc.archerseven.com"
channelName = "#Nyx"
port = 6669
import random
nickname = "Nyx" + str(random.randint(0,50))

#Settings
noUserIcons=False
defaultBrowser="x-www-browser"

servers = [] #List of Servers, server()

#Colors for TextView
serverMsgTagColor = gtk.gdk.Color(red=255 * 257,green=144 * 257 ,blue=0,pixel=0)#Orange
nickTagColor = gtk.gdk.Color(red=50 * 257, green=150 * 257, blue=255 * 257, pixel=0)#Blue-ish
timeTagColor = gtk.gdk.Color(red=124 * 257,green=124 * 257 ,blue=124 * 257,pixel=0)#Grey 
partTagColor = gtk.gdk.Color(red=0,green=6 * 257 ,blue=119 * 257,pixel=0)#Dark Blue
successTagColor = gtk.gdk.Color(red=0,green=184 * 257 ,blue=22 * 257,pixel=0)#Green
highlightTagColor = gtk.gdk.Color(red=255 * 257,green=0,blue=0,pixel=0)#Red

class MainForm:
    def __init__(self):
        global serverAddr
        global channelName
        global port        
        global nickname
        global connectReturnQueue     

        global serverMsgTagColor
        global nickTagColor
        global timeTagColor
        global partTagColor
        global successTagColor
        global highlightTagColor

        print "Nyx 0.1 Alpha"
        print "Initializing window"

        self.w = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.w.set_title("Nyx 0.1 Alpha")
        self.w.connect("delete_event",self.delete_event)
        self.w.connect("map-event",self.window_focus)
        self.w.connect("focus-in-event",self.window_focus)
        self.w.connect("focus-out-event",self.window_unfocus)

        self.w.set_default_size(750,450)
        
        #Set up the server, which is connected to at startup in Nyx.
        self.nServer = IRC.server()        
        self.nServer.cAddress = serverAddr
        self.nServer.Nick = nickname
        self.nServer.cPort = port
        self.nServer.listTreeStore = listTreeStore
        servers.append(self.nServer)

        self.setupForm(self.w)
        self.w.show()

        #Colors
        serverMsgTag = self.nServer.cTextBuffer.create_tag("serverMsgTag",foreground_gdk=serverMsgTagColor)#Orange
        nickTag = self.nServer.cTextBuffer.create_tag("nickTag",foreground_gdk=nickTagColor)#Blue-ish
        timeTag = self.nServer.cTextBuffer.create_tag("timeTag",foreground_gdk=timeTagColor)#Grey 
        partTag = self.nServer.cTextBuffer.create_tag("partTag",foreground_gdk=partTagColor)#Red
        successTag = self.nServer.cTextBuffer.create_tag("successTag",foreground_gdk=successTagColor)#Green
        highlightTag = self.nServer.cTextBuffer.create_tag("highlightTag",foreground_gdk=highlightTagColor)

        self.nServer.cTextBuffer.insert_with_tags(self.nServer.cTextBuffer.get_end_iter(),"Nyx 0.1 Alpha Initialized\n",serverMsgTag)

        #Add the events.
        IRC.connectEvent("onMotdMsg",self.onMotdMsg,self.nServer)
        IRC.connectEvent("onServerMsg",self.onServerMsg,self.nServer)
        IRC.connectEvent("onPrivMsg",self.onPrivMsg,self.nServer)
        IRC.connectEvent("onJoinMsg",self.onJoinMsg,self.nServer)
        IRC.connectEvent("onQuitMsg",self.onQuitMsg,self.nServer)
        IRC.connectEvent("onPartMsg",self.onPartMsg,self.nServer)
        IRC.connectEvent("onNoticeMsg",self.onNoticeMsg,self.nServer)
        IRC.connectEvent("onKickMsg",self.onKickMsg,self.nServer)
        IRC.connectEvent("onNickChange",self.onNickChange,self.nServer)
        IRC.connectEvent("onModeChange",self.onModeChange,self.nServer)
        IRC.connectEvent("onUsersChange",self.onUsersChange,self.nServer)
        IRC.connectEvent("onUserJoin",self.onUserJoin,self.nServer)
        IRC.connectEvent("onUserRemove",self.onUserRemove,self.nServer)
        IRC.connectEvent("onLagChange",self.onLagChange,self.nServer)     
        IRC.connectEvent("onByteSendChange",self.onByteSendChange,self.nServer)
        IRC.connectEvent("onOwnPrivMsg",self.onOwnPrivMsg,self.nServer)

        #Start a new a connection to a server(Multi threaded)
        gtk.gdk.threads_enter()
        thread.start_new(IRC.connect,(serverAddr,nickname,"NyxIRC",port,self.nServer))
        gtk.gdk.threads_leave()
        
    def delete_event(self, widget, event, data=None):
        servers[0].cSocket.send("QUIT :" + "Nyx IRC Client, visit http://sourceforge.net/projects/nyxirc/\r\n")
        gtk.main_quit()
        return False

    def window_focus(self,widget,event):
        print "FOCUS"
        widget.set_urgency_hint(False)
        widget.focused = True

    def window_unfocus(self,widget,event):
        print "UNFOCUS"
        widget.focused = False

    def setupForm(self,w):
        global chatTextBuffer
        global chatTextView
        global listTreeStore
        global listTreeView
        global serverAddr

        #The Nyx item in the menu
        self.nyx_menu = gtk.MenuItem("_Nyx")
        self.nyx_menu.show()
        """----------------------------------"""
        #The View item in the menu
        self.view_menu = gtk.MenuItem("_View")
        self.view_menu.show()
        """----------------------------------"""
        #The Server item in the menu
        self.server_menu = gtk.MenuItem("_Server")
        self.server_menu.show()
        """----------------------------------"""
        #The Tools item in the menu
        self.tools_menu = gtk.MenuItem("_Tools")
        self.tools_menu.show()
        """----------------------------------"""
        #The About item in the help item
        self.about_menu = gtk.Menu()    
        self.about_menu_item = gtk.ImageMenuItem(gtk.STOCK_ABOUT,"About")    
        self.about_menu.append(self.about_menu_item)
        self.about_menu_item.show()

        #The help item in the menu
        self.help_menu = gtk.MenuItem("_Help")
        self.help_menu.show()
        self.help_menu.set_submenu(self.about_menu)
        """----------------------------------"""

        #VBox for the Menu
        self.MenuVBox = gtk.VBox()
        w.add(self.MenuVBox)
        self.MenuVBox.show()
        
        #The menu
        self.menu_bar = gtk.MenuBar()
        self.MenuVBox.pack_start(self.menu_bar, False, False, 0)
        self.menu_bar.show()
        #Add all the menu's to the menu :P
        self.menu_bar.append(self.nyx_menu)
        self.menu_bar.append(self.view_menu)
        self.menu_bar.append(self.server_menu)
        self.menu_bar.append(self.tools_menu)
        self.menu_bar.append(self.help_menu)

        #HPaned - The split panel
        self.HPaned1 = gtk.HPaned()
        self.MenuVBox.pack_end(self.HPaned1)
        self.HPaned1.show()
    
        #TreeBox - For the TreeView and Ping meter
        self.TreeVBox = gtk.VBox()
        self.HPaned1.add(self.TreeVBox)
        self.TreeVBox.show()

        #TreeView - Treeview for the channels and servers(like in xchat lol :P) 
        
        self.treeScrolledWindow = gtk.ScrolledWindow()
        self.treeScrolledWindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.TreeVBox.pack_start(self.treeScrolledWindow)

        self.TreeView1 = gtk.TreeView(listTreeStore)
        #Border..
        self.treeScrolledWindow.set_shadow_type(gtk.SHADOW_IN)      

        self.treeScrolledWindow.add(self.TreeView1)
        self.treeScrolledWindow.show()
        self.TreeView1.show()

        listTreeView = self.TreeView1
        self.HPaned1.set_position(150)
    
        # --All the treeView stuff...
        self.tvcolumn = gtk.TreeViewColumn(None)

        serverTreeIter = listTreeStore.append(None,[serverAddr, gtk.STOCK_NETWORK])

        #Select that row ^^^        
        self.selection = self.TreeView1.get_selection()
        self.selection.select_iter(serverTreeIter)
        
        #Add the column, to the treeview
        self.TreeView1.append_column(self.tvcolumn)
        
        self.TreeView1.set_headers_visible(False)#Don't show the Columns....
        self.TreeView1.set_enable_tree_lines(True)#Set the Tree Lines, so that they show...

        self.cellpb = gtk.CellRendererPixbuf()#The renderer for images ??
        self.cell = gtk.CellRendererText()#The renderer for text
        
        self.tvcolumn.pack_start(self.cellpb, False)
        self.tvcolumn.pack_start(self.cell, True)

        # set the cell attributes to the appropriate liststore column
        self.tvcolumn.set_attributes(self.cellpb, stock_id=1)
        self.tvcolumn.set_attributes(self.cell, text=0)

        #SelectionChanged signal
        selection = self.TreeView1.get_selection()
        selection.connect('changed', self.TreeView_OnSelectionChanged)

        #PING measure
        self.pingLabel = gtk.Label("LAG")
        self.TreeVBox.pack_start(self.pingLabel,False,False,5)
        self.pingLabel.show()

        #Number of messages in the msgBuffer(queue) which are waiting to be sent.
        self.queueLabel = gtk.Label("0 messages")
        self.TreeVBox.pack_start(self.queueLabel,False,False,5)
        self.queueLabel.show()

        #HBox - For the TextView and EntryBox
        self.VBox1 = gtk.VBox()
        self.HPaned1.add(self.VBox1)
        self.VBox1.show()
        #ScrollWindows for the TextView
        self.chatScrolledWindow = gtk.ScrolledWindow()
        self.chatScrolledWindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.VBox1.pack_start(self.chatScrolledWindow)
        self.chatScrolledWindow.show()


        #TextView - For the actual chat...
        self.chatTextView = gtk.TextView()
        self.chatTextView.set_buffer(servers[0].cTextBuffer)
        self.chatTextView.set_wrap_mode(gtk.WRAP_WORD)
        self.chatTextView.set_editable(False)
        self.chatTextView.modify_font(pango.FontDescription("monospace 9"))

        self.chatTextView.connect("populate-popup",self.TextView_populatePopup)
        self.newTextViewMenu=[]

        #Borders
        self.chatTextView.set_border_window_size(gtk.TEXT_WINDOW_LEFT,1)
        self.chatTextView.set_border_window_size(gtk.TEXT_WINDOW_RIGHT,1)
        #self.chatTextView.set_border_window_size(gtk.TEXT_WINDOW_TOP,1)
        self.chatTextView.set_border_window_size(gtk.TEXT_WINDOW_BOTTOM,1)
        #Borders-Color
        self.chatTextView.modify_bg(gtk.STATE_NORMAL,gtk.gdk.Color(red=124 * 257,green=124 * 257 ,blue=124 * 257,pixel=0))

        self.chatScrolledWindow.add(self.chatTextView)
        self.chatTextView.show()
        chatTextView = self.chatTextView
        #EntryBox - For the speaking part
        self.chatEntry = gtk.Entry()
        self.VBox1.pack_end(self.chatEntry,False,False,5)
        self.chatEntry.connect("activate",self.chatEntry_Activate)
        self.chatEntry.show()

    def chatEntry_Activate(self,widget):
        if widget.get_text() != "":
            global timeTagColor, nickTagColor
            #Get the current channel...
            if len(servers[0].channels) != 0:
                #Loop through all of the channels
                for i in servers[0].channels:
                    selection = listTreeView.get_selection()
                    model, selected = selection.get_selected()
                    #Select the one that is selected in the treeview
                    if listTreeStore.get_value(selected, 0).replace(" ","") == i.cName:
                        cChannel = i
        
            wText = widget.get_text()
            if wText.startswith(" "):
                wText = wText[1:]

            #Add what you said to the TextView
            import sendMsg
            if sendMsg.entryBoxCheck(wText,servers[0],listTreeView) == False:
                IRCHelper.sendMsg(servers[0],cChannel.cName,wText,False)

            widget.set_text("")

    def TreeView_OnSelectionChanged(self,selection):
        #Get the selected iter
        model, selected = selection.get_selected()
        newlySelected = listTreeStore.get_value(selected, 0)
        print newlySelected

        if listTreeStore.iter_parent(selected) != None:#If the selected iter is a channel
            for i in servers[0].channels:
                if i.cName == newlySelected:
                    chatTextView.set_buffer(i.cTextBuffer)
                    print "NewTextBuffer Channel = " + i.cName
        else:#If the selected iter is a server
            for i in servers:
                if i.cAddress == newlySelected:
                    chatTextView.set_buffer(i.cTextBuffer)
                    print "NewTextBuffer Channel = " + i.cAddress

    #||IRC Events||#
    """
    onMotdMsg
    When a MOTD Message is received.
    """
    def onMotdMsg(self,cResp,cServer):#When a MOTD message is received and parsed.
        global chatTextView
        print "onMotdMsg"
        cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()) + "\n","timeTag")

        for m in cResp:
            if m.msg != "":
                cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),">" + m.msg + "\n","serverMsgTag")
                print "\033[1;35m" + m.msg + "\033[1;m"

        #Scroll the TextView to the bottom...                                   
        endMark = chatTextView.get_buffer().create_mark(None, chatTextView.get_buffer().get_end_iter(), True)
        chatTextView.scroll_to_mark(endMark,0)

    """
    onServerMsg
    When a server message is received.
    """
    def onServerMsg(self,cResp,cServer):#When a server msg is received and parsed.
        global timeTagColor
        global nickTagColor
        global serverMsgTagColor
        
        serverMsgTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=serverMsgTagColor)#Orange
        nickTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
        timeTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey 

        for m in cResp:
            if m.msg != "":
                cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
                cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),">",nickTag)
                cServer.cTextBuffer.insert_with_tags(cServer.cTextBuffer.get_end_iter(),m.msg + "\n",serverMsgTag)
        
        #Scroll the TextView to the bottom...                                   
        endMark = cServer.cTextBuffer.create_mark(None, cServer.cTextBuffer.get_end_iter(), True)
        chatTextView.scroll_to_mark(endMark,0)    
        
    """
    onPrivMsg
    When a PRIV message is received, this includes an ACTION message.
    """
    def onPrivMsg(self,cResp,cServer):#When a normal msg is received and parsed.
        global timeTagColor
        global nickTagColor
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            if ch.cName.lower() == cResp.channel.lower():
                rChannel = ch

        #If the "Channel" in the cResp is your nick, add it to the currently selected channel/server
        if cResp.channel.lower() == cServer.cNick.lower():
            #Get the server first, this way if the selected chanel isn't found it's not gonna generate an exception
            rChannel = cServer
            #Get the selected iter
            model, selected = listTreeView.get_selection().get_selected()
            treeiterSelected = listTreeStore.get_value(selected, 0)
            for ch in cServer.channels:
                if ch.cName.lower() == treeiterSelected.lower():
                    rChannel = ch

        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey 
        highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=highlightTagColor)#Red    

        import mIRCColors
        newNickTagColor = mIRCColors.mIRCColors.get(mIRCColors.canonicalColor(cResp.nick)[0])
        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=newNickTagColor)
        if "ACTION" in cResp.msg:
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
            rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter()," Received CTCP " + cResp.msg.replace("","") + " from " + cResp.nick + "\n")
        else:
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)

            #If it's a Private Message to you not the channel.
            if cResp.channel == cServer.cNick:
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," )",highlightTag)
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick,nickTag)
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"(",highlightTag)
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),": ",nickTag)
            #If it's a message to the channel
            else:
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," " + cResp.nick + ": ",nickTag)

            #Make a tag for the message
            msgTag = rChannel.cTextBuffer.create_tag(None)
            if cServer.cNick.lower() in cResp.msg.lower():
                msgTag.set_property("foreground-gdk",highlightTagColor)
                if self.w.focused==False:
                    self.w.set_urgency_hint(True)
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
                    urlTag.connect("event",self.urlTextTagEvent,i[0])
                    endMark=rChannel.cTextBuffer.get_end_iter()
                    startIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1, lineOffsetBAddMsg + cResp.msg.index(i[0]))
                    endIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1,lineOffsetBAddMsg + (cResp.msg.index(i[0]) + len(i[0])))
                    rChannel.cTextBuffer.apply_tag(urlTag,startIter,endIter)
            #URLs END-------------------------------------------------
            #File Paths-----------------------------------------------------
            import re
            m = re.findall("([/|~][A-Za-z/.0-9]+)",cResp.msg)

            if m != None:
                import pango
                for i in m:
                    fileTag = rChannel.cTextBuffer.create_tag(None,underline=pango.UNDERLINE_SINGLE)
                    fileTag.connect("event",self.fileTextTagEvent,i)
                    endMark=rChannel.cTextBuffer.get_end_iter()
                    startIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1, lineOffsetBAddMsg + cResp.msg.index(i))
                    endIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1,lineOffsetBAddMsg + (cResp.msg.index(i) + len(i)))
                    print str(lineOffsetBAddMsg + cResp.msg.index(i)) + "--" + str(lineOffsetBAddMsg + (cResp.msg.index(i) + len(i)))
                    rChannel.cTextBuffer.apply_tag(fileTag,startIter,endIter)
            #File Paths END-------------------------------------------------

        #Get the selected iter
        model, selected = listTreeView.get_selection().get_selected()
        newlySelected = listTreeStore.get_value(selected, 0)
        #Check to see if this channel is selected, and scroll the TextView if it is.
        #If i don't do this the TextView will scroll even when you have another channel/server selected
        #which is a bit annoying
        if newlySelected == rChannel.cName:
            #Scroll the TextView to the bottom...                                   
            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
            chatTextView.scroll_to_mark(endMark,0) 

    def urlTextTagEvent(self,texttag, widget, event, textiter,url):
        print event
        if event.type == gtk.gdk.BUTTON_PRESS:
            if event.button == 3:
                print "BTN PRESS"
                seperator = gtk.SeparatorMenuItem()
                open_item = gtk.MenuItem("Open in default web browser")
                open_item.connect("activate", self.urlTextTagMenu_Activate,url)
                self.newTextViewMenu = []
                self.newTextViewMenu.append(seperator)
                self.newTextViewMenu.append(open_item)

    def urlTextTagMenu_Activate(self, widget, url):
        import os
        if os.name != "nt":
            os.system(defaultBrowser + " " + url)
        else:
            os.system(url)

    """FILE TextTag -------------------------------------------------"""
    def fileTextTagEvent(self,texttag, widget, event, textiter,path):
        print event
        if event.type == gtk.gdk.BUTTON_PRESS:
            if event.button == 3:
                print "BTN PRESS"
                if len(self.newTextViewMenu) == 0:
                    seperator = gtk.SeparatorMenuItem()
                    open_item = gtk.MenuItem("Open")
                    openR_item = gtk.MenuItem("Open as root")
                    open_item.connect("activate", self.fileTextTagMenu_Activate,path)
                    openR_item.connect("activate", self.fileTextTagMenuR_Activate,path)
                    self.newTextViewMenu.append(seperator)
                    self.newTextViewMenu.append(open_item)
                    self.newTextViewMenu.append(openR_item)

    def TextView_populatePopup(self,textview, menu):
        print "TextView_populatePopup"
        print self.newTextViewMenu
        if len(self.newTextViewMenu) != 0:
            for i in self.newTextViewMenu:
                menu.append(i)
                i.show()
            self.newTextViewMenu = []

    def fileTextTagMenu_Activate(self, widget, path):
        import os
        os.system("gnome-open " + path)

    def fileTextTagMenuR_Activate(self, widget, path):
        import os
        os.system("gksudo 'gnome-open %s'" % path)
    """FILE TextTag END----------------------------------------------"""

    """
    onJoinMsg
    When a JOIN message is received.(When a user joins a channel)
    """
    def onJoinMsg(self,cResp,cServer):#When a user joins a channel
        global successTagColor
        global nickTagColor
        global timeTagColor
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            print ch.cName,cResp.channel
            if ch.cName.lower() == cResp.channel.lower():
                rChannel = ch

        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey    
        successTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=successTagColor)#Green


        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," -->" + " ",nickTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " has joined " + cResp.channel + "\n",successTag)

        #Get the selected iter
        model, selected = listTreeView.get_selection().get_selected()
        newlySelected = listTreeStore.get_value(selected, 0)
        #Check to see if this channel is selected, and scroll the TextView if it is.
        #If i don't do this the TextView will scroll even when you have another channel/server selected
        #which is a bit annoying
        if newlySelected == rChannel.cName:#If the selected channel is this one then scroll otherwise it would scroll it weirdly.
            #Scroll the TextView to the bottom...                                   
            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
            chatTextView.scroll_to_mark(endMark,0)

    """
    onQuitMsg
    When a QUIT message is received.(When a user quits server)
    """
    def onQuitMsg(self,cResp,cServer):
        global partTagColor
        global nickTagColor
        global timeTagColor
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            if ch.cName.lower() == cResp.msg.lower():
                rChannel = ch
        try:
            nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
            timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey    
            partTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=partTagColor)#Green

            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," <--" + " ",nickTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " has quit " + rChannel.cName + " (" + cResp.msg + ")" + "\n",partTag)
            
            #Get the selected iter
            model, selected = listTreeView.get_selection().get_selected()
            newlySelected = listTreeStore.get_value(selected, 0)
            if newlySelected == rChannel.cName:
                #Scroll the TextView to the bottom...                                   
                endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
                chatTextView.scroll_to_mark(endMark,0)
        except:
            #I guess every server does this , it doesn't give you the channel the person QUIT on, 
            #so i have to check if the person who QUIT is in any of the channels that i'm on, and notify the user on the correct channel.
            for ch in cServer.channels:
                for user in ch.cUsers:
                    if cResp.nick.lower() == user.cNick.lower():
                        rChannel = ch

                        print "Found channel: \033[1;35m" + rChannel.cName + "\033[1;m"

                        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
                        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey    
                        partTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=partTagColor)#Green

                        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
                        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," <--" + " ",nickTag)
                        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " has quit " + rChannel.cName + " (" + cResp.msg + ")" + "\n",partTag)

                        #Get the selected iter
                        model, selected = listTreeView.get_selection().get_selected()
                        newlySelected = listTreeStore.get_value(selected, 0)
                        #Check to see if this channel is selected, and scroll the TextView if it is.
                        #If i don't do this the TextView will scroll even when you have another channel/server selected
                        #which is a bit annoying
                        if newlySelected == rChannel.cName:
                            #Scroll the TextView to the bottom...                                   
                            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
                            chatTextView.scroll_to_mark(endMark,0)
                    
    """
    onPartMsg
    When a PART message is received.(A user leaves a channel)
    """                     
    def onPartMsg(self,cResp,cServer):
        global partTagColor
        global nickTagColor
        global timeTagColor
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            if ch.cName.lower() == cResp.channel.lower():
                rChannel = ch

        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey    
        partTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=partTagColor)#Green

        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," <--" + " ",nickTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " has left " + cResp.channel + " (" + cResp.msg + ")" + "\n",partTag)

        if cResp.nick == cServer.cNick:
            for usr in rChannel.cUsers:
                cServer.listTreeStore.remove(usr.cTreeIter)
            
            rChannel.cUsers = []


        #Get the selected iter
        model, selected = listTreeView.get_selection().get_selected()
        newlySelected = listTreeStore.get_value(selected, 0)
        #Check to see if this channel is selected, and scroll the TextView if it is.
        #If i don't do this the TextView will scroll even when you have another channel/server selected
        #which is a bit annoying
        if newlySelected == rChannel.cName:
            #Scroll the TextView to the bottom...                                   
            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
            chatTextView.scroll_to_mark(endMark,0)

    """
    onNoticeMsg
    When a NOTICE message is received.
    """
    def onNoticeMsg(self,cResp,cServer):
        global highlightTagColor
        global nickTagColor
        global timeTagColor

        try:#If a channel isn't selected...
            #Get the selected iter
            model, selected = listTreeView.get_selection().get_selected()
            newlySelected = listTreeStore.get_value(selected, 0)
            #Get the textbuffer for the right channel.
            for ch in cServer.channels:
                if ch.cName.lower() == newlySelected.lower():
                    rChannel = ch

            nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
            timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey    
            highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=highlightTagColor)#Green

            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >",highlightTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick,nickTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"<" + " ",highlightTag)
            rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter(),cResp.msg + "\n")

            #Get the selected iter
            model, selected = listTreeView.get_selection().get_selected()
            newlySelected = listTreeStore.get_value(selected, 0)
            #Check to see if this channel is selected, and scroll the TextView if it is.
            #If i don't do this the TextView will scroll even when you have another channel/server selected
            #which is a bit annoying
            if newlySelected == rChannel.cName:
                #Scroll the TextView to the bottom...                                   
                endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
                chatTextView.scroll_to_mark(endMark,0)

        except:
            cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),"timeTag")
            cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter()," >","highlightTag")
            cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),cResp.nick,"nickTag")  
            cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),"<" + " ","highlightTag")   
            cServer.cTextBuffer.insert(cServer.cTextBuffer.get_end_iter(),cResp.msg + "\n")

            #Get the selected iter
            model, selected = listTreeView.get_selection().get_selected()
            newlySelected = listTreeStore.get_value(selected, 0)
            #Check to see if this server is selected, and scroll the TextView if it is.
            #If i don't do this the TextView will scroll even when you have another channel/server selected
            #which is a bit annoying
            if newlySelected == cServer.cName:
                #Scroll the TextView to the bottom...                                   
                endMark = cServer.cTextBuffer.create_mark(None, cServer.cTextBuffer.get_end_iter(), True)
                chatTextView.scroll_to_mark(endMark,0)

    """
    onKickMsg
    When a KICK message is received.(When a operator kicks another user from a channel)
    """
    def onKickMsg(self,cResp,cServer):
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            if ch.cName.lower() == cResp.channel.lower():
                rChannel = ch

        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey    
        highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=highlightTagColor)#Green
    
        personWhoKicked = cResp.nick.split(",")[0]
        personWhoWasKicked = cResp.nick.split(",")[1]

        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," <-- ",highlightTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),personWhoKicked,nickTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," has kicked " + personWhoWasKicked + "(" + cResp.msg[1:] + ")\n",highlightTag)

        #Get the selected iter
        model, selected = listTreeView.get_selection().get_selected()
        newlySelected = listTreeStore.get_value(selected, 0)
        #Check to see if this channel is selected, and scroll the TextView if it is.
        #If i don't do this the TextView will scroll even when you have another channel/server selected
        #which is a bit annoying
        if newlySelected == rChannel.cName:
            #Scroll the TextView to the bottom...                                   
            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
            chatTextView.scroll_to_mark(endMark,0)

        if personWhoWasKicked == cServer.cNick:
            IRCHelper.join(cServer,rChannel.cName,cServer.listTreeStore)

    """
    onNickChange
    When a NICK message is received.(When a user changes his nick or someone else(like a service) changes a users nick)
    """
    def onNickChange(self,cResp,cServer):
        global partTagColor
        global nickTagColor
        global timeTagColor
        global nickname
        print "OnNickChange"
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            if ch.cName.lower() == cResp.msg.lower():
                rChannel = ch
       

        try:
            nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
            timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey    
            partTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=partTagColor)#Green

            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >!<" + " ",nickTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " is now known as " + cResp.msg + "\n",partTag)

            #Get the selected iter
            model, selected = listTreeView.get_selection().get_selected()
            newlySelected = listTreeStore.get_value(selected, 0)
            #Check to see if this channel is selected, and scroll the TextView if it is.
            #If i don't do this the TextView will scroll even when you have another channel/server selected
            #which is a bit annoying
            if newlySelected == rChannel.cName:
                #Scroll the TextView to the bottom...                                   
                endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
                chatTextView.scroll_to_mark(endMark,0)

            #Search for the user and change his name.
            for user in rChannel.cUsers:
                if user.cNick == cResp.nick:
                    cServer.listTreeStore.set_value(user.cTreeIter,0,cResp.msg)    
                    user.cNick = cResp.msg
        except:
            #Every server does this, it doesn't give you the channel the person QUIT on, 
            #so i have to check if the person who QUIT is in any of the channels that i'm on, and notify the user on the correct channel.
            for ch in cServer.channels:
                for user in ch.cUsers:
                    if cResp.nick.lower() in user.cNick.lower():                        
                        rChannel = ch

                        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
                        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey    
                        partTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=partTagColor)#Green

                        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
                        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >!<" + " ",nickTag)
                        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " is now known as " + cResp.msg + "\n",partTag)

                        #Get the selected iter
                        model, selected = listTreeView.get_selection().get_selected()
                        newlySelected = listTreeStore.get_value(selected, 0)
                        #Check to see if this channel is selected, and scroll the TextView if it is.
                        #If i don't do this the TextView will scroll even when you have another channel/server selected
                        #which is a bit annoying
                        if newlySelected == rChannel.cName:
                            #Scroll the TextView to the bottom...                                   
                            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
                            chatTextView.scroll_to_mark(endMark,0)

                        #Search for the user and change his name.(in the treeview)
                        for user in rChannel.cUsers:
                            if user.cNick.lower() == cResp.nick.lower():
                                print "Setting-" + cResp.msg
                                print rChannel.cTreeIter,user.cTreeIter
                                print "USER =",cServer.listTreeStore.get_value(user.cTreeIter,0)
                                cServer.listTreeStore.set_value(user.cTreeIter,0,cResp.msg)                        
                                user.cNick = cResp.msg


                        #Search the name in the Users
    """
    onModeChange
    When a user changes his/her/someones MODE 
    """
    def onModeChange(self,cResp,cServer):
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            if ch.cName.lower() == cResp.channel.lower():
                rChannel = ch

        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey    
        highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=highlightTagColor)#Green
    
        print "cResp.msg=" + cResp.msg
        mode = cResp.msg.split()[0]
        personModeChange = cResp.msg.split()[1] #Person who's mode got changed

        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
        #>!<
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," >",highlightTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"!",nickTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"< ",highlightTag)

        #nick
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick,nickTag)
        # sets mode +o for dom96
        rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter()," sets mode " + mode + " for " + personModeChange + "\n")

        #Get the selected iter
        model, selected = listTreeView.get_selection().get_selected()
        newlySelected = listTreeStore.get_value(selected, 0)
        #Check to see if this channel is selected, and scroll the TextView if it is.
        #If i don't do this the TextView will scroll even when you have another channel/server selected
        #which is a bit annoying
        if newlySelected == rChannel.cName:
            #Scroll the TextView to the bottom...                                   
            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
            chatTextView.scroll_to_mark(endMark,0)
                            
    """
    onUsersChange
    When the list of users are changed(When joining a channel
    """
    def onUsersChange(self,cChannel,cServer):

        # * = Founder and ~ = Founder
        # ! = Admin / Protected and & = Admin
        # @ = Op
        # % = HalfOp
        # + = Voice
                
        #Clear the users in the treeview
        itr = cServer.listTreeStore.iter_children(cChannel.cTreeIter)
        while itr:
            cServer.listTreeStore.remove(itr)
            itr = cServer.listTreeStore.iter_next(itr)

        #Sort the users.
        owners = []
        for user in cChannel.cUsers:
            if "*" in user.cMode or "~" in user.cMode:
                print "Adding " + user.cNick + " to Founders(With mode",user.cMode + ")"
                owners.append(user.cNick)
        owners.sort(key=str.lower)              
        admins = []
        for user in cChannel.cUsers:
            if "!" in user.cMode or "&" in user.cMode:
                print "Adding",user.cNick,"to Admins(With mode",user.cMode + ")"
                admins.append(user.cNick)
        admins.sort(key=str.lower)
        ops = []
        for user in cChannel.cUsers:
            if "@" in user.cMode:
                print "Adding",user.cNick,"to OPs(With Mode",user.cMode + ")"
                ops.append(user.cNick)
        ops.sort(key=str.lower)
        hops = []
        for user in cChannel.cUsers:
            if "%" in user.cMode:
                print "Adding",user.cNick,"to HOPs"
                hops.append(user.cNick)
        hops.sort(key=str.lower)
        vs = []
        for user in cChannel.cUsers:
            if "+" in user.cMode:
                print "Adding",user.cNick,"to V"
                vs.append(user.cNick)
        vs.sort(key=str.lower)
        others = []
        for user in cChannel.cUsers:
            if ("*" not in user.cMode and "!" not in user.cMode and "@" not in user.cMode and "%" not in user.cMode and
 "+" not in user.cMode and "~" not in user.cMode and "&" not in user.cMode):
                print "Adding",user.cNick,"to Others(With mode",user.cMode + ")"
                others.append(user.cNick)
        others.sort(key=str.lower)

        self.register_iconsets([("founder", sys.path[0] + "/images/Founder.png"),("admin", sys.path[0] + "/images/Admin.png"),
        ("op", sys.path[0] + "/images/op.png"),("hop", sys.path[0] + "/images/hop.png"),("voice", sys.path[0] + "/images/voice.png")])

        print others,hops,ops,admins,owners
        #Add the Owners, to the list of users.
        for user in owners:
            for cUsr in cChannel.cUsers:
                if cUsr.cNick == user:
                    if self.itrContainsString(cUsr.cNick,cServer.listTreeStore.iter_children(cChannel.cTreeIter),cServer.listTreeStore) == False:
                        if noUserIcons==False:
                            cUsr.cTreeIter = cServer.listTreeStore.append(cChannel.cTreeIter,[user,self.lookupIcon("founder")])
                        else:
                            cUsr.cTreeIter = cServer.listTreeStore.append(cChannel.cTreeIter,[user,None])
        #Add the admins, to the list of users
        for user in admins:
            for cUsr in cChannel.cUsers:
                if cUsr.cNick == user:
                    if self.itrContainsString(cUsr.cNick,cServer.listTreeStore.iter_children(cChannel.cTreeIter),cServer.listTreeStore) == False:
                        if noUserIcons==False:
                            cUsr.cTreeIter = cServer.listTreeStore.append(cChannel.cTreeIter,[user,self.lookupIcon("admin")])
                        else:
                            cUsr.cTreeIter = cServer.listTreeStore.append(cChannel.cTreeIter,[user,None])
        #Add the operators, to the list of users
        for user in ops:
            for cUsr in cChannel.cUsers:
                if cUsr.cNick == user:
                    if self.itrContainsString(cUsr.cNick,cServer.listTreeStore.iter_children(cChannel.cTreeIter),cServer.listTreeStore) == False:
                        if noUserIcons==False:
                            cUsr.cTreeIter = cServer.listTreeStore.append(cChannel.cTreeIter,[user,self.lookupIcon("op")])
                        else:
                            cUsr.cTreeIter = cServer.listTreeStore.append(cChannel.cTreeIter,[user,None])
        #Add the half operators, to the list of users
        for user in hops:
            for cUsr in cChannel.cUsers:
                if cUsr.cNick == user:
                    if self.itrContainsString(cUsr.cNick,cServer.listTreeStore.iter_children(cChannel.cTreeIter),cServer.listTreeStore) == False:
                        if noUserIcons==False:
                            cUsr.cTreeIter = cServer.listTreeStore.append(cChannel.cTreeIter,[user,self.lookupIcon("hop")])
                        else:
                            cUsr.cTreeIter = cServer.listTreeStore.append(cChannel.cTreeIter,[user,None])
        #Add the voices, to the list of users
        for user in vs:
            for cUsr in cChannel.cUsers:
                if cUsr.cNick == user:
                    if self.itrContainsString(cUsr.cNick,cServer.listTreeStore.iter_children(cChannel.cTreeIter),cServer.listTreeStore) == False:
                        if noUserIcons==False:
                            cUsr.cTreeIter = cServer.listTreeStore.append(cChannel.cTreeIter,[user,self.lookupIcon("voice")])
                        else:
                            cUsr.cTreeIter = cServer.listTreeStore.append(cChannel.cTreeIter,[user,None])
        #Add the rest, to the list of users
        for user in others:
            for cUsr in cChannel.cUsers:
                if cUsr.cNick == user:
                    if self.itrContainsString(cUsr.cNick,cServer.listTreeStore.iter_children(cChannel.cTreeIter),cServer.listTreeStore) == False:
                        cUsr.cTreeIter = cServer.listTreeStore.append(cChannel.cTreeIter,[user,None])


    def itrContainsString(self,string,itr,treestore):
        try:
            while itr:
                if treestore.get_value(itr, 0) == string:
                    return True
                itr = treestore.iter_next(itr)

            return False
        except:
            return True
            traceback.print_exc()

    def register_iconsets(self,icon_info):
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
    def lookupIcon(self,icon):
        stock_ids = gtk.stock_list_ids()
        for stock in stock_ids:
            if stock == icon:
                return stock

    """
    onUserJoin
    When a user joins a channel, provides the user and the index of where to add the user
    """
    def onUserJoin(self,cChannel,cServer,cIndex,cUsr):
        if cUsr.cMode == "":
            cUsr.cTreeIter = cServer.listTreeStore.insert(cChannel.cTreeIter,cIndex,[cUsr.cNick,None])
        else:
            print "onUserJoin, " + cUsr.cMode
            if "*" in cUsr.cMode or "~" in cUsr.cMode:
                print "*",cIndex
                if noUserIcons==False:
                    cUsr.cTreeIter = cServer.listTreeStore.insert(cChannel.cTreeIter,cIndex,[cUsr.cNick,self.lookupIcon("founder")])
                else:
                    cUsr.cTreeIter = cServer.listTreeStore.insert(cChannel.cTreeIter,cIndex,[cUsr.cNick,None])

                return
            elif "!" in cUsr.cMode or "&" in cUsr.cMode:
                if noUserIcons==False:
                    cUsr.cTreeIter = cServer.listTreeStore.insert(cChannel.cTreeIter,cIndex,[cUsr.cNick,self.lookupIcon("admin")])
                else:
                    cUsr.cTreeIter = cServer.listTreeStore.insert(cChannel.cTreeIter,cIndex,[cUsr.cNick,None])
                return
            elif "@" in cUsr.cMode:
                if noUserIcons==False:
                    cUsr.cTreeIter = cServer.listTreeStore.insert(cChannel.cTreeIter,cIndex,[cUsr.cNick,self.lookupIcon("op")])
                else:
                    cUsr.cTreeIter = cServer.listTreeStore.insert(cChannel.cTreeIter,cIndex,[cUsr.cNick,None])
                return
            elif "%" in cUsr.cMode:
                if noUserIcons==False:
                    cUsr.cTreeIter = cServer.listTreeStore.insert(cChannel.cTreeIter,cIndex,[cUsr.cNick,self.lookupIcon("hop")])
                else:
                    cUsr.cTreeIter = cServer.listTreeStore.insert(cChannel.cTreeIter,cIndex,[cUsr.cNick,None])
                return
            elif "+" in cUsr.cMode:
                if noUserIcons==False:
                    cUsr.cTreeIter = cServer.listTreeStore.insert(cChannel.cTreeIter,cIndex,[cUsr.cNick,self.lookupIcon("voice")])
                else:
                    cUsr.cTreeIter = cServer.listTreeStore.insert(cChannel.cTreeIter,cIndex,[cUsr.cNick,None])
                return


    """
    onUserRemove
    When a user either QUIT's ,PART's(from a channel) or is KICKed, provides the iter to remove
    """
    def onUserRemove(self,cChannel,cServer,cTreeIter,usr):
        print "onUserRemove"
        print cChannel.cName
        if usr != None:
            cChannel.cUsers.remove(usr)
        else:
            print "An error occured while trying to remove user from the user list, received",usr ," onUserRemove"

        try:
            cServer.listTreeStore.remove(cTreeIter)
        except:
            print "Error removing user from TreeStore, onUserRemove"

    """
    onLagChange
    When a PONG message is received with the timestamp(LAG1234567890.0)
    """
    def onLagChange(self,cResp,cServer):
        lag=cResp[3].replace(":LAG","").replace("\r","")
        import time
        print str(time.time()) + " " + lag
        lagInt=time.time() - float(lag)
        print "onLagChange " + cResp[3] + " lag = " + str(lagInt)
        self.pingLabel.set_text(str(lagInt))

    """
    onByteSendChange
    When the amount of Bytes to send(which reside in the queue waiting to be sent) changes
    """
    def onByteSendChange(self,cServer,entriesLeft):
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

        #If the "Channel" in the cResp is your nick, add it to the currently selected channel/server
        if cResp.channel.lower() == cServer.cNick.lower():
            #Get the server first, this way if the selected chanel isn't found it's not gonna generate an exception
            rChannel = cServer
            #Get the selected iter
            model, selected = listTreeView.get_selection().get_selected()
            treeiterSelected = listTreeStore.get_value(selected, 0)
            for ch in cServer.channels:
                if ch.cName.lower() == treeiterSelected.lower():
                    rChannel = ch

        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey 
        highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=highlightTagColor)#Red    

        if "ACTION" in cResp.msg:
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
            rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter()," Received CTCP " + cResp.msg.replace("","") + " from " + cResp.nick + "\n")
        else:
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)

            #If it's a Private Message to you not the channel.
            if cResp.channel == cServer.cNick:
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," )",highlightTag)
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick,nickTag)
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),"(",highlightTag)
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),": ",nickTag)
            #If it's a message to the channel
            else:
                rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," " + cResp.nick + ": ",nickTag)

            #Make a tag for the message
            msgTag = rChannel.cTextBuffer.create_tag(None)

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
                    urlTag.connect("event",self.urlTextTagEvent,i[0])
                    endMark=rChannel.cTextBuffer.get_end_iter()
                    startIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1, lineOffsetBAddMsg + cResp.msg.index(i[0]))
                    endIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1,lineOffsetBAddMsg + (cResp.msg.index(i[0]) + len(i[0])))
                    rChannel.cTextBuffer.apply_tag(urlTag,startIter,endIter)
            #URLs END-------------------------------------------------
            #File Paths-----------------------------------------------------
            import re
            m = re.findall("([/|~][A-Za-z/.0-9]+)",cResp.msg)

            if m != None:
                import pango
                for i in m:
                    fileTag = rChannel.cTextBuffer.create_tag(None,underline=pango.UNDERLINE_SINGLE)
                    fileTag.connect("event",self.fileTextTagEvent,i)
                    endMark=rChannel.cTextBuffer.get_end_iter()
                    startIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1, lineOffsetBAddMsg + cResp.msg.index(i))
                    endIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1,lineOffsetBAddMsg + (cResp.msg.index(i) + len(i)))
                    print str(lineOffsetBAddMsg + cResp.msg.index(i)) + "--" + str(lineOffsetBAddMsg + (cResp.msg.index(i) + len(i)))
                    rChannel.cTextBuffer.apply_tag(fileTag,startIter,endIter)
            #File Paths END-------------------------------------------------

        #Get the selected iter
        model, selected = listTreeView.get_selection().get_selected()
        newlySelected = listTreeStore.get_value(selected, 0)
        #Check to see if this channel is selected, and scroll the TextView if it is.
        #If i don't do this the TextView will scroll even when you have another channel/server selected
        #which is a bit annoying
        if newlySelected == rChannel.cName:
            #Scroll the TextView to the bottom...                                   
            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
            chatTextView.scroll_to_mark(endMark,0) 

    #||IRC Events end||#
    """---------------------------------------------"""




def main():
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave() 
    
if __name__ == "__main__":
    Initialize = MainForm()
    main()



