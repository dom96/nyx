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

from settings import settings

import IRCEvents
#!--End of Import--!#

gobject.threads_init() 

chatTextView = gtk.TextView()#The TextView for the chat

listTreeStore = gtk.TreeStore(str,str,gtk.gdk.Color)#For the list of servers,channels,users
listTreeView = gtk.TreeView
UserListTreeStore = gtk.ListStore(str,str)
UserListTreeView = gtk.TreeView

#Settings
noUserIcons=False
defaultBrowser="x-www-browser"

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

        self.settings = settings.loadSettings()

        #Set up the server, which is connected to at startup in Nyx.
        self.nServer = IRC.server()
        #self.nServer.cAddresses
        for server in self.settings.servers:
            if server.autoconnect == True:
                for address in server.addresses:
                    self.nServer.addresses.append(address)
                break #TODO:Delete this and make it connect to each and every server with autoconnect = True
        #Add the nick and the alternative nicks...
        for nick in self.settings.nicks:
            self.nServer.nicks.append(nick)
        self.nServer.cNick = self.settings.nicks[0]
        self.nServer.cRealname = self.settings.realname
        self.nServer.cUsername = self.settings.username
        self.nServer.listTreeStore = listTreeStore
        self.nServer.settings = self.settings

        #Setup the form
        self.setupForm(self.w,self.nServer)
        self.w.show()
        #Setup the form END
        pDebug(listTreeView)

        self.nServer.listTreeView = listTreeView
        self.nServer.UserListTreeView = UserListTreeView
        self.nServer.chatTextView = chatTextView
        self.nServer.w = self.w

        servers.append(self.nServer)

        #Colors
        serverMsgTag = self.nServer.cTextBuffer.create_tag("serverMsgTag",foreground_gdk=serverMsgTagColor)#Orange
        nickTag = self.nServer.cTextBuffer.create_tag("nickTag",foreground_gdk=nickTagColor)#Blue-ish
        timeTag = self.nServer.cTextBuffer.create_tag("timeTag",foreground_gdk=timeTagColor)#Grey 
        partTag = self.nServer.cTextBuffer.create_tag("partTag",foreground_gdk=partTagColor)#Red
        successTag = self.nServer.cTextBuffer.create_tag("successTag",foreground_gdk=successTagColor)#Green
        highlightTag = self.nServer.cTextBuffer.create_tag("highlightTag",foreground_gdk=highlightTagColor)

        self.nServer.cTextBuffer.insert_with_tags(self.nServer.cTextBuffer.get_end_iter(),"Nyx 0.1 Alpha Initialized\n",serverMsgTag)

        #Add the events.
        IRC.connectEvent("onMotdMsg",IRCEvents.onMotdMsg,self.nServer)
        IRC.connectEvent("onServerMsg",IRCEvents.onServerMsg,self.nServer)
        IRC.connectEvent("onPrivMsg",IRCEvents.onPrivMsg,self.nServer)
        IRC.connectEvent("onJoinMsg",IRCEvents.onJoinMsg,self.nServer)
        IRC.connectEvent("onQuitMsg",IRCEvents.onQuitMsg,self.nServer)
        IRC.connectEvent("onPartMsg",IRCEvents.onPartMsg,self.nServer)
        IRC.connectEvent("onNoticeMsg",IRCEvents.onNoticeMsg,self.nServer)
        IRC.connectEvent("onKickMsg",IRCEvents.onKickMsg,self.nServer)
        IRC.connectEvent("onNickChange",IRCEvents.onNickChange,self.nServer)
        IRC.connectEvent("onModeChange",IRCEvents.onModeChange,self.nServer)
        IRC.connectEvent("onUsersChange",IRCEvents.onUsersChange,self.nServer)
        IRC.connectEvent("onUserJoin",IRCEvents.onUserJoin,self.nServer)
        IRC.connectEvent("onUserRemove",IRCEvents.onUserRemove,self.nServer)
        IRC.connectEvent("onLagChange",self.onLagChange,self.nServer)     
        IRC.connectEvent("onByteSendChange",self.onByteSendChange,self.nServer)
        IRC.connectEvent("onOwnPrivMsg",self.onOwnPrivMsg,self.nServer)
        IRC.connectEvent("onTopicChange",self.onTopicChange,self.nServer); IRC.connectEvent("onTopicChange",IRCEvents.onTopicChange,self.nServer)
        IRC.connectEvent("onChannelModeChange",IRCEvents.onChannelModeChange,self.nServer)
        IRC.connectEvent("onServerDisconnect",IRCEvents.onServerDisconnect,self.nServer)

        #Start a new a connection to a server(Multi threaded), self.nServer contains all the info needed, address etc.
        #gtk.gdk.threads_enter()
        thread.start_new(IRC.connect,(self.nServer,))
        #gtk.gdk.threads_leave()   

    def delete_event(self, widget, event=None, data=None):
        if servers[0].connected==True: servers[0].cSocket.send("QUIT :" + "Nyx IRC Client, visit http://sourceforge.net/projects/nyxirc/\r\n");
        gtk.main_quit()
        return False

    def window_focus(self,widget,event):
        pDebug("FOCUS")
        widget.set_urgency_hint(False)
        widget.focused = True

    def window_unfocus(self,widget,event):
        pDebug("UNFOCUS")
        widget.focused = False

    def setupForm(self,w,nServer):
        global chatTextBuffer
        global chatTextView
        global listTreeStore
        global listTreeView
        global serverAddr
        global UserListTreeStore
        global UserListTreeView

        self.nyx_menu_menu = gtk.Menu()
        #The exit item in the nyx item
        self.exit_menu_item = gtk.ImageMenuItem(gtk.STOCK_QUIT,"Exit")
        self.exit_menu_item.get_children()[0].set_label("_Exit")
        self.exit_menu_item.connect("activate",self.delete_event)
        self.nyx_menu_menu.append(self.exit_menu_item)
        self.exit_menu_item.show()

        #The Nyx item in the menu
        self.nyx_menu = gtk.MenuItem("_Nyx")
        self.nyx_menu.show()
        self.nyx_menu.set_submenu(self.nyx_menu_menu)
        """----------------------------------"""
        #The View item in the menu
        self.view_menu = gtk.MenuItem("_View")
        self.view_menu.show()
        """----------------------------------"""
       
        self.server_menu_menu = gtk.Menu()    
        #The disconnect item in the Server item
        self.disconnect_menu_item = gtk.ImageMenuItem(gtk.STOCK_DISCONNECT,"Disconnect")
        self.disconnect_menu_item.connect("activate",lambda x: servers[0].cSocket.send("QUIT :Nyx IRC Client, visit http://sourceforge.net/projects/nyxirc/\r\n"))
        self.server_menu_menu.append(self.disconnect_menu_item)
        self.disconnect_menu_item.show()

        #The reconnect item in the Server item   
        self.reconnect_menu_item = gtk.ImageMenuItem(gtk.STOCK_CONNECT,"Reconnect")
        self.reconnect_menu_item.get_children()[0].set_label("_Reconnect")
        self.server_menu_menu.append(self.reconnect_menu_item)
        self.reconnect_menu_item.show()

        #The Server item in the menu
        self.server_menu = gtk.MenuItem("_Server")
        self.server_menu.show()
        self.server_menu.set_submenu(self.server_menu_menu)
        """----------------------------------"""
        #The preferences item in the tools item
        self.preferences_menu = gtk.Menu()    
        self.preferences_menu_item = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES,"Preferences")    
        self.preferences_menu.append(self.preferences_menu_item)
        self.preferences_menu_item.show()

        #The Tools item in the menu
        self.tools_menu = gtk.MenuItem("_Tools")
        self.tools_menu.show()
        self.tools_menu.set_submenu(self.preferences_menu)
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
        """TreeView(Channels/Servers) START"""
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

        serverTreeIter = listTreeStore.append(None,[nServer.addresses[0].cAddress, gtk.STOCK_NETWORK,normalChannelColor])
        nServer.cTreeIter = serverTreeIter

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

        # set the cell attributes to the appropriate treestore column
        self.tvcolumn.set_attributes(self.cellpb, stock_id=1)
        self.tvcolumn.set_attributes(self.cell, text=0,foreground_gdk=2)

        #SelectionChanged signal
        selection = self.TreeView1.get_selection()
        selection.connect('changed', self.TreeView_OnSelectionChanged)
        self.TreeView1.connect("focus-in-event",self.TreeView_focusInEvent)
        self.TreeView1.connect("button-press-event",self.TreeView_ButtonPressEvent)
        """TreeView(Channels/Servers) END""" 

        #PING measure
        self.pingLabel = gtk.Label("LAG")
        self.TreeVBox.pack_start(self.pingLabel,False,False,5)
        self.pingLabel.show()

        #Number of messages in the msgBuffer(queue) which are waiting to be sent.
        self.queueLabel = gtk.Label("0 messages")
        self.TreeVBox.pack_start(self.queueLabel,False,False,5)
        self.queueLabel.show()

        self.HPaned2 = gtk.HPaned() #HPaned between the TextView and UserTreeView
        self.HPaned2.show()

        """UserTreeView"""
        self.UserScrolledWindow = gtk.ScrolledWindow()
        self.UserScrolledWindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.HPaned2.pack2(self.UserScrolledWindow,False,True) #Resize = False Shrink = True

        self.UserTreeView = gtk.TreeView(UserListTreeStore)
        #Border..
        self.UserScrolledWindow.set_shadow_type(gtk.SHADOW_IN)      

        self.UserScrolledWindow.add(self.UserTreeView)
        self.UserScrolledWindow.show()
        self.UserTreeView.show()

        UserListTreeView = self.UserTreeView
        self.HPaned2.set_position(420)
    
        # --All the treeView stuff...
        self.usrTvcolumn = gtk.TreeViewColumn(None)
        
        #Add the column, to the treeview
        self.UserTreeView.append_column(self.usrTvcolumn)
        
        self.UserTreeView.set_headers_visible(False)#Don't show the Columns....

        self.usrcellpb = gtk.CellRendererPixbuf()#The renderer for images ??
        self.usrcell = gtk.CellRendererText()#The renderer for text

        self.usrTvcolumn.pack_start(self.usrcellpb, False)
        self.usrTvcolumn.pack_start(self.usrcell, True)

        # set the cell attributes to the appropriate treestore column
        self.usrTvcolumn.set_attributes(self.usrcellpb, stock_id=1)
        self.usrTvcolumn.set_attributes(self.usrcell, text=0,foreground_gdk=2)

        #SelectionChanged signal
        #selection = self.UserTreeView.get_selection()
        #selection.connect('changed', self.TreeView_OnSelectionChanged)
        #self.UserTreeView.connect("focus-in-event",self.TreeView_focusInEvent)
        self.UserTreeView.connect("button-press-event",self.UserTreeView_ButtonPressEvent)
        """UserTreeView END"""

        self.HBox1 = gtk.HBox()
        self.HBox1.pack_end(self.HPaned2)
        self.HPaned1.add(self.HBox1)
        self.HBox1.show()

        """TextView/EntryBox(For typing)/TopicEntryBox"""
        #HBox - For the TextView and EntryBox
        self.VBox1 = gtk.VBox()
        self.HPaned2.pack1(self.VBox1,True,True) #Resize = True Shrink=True
        self.VBox1.show()
        #TopicEntryBox
        self.TopicEntryBox = gtk.Entry()
        self.VBox1.pack_start(self.TopicEntryBox,False,False,5)
        self.TopicEntryBox.show()

        #ScrollWindows for the TextView
        self.chatScrolledWindow = gtk.ScrolledWindow()
        self.chatScrolledWindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.VBox1.pack_start(self.chatScrolledWindow)
        self.chatScrolledWindow.show()

        #TextView - For the actual chat...
        self.chatTextView = gtk.TextView()
        self.chatTextView.set_buffer(nServer.cTextBuffer)
        self.chatTextView.set_wrap_mode(gtk.WRAP_WORD)
        self.chatTextView.set_editable(False)
        self.chatTextView.set_cursor_visible(False)
        self.chatTextView.modify_font(pango.FontDescription("monospace 9"))

        self.chatTextView.connect("populate-popup",IRCEvents.TextView_populatePopup)
        self.newTextViewMenu=[]

        #Borders
        self.chatTextView.set_border_window_size(gtk.TEXT_WINDOW_LEFT,1)
        self.chatTextView.set_border_window_size(gtk.TEXT_WINDOW_RIGHT,1)
        self.chatTextView.set_border_window_size(gtk.TEXT_WINDOW_TOP,1)
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
        """TextView/EntryBox/TopicEntryBox END"""


    def chatEntry_Activate(self,widget):
        if widget.get_text() != "":
            global timeTagColor, nickTagColor
            #Get the current channel...
            if len(servers[0].channels) != 0:
                #Loop through all of the channels
                for i in servers[0].channels:
                    selection = listTreeView.get_selection()
                    model, selected = selection.get_selected()
                    sl=listTreeStore.get_value(selected, 0).replace(" ","")
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
            if sendMsg.entryBoxCheck(wText,servers[0],listTreeView) == False:
                pDebug(dest)
                IRCHelper.sendMsg(servers[0],dest,wText)

            widget.set_text("")

    """TREEVIEW EVENTS!!!!"""
    def TreeView_OnSelectionChanged(self,selection):
        #Get the selected iter
        model, selected = selection.get_selected()
        newlySelected = listTreeStore.get_value(selected, 0)
        pDebug(newlySelected)

        if listTreeStore.iter_parent(selected) != None:#If the selected iter is a channel
            if newlySelected.startswith("#"):
                for i in servers[0].channels:
                    if i.cName == newlySelected:
                        servers[0].listTreeStore.set_value(i.cTreeIter,2,normalChannelColor)
                        chatTextView.set_buffer(i.cTextBuffer)
                        pDebug("NewTextBuffer Channel = " + i.cName)
                        UserListTreeView.set_model(i.UserListStore)
                        pDebug(i.cTopic)
                        self.TopicEntryBox.set_text(i.cTopic)
            #If the selected iter is a user
            else:
                for i in servers[0].channels:
                    pDebug(i.cName.lower() + newlySelected.lower())
                    if i.cName.lower() == newlySelected.lower():
                        servers[0].listTreeStore.set_value(i.cTreeIter,2,normalChannelColor)
                        chatTextView.set_buffer(i.cTextBuffer)
                        pDebug("NewTextBuffer User = " + i.cName)
                        break

        else:#If the selected iter is a server
            for i in servers:
                if i.cAddress == newlySelected:
                    i.listTreeStore.set_value(i.cTreeIter,2,normalChannelColor)
                    chatTextView.set_buffer(i.cTextBuffer)
                    pDebug("NewTextBuffer Server = " + i.cAddress)

                    UserListTreeView.set_model(UserListTreeStore)
                    self.TopicEntryBox.set_text("")

                    break

        #Scroll the TextView to the bottom...
        endMark = chatTextView.get_buffer().create_mark(None, chatTextView.get_buffer().get_end_iter(), True)
        chatTextView.scroll_to_mark(endMark,0)

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

                TreeIter = listTreeStore.get_iter(path)
                TreeIterValue = listTreeStore.get_value(TreeIter,0)

                ServerIter = listTreeStore.iter_parent(TreeIter)
                ServerIterValue = listTreeStore.get_value(ServerIter,0)
                parentServer = object
                for server in servers:
                    if server.cName == ServerIterValue:
                        parentServer = server
                selectedChannel=object
                for ch in parentServer.channels:
                    if ch.cName==TreeIterValue:
                        selectedChannel = ch


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

                TreeIter = listTreeStore.get_iter(path)
                TreeIterValue = listTreeStore.get_value(TreeIter,0)
                pDebug(TreeIterValue)

                if TreeIterValue.startswith("#"):
                    menu.popup(None, None, None, event.button, time)
                elif ServerIter != None:
                    #Hide the modes which are 'Channel only'
                    channel_item.hide()
                    menu.popup(None, None, None, event.button, time)

            return 1

    def closeChannelClick(self, widget, path):
        TreeIter = listTreeStore.get_iter(path)
        TreeIterValue = listTreeStore.get_value(TreeIter,0)
        TreeIterColor = listTreeStore.get_value(TreeIter,2)
        for ch in servers[0].channels:
            if ch.cName == TreeIterValue:
                servers[0].channels.remove(ch)
                break

        listTreeStore.remove(TreeIter)
        if TreeIterColor == normalChannelColor and TreeIterValue.startswith("#"): #TODO: have to change the color of the channel when the user PARTs it.
            servers[0].cSocket.send("PART " + TreeIterValue + " :Leaving\r\n")

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

                #Get the selected iter
                selection = listTreeView.get_selection()
                model, TIselected = selection.get_selected()
                selected = listTreeStore.get_value(TIselected, 0)
                selectedChannel = object
                for ch in servers[0].channels:
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
        lag=cResp[3].replace(":LAG","").replace("\r","").replace("\n","")
        import time
        pDebug(str(time.time()) + " " + lag)
        lagInt=time.time() - float(lag)

        lagMS = lagInt * 1000
        pDebug("onLagChange " + str(cResp[3].replace("\r","").replace("\n","")) + ";lag=" + str(lagInt) + ";lagInMS=" + str(lagMS))
        self.pingLabel.set_text(str(int(round(lagMS))) + " ms")

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
            if cResp.channel.lower().startswith("#") == False:
                for usr in ch.cUsers:
                    if usr.cNick.lower() == cResp.channel.lower():
                        rChannel = usr

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
            m = re.findall("(^[/|~][A-Za-z/.0-9]+)",cResp.msg)

            if m != None:
                import pango
                for i in m:
                    fileTag = rChannel.cTextBuffer.create_tag(None,underline=pango.UNDERLINE_SINGLE)
                    fileTag.connect("event",self.fileTextTagEvent,i)
                    endMark=rChannel.cTextBuffer.get_end_iter()
                    startIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1, lineOffsetBAddMsg + cResp.msg.index(i))
                    endIter=rChannel.cTextBuffer.get_iter_at_line_offset(endMark.get_line() - 1,lineOffsetBAddMsg + (cResp.msg.index(i) + len(i)))
                    pDebug(str(lineOffsetBAddMsg + cResp.msg.index(i)) + "--" + str(lineOffsetBAddMsg + (cResp.msg.index(i) + len(i))))
                    rChannel.cTextBuffer.apply_tag(fileTag,startIter,endIter)
            #File Paths END-------------------------------------------------

        #Get the selected iter
        model, selected = listTreeView.get_selection().get_selected()
        newlySelected = listTreeStore.get_value(selected, 0)
        #Check to see if this channel is selected, and scroll the TextView if it is.
        #If i don't do this the TextView will scroll even when you have another channel/server selected
        #which is a bit annoying
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
        """----------------------"""    
        
        if newlySelected == rChannel.cName:
            #Scroll the TextView to the bottom...                                   
            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
            chatTextView.scroll_to_mark(endMark,0)

    """
    onTopicChange
    When the topic is changed, change the text in TopicTextBox
    """
    def onTopicChange(self,cResp,cServer):
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


