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
def setup_form(self):
    import gtk
    import pygtk
    
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
    self.disconnect_menu_item.connect("activate",lambda x: self.get_server().cSocket.send("QUIT :Nyx IRC Client, visit http://sourceforge.net/projects/nyxirc/\r\n"))
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

    self.tools_menu_menu = gtk.Menu()    
    #The disconnect item in the Server item
    self.preferences_menu_item = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES,"Preferences")
    self.tools_menu_menu.append(self.preferences_menu_item)
    self.preferences_menu_item.show()

    #The reconnect item in the Server item   
    self.themes_menu_item = gtk.MenuItem(gtk.STOCK_CONNECT,"Themes")
    self.themes_menu_item.get_children()[0].set_label("_Themes")
    self.tools_menu_menu.append(self.themes_menu_item)
    self.themes_menu_item.show()

    #The Tools item in the menu
    self.tools_menu = gtk.MenuItem("_Tools")
    self.tools_menu.show()
    self.tools_menu.set_submenu(self.tools_menu_menu)
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
    self.w.add(self.MenuVBox)
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

    self.TreeView1 = gtk.TreeView(self.listTreeStore)
    #Border..
    self.treeScrolledWindow.set_shadow_type(gtk.SHADOW_IN)      

    self.treeScrolledWindow.add(self.TreeView1)
    self.treeScrolledWindow.show()
    self.TreeView1.show()
    
    self.HPaned1.set_position(150)

    # --All the treeView stuff...
    self.tvcolumn = gtk.TreeViewColumn(None)

    #serverTreeIter = self.listTreeStore.append(None,[self.nServer.addresses[0].cAddress, gtk.STOCK_NETWORK, self.settings.normalTColor])
    #self.nServer.cTreeIter = serverTreeIter

    #Select that row ^^^        
    #self.selection = self.TreeView1.get_selection()
    #self.selection.select_iter(serverTreeIter)
    
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

    """User tree view"""
    self.UserScrolledWindow = gtk.ScrolledWindow()
    self.UserScrolledWindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
    self.HPaned2.pack2(self.UserScrolledWindow,False,True) #Resize = False Shrink = True

    self.UserTreeView = gtk.TreeView(self.UserListTreeStore)
    self.UserTreeView.set_rules_hint(True) #Make odd numbered rows a different color(This doesn't seem to work for me...)
    #Border..
    self.UserScrolledWindow.set_shadow_type(gtk.SHADOW_IN)      

    self.UserScrolledWindow.add(self.UserTreeView)
    self.UserScrolledWindow.show()
    self.UserTreeView.show()

    self.HPaned2.set_position(420)

    # --All the treeView stuff...
    self.usrTvcolumn = gtk.TreeViewColumn(None)
    
    #Add the column, to the treeview
    self.UserTreeView.append_column(self.usrTvcolumn)
    
    self.UserTreeView.set_headers_visible(False)#Don't show the Columns....


    self.usrcellpb = gtk.CellRendererPixbuf() #The renderer for images ??
    self.usrcell = gtk.CellRendererText() #The renderer for text

    self.usrTvcolumn.pack_start(self.usrcellpb, False)
    self.usrTvcolumn.pack_start(self.usrcell, True)

    # set the cell attributes to the appropriate treestore column
    self.usrTvcolumn.set_attributes(self.usrcellpb, stock_id=1)
    self.usrTvcolumn.set_attributes(self.usrcell, text=0,foreground_gdk=2)

    #button-press-event signal
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
    #self.chatTextView.set_buffer(self.nServer.cTextBuffer)
    self.chatTextView.set_wrap_mode(gtk.WRAP_WORD_CHAR)
    self.chatTextView.set_editable(False)
    self.chatTextView.set_cursor_visible(False)
    import pango
    self.chatTextView.modify_font(pango.FontDescription("monospace 9"))
    import IRCEvents
    self.chatTextView.connect("populate-popup", IRCEvents.TextView_populatePopup)
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

    #EntryBox - For the speaking part
    self.chatEntry = gtk.Entry()
    self.VBox1.pack_end(self.chatEntry,False,False,5)
    self.chatEntry.connect("activate",self.chatEntry_Activate)
    self.chatEntry.show()
    """TextView/EntryBox/TopicEntryBox END"""

import IRCEvents
def connect_server(self, settingsServer, IRC, servers):

    nServer = IRC.server()
    nServer.addresses = settingsServer.addresses
    nServer.cName = settingsServer.cName

    nServer.cAddress = nServer.addresses[0]
    #Add the nick and the alternative nicks...
    for nick in self.settings.nicks:
        nServer.nicks.append(nick)
    nServer.cNick = self.settings.nicks[0]
    nServer.cRealname = self.settings.realname
    nServer.cUsername = self.settings.username
    nServer.listTreeStore = self.listTreeStore

    IRC.otherStuff = IRC.other(self.settings, self.theme)

    nServer.listTreeView = self.TreeView1
    nServer.UserListTreeView = self.UserTreeView
    nServer.chatTextView = self.chatTextView
    nServer.w = self.w

    servers.append(nServer)

    connect_events(self, nServer, IRC)

    #Start a new a connection to a server(Multi threaded), self.nServer contains all the info needed, address etc.
    import thread
    thread.start_new(lambda x: nServer.connect(), (None,))

def connect_events(self, server, IRC):
    IRC.connectEvent("onMotdMsg", IRCEvents.onMotdMsg, server)
    IRC.connectEvent("onServerMsg", IRCEvents.onServerMsg, server)
    IRC.connectEvent("onPrivMsg", IRCEvents.onPrivMsg, server)
    IRC.connectEvent("onJoinMsg", IRCEvents.onJoinMsg, server)
    IRC.connectEvent("onQuitMsg", IRCEvents.onQuitMsg, server)
    IRC.connectEvent("onPartMsg", IRCEvents.onPartMsg, server)
    IRC.connectEvent("onNoticeMsg", IRCEvents.onNoticeMsg, server)
    IRC.connectEvent("onKickMsg", IRCEvents.onKickMsg, server)
    IRC.connectEvent("onNickChange", IRCEvents.onNickChange, server)
    IRC.connectEvent("onModeChange", IRCEvents.onModeChange, server)
    IRC.connectEvent("onUsersChange", IRCEvents.onUsersChange, server)
    IRC.connectEvent("onUserJoin", IRCEvents.onUserJoin, server)
    IRC.connectEvent("onUserRemove", IRCEvents.onUserRemove, server)
    IRC.connectEvent("onUserOrderUpdate", IRCEvents.onUserOrderUpdate, server)
    IRC.connectEvent("onLagChange", self.onLagChange, server)     
    IRC.connectEvent("onByteSendChange", self.onByteSendChange, server)
    IRC.connectEvent("onOwnPrivMsg", self.onOwnPrivMsg, server)
    IRC.connectEvent("onTopicChange", self.onTopicChange, server); IRC.connectEvent("onTopicChange", IRCEvents.onTopicChange, server)
    IRC.connectEvent("onChannelModeChange", IRCEvents.onChannelModeChange, server)
    IRC.connectEvent("onServerDisconnect", IRCEvents.onServerDisconnect, server)
    IRC.connectEvent("onKillMsg", IRCEvents.onKillMsg, server)
    
    
    
    
    
    
    
    
