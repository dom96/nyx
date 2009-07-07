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
#Queue
import Queue
#!--End of Import--!#

gobject.threads_init() 

chatTextView = gtk.TextView()#The TextView for the chat

listTreeStore = gtk.TreeStore(str,str)#For the list of servers,channels,users
listTreeView = gtk.TreeView

#Info
serverAddr = "irc.spotchat.org"
channelName = "#freenode"
port = 6667
nickname = "Nyx"

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
        self.w.set_default_size(750,450)
        

        #Set up the server, which is connected to at startup of Nyx.
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
        IRC.connectEvent("onUsersChange",self.onUsersChange,self.nServer)

        #Start a new a connection to a server(Multi threaded)
        gtk.gdk.threads_enter()
        thread.start_new(IRC.connect,(serverAddr,nickname,"NyxIRC",port,self.nServer))
        gtk.gdk.threads_leave()
        

        
    def delete_event(self, widget, event, data=None):
        gtk.main_quit()
        return False


    def setupForm(self,w):
        global chatTextBuffer
        global chatTextView
        global listTreeStore
        global listTreeView
        global serverAddr
        #The About item in the help item
        self.menu = gtk.Menu()    
        self.menu_item = gtk.ImageMenuItem(gtk.STOCK_ABOUT,"About")    
        self.menu.append(self.menu_item)
        self.menu_item.show()

        #The help item in the menu
        self.help_menu = gtk.MenuItem("Help")
        self.help_menu.show()
        self.help_menu.set_submenu(self.menu)

        #VBox for the Menu
        self.MenuVBox = gtk.VBox()
        w.add(self.MenuVBox)
        self.MenuVBox.show()
        
        #The menu
        self.menu_bar = gtk.MenuBar()
        self.MenuVBox.pack_start(self.menu_bar, False, False, 0)
        self.menu_bar.show()
        #Add the Help item into the menu
        self.menu_bar.append(self.help_menu)

        #HPaned - The split panel
        self.HPaned1 = gtk.HPaned()
        self.MenuVBox.pack_end(self.HPaned1)
        self.HPaned1.show()
    
        #TreeView - Treeview for the channels and servers(like in xchat lol :P)

        #Create the EventBox to change the border color, of it.
        self.treeEb = gtk.EventBox()
        self.treeEb.modify_bg(gtk.STATE_NORMAL,gtk.gdk.Color(red=124 * 257,green=124 * 257 ,blue=124 * 257,pixel=0))  
        self.HPaned1.add(self.treeEb)
        self.treeScrolledWindow = gtk.ScrolledWindow()
        self.treeScrolledWindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

        self.TreeView1 = gtk.TreeView(listTreeStore)
        self.treeScrolledWindow.set_border_width(1)
      
        self.treeEb.add(self.treeScrolledWindow)
        self.treeScrolledWindow.add(self.TreeView1)
        self.treeScrolledWindow.show()
        self.treeEb.show()
        self.TreeView1.show()

        listTreeView = self.TreeView1
        self.HPaned1.set_position(150)
    
        # --All the treeView stuff...
        self.tvcolumn = gtk.TreeViewColumn(None)

        serverTreeIter = listTreeStore.append(None,[serverAddr, gtk.STOCK_NETWORK])

        #Select that row^^        
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
        #EntryBox - For actually speaking
        self.chatEntry = gtk.Entry()
        self.VBox1.pack_end(self.chatEntry,False,False,5)
        self.chatEntry.connect("activate",self.chatEntry_Activate)
        self.chatEntry.show()

    def chatEntry_Activate(self,widget):
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

        if self.entryBoxCheck(wText,servers[0]) == False:
            IRCHelper.sendMsg(servers[0],cChannel.cName,wText)

            #Create the colors
            nickTag = cChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
            timeTag = cChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey 
            global nickname
            cChannel.cTextBuffer.insert_with_tags(cChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
            cChannel.cTextBuffer.insert_with_tags(cChannel.cTextBuffer.get_end_iter()," " + nickname + ": ",nickTag)
            cChannel.cTextBuffer.insert(cChannel.cTextBuffer.get_end_iter(),wText + "\n")

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
    def onMotdMsg(self,cResp,cServer):#When a MOTD message is received and parsed.
        global chatTextView

        cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()) + "\n","timeTag")
        msg = ""
        for m in cResp:
            if m.msg != "":
                msg += ">" + m.msg                

        cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),msg + "\n","serverMsgTag")

        #Scroll the TextView to the bottom...                                   
        endMark = chatTextView.get_buffer().create_mark(None, chatTextView.get_buffer().get_end_iter(), True)
        chatTextView.scroll_to_mark(endMark,0)

        print servers[0].cRealname
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
        
        print servers[0].cRealname
    def onPrivMsg(self,cResp,cServer):#When a normal msg is received and parsed.
        global timeTagColor
        global nickTagColor
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            if ch.cName.lower() == cResp.channel.lower():
                rChannel = ch

        #If the "Channel" in the cResp is your nick, add it to the currently selected channel/server
        if cResp.channel == nickname:
            #Get the selected iter
            model, selected = listTreeView.get_selection().get_selected()
            treeiterSelected = listTreeStore.get_value(selected, 0)
            for ch in cServer.channels:
                if ch.cName.lower() == treeiterSelected:
                    rChannel = ch

        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey     

        if "ACTION" in cResp.msg:
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," @" + " " + cResp.nick,nickTag)
            rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter(),cResp.msg.replace("ACTION","").replace("","") + "\n")
            
        else:
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," " + cResp.nick + ": ",nickTag)
            rChannel.cTextBuffer.insert(rChannel.cTextBuffer.get_end_iter(),cResp.msg + "\n")

        #Get the selected iter
        model, selected = listTreeView.get_selection().get_selected()
        newlySelected = listTreeStore.get_value(selected, 0)
        if newlySelected == rChannel.cName:
            #Scroll the TextView to the bottom...                                   
            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
            chatTextView.scroll_to_mark(endMark,0)     
       
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
        if newlySelected == rChannel.cName:#If the selected channel is this one then scroll otherwise it would scroll it weirdly.
            #Scroll the TextView to the bottom...                                   
            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
            chatTextView.scroll_to_mark(endMark,0)

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
            #Freenode does this, it doesn't give you the channel the person QUIT on, 
            #so i have to check if the person who QUIT is in any of the channels that i'm on, and notify the user on the correct channel.
            for ch in cServer.channels:
                for user in ch.cUsers:
                    if cResp.nick.lower() in user.cNick.lower():
                        rChannel = ch

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

        #Get the selected iter
        model, selected = listTreeView.get_selection().get_selected()
        newlySelected = listTreeStore.get_value(selected, 0)
        if newlySelected == rChannel.cName:
            #Scroll the TextView to the bottom...                                   
            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
            chatTextView.scroll_to_mark(endMark,0)  
    def onNoticeMsg(self,cResp,cServer):
        global highlightTagColor
        global nickTagColor
        global timeTagColor

        print cResp.channel,cServer.cNick
        if cResp.channel != cServer.cNick: 
            #Get the textbuffer for the right channel.
            for ch in cServer.channels:
                if ch.cName.lower() == cResp.channel.lower():
                    rChannel = ch



            print "....."
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
            if newlySelected == rChannel.cName:
                #Scroll the TextView to the bottom...                                   
                endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
                chatTextView.scroll_to_mark(endMark,0)

        else:
            print "!!!!"
            #nickTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
            #timeTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey    
            #highlightTag = cServer.cTextBuffer.create_tag(None,foreground_gdk=highlightTagColor)#Green
            cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),"timeTag")
            cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter()," >","highlightTag")
            cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),cResp.nick,"nickTag")  
            cServer.cTextBuffer.insert_with_tags_by_name(cServer.cTextBuffer.get_end_iter(),"<" + " ","highlightTag")   
            cServer.cTextBuffer.insert(cServer.cTextBuffer.get_end_iter(),cResp.msg + "\n")

            #Get the selected iter
            model, selected = listTreeView.get_selection().get_selected()
            newlySelected = listTreeStore.get_value(selected, 0)
            if newlySelected == cServer.cName:
                #Scroll the TextView to the bottom...                                   
                endMark = cServer.cTextBuffer.create_mark(None, cServer.cTextBuffer.get_end_iter(), True)
                chatTextView.scroll_to_mark(endMark,0)


    def onKickMsg(self,cResp,cServer):
        #Get the textbuffer for the right channel.
        for ch in cServer.channels:
            if ch.cName.lower() == cResp.channel.lower():
                rChannel = ch

        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey    
        highlightTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=highlightTagColor)#Green
    
        print cResp.msg
        personWhoKicked = cResp.nick.split(",")[0]
        personWhoWasKicked = cResp.nick.split(",")[1]

        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," <-- ",highlightTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),personWhoKicked,nickTag)
        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," has kicked " + personWhoWasKicked + "(" + cResp.msg[1:] + ")\n",highlightTag)

        #Get the selected iter
        model, selected = listTreeView.get_selection().get_selected()
        newlySelected = listTreeStore.get_value(selected, 0)
        if newlySelected == rChannel.cName:
            #Scroll the TextView to the bottom...                                   
            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
            chatTextView.scroll_to_mark(endMark,0)

        if personWhoWasKicked == cServer.cNick:
            IRCHelper.join(cServer,rChannel.cName,cServer.listTreeStore)

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
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," <>" + " ",nickTag)
            rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " changed his nick to " + cResp.msg + "\n",partTag)

            #Get the selected iter
            model, selected = listTreeView.get_selection().get_selected()
            newlySelected = listTreeStore.get_value(selected, 0)
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
            #Freenode does this, it doesn't give you the channel the person QUIT on, 
            #so i have to check if the person who QUIT is in any of the channels that i'm on, and notify the user on the correct channel.
            for ch in cServer.channels:
                for user in ch.cUsers:
                    if cResp.nick.lower() in user.cNick.lower():                        
                        rChannel = ch

                        nickTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=nickTagColor)#Blue-ish
                        timeTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=timeTagColor)#Grey    
                        partTag = rChannel.cTextBuffer.create_tag(None,foreground_gdk=partTagColor)#Green

                        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),strftime("[%H:%M:%S]", localtime()),timeTag)
                        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter()," <>" + " ",nickTag)
                        rChannel.cTextBuffer.insert_with_tags(rChannel.cTextBuffer.get_end_iter(),cResp.nick + " changed his nick to " + cResp.msg + "\n",partTag)

                        #Get the selected iter
                        model, selected = listTreeView.get_selection().get_selected()
                        newlySelected = listTreeStore.get_value(selected, 0)
                        if newlySelected == rChannel.cName:
                            #Scroll the TextView to the bottom...                                   
                            endMark = rChannel.cTextBuffer.create_mark(None, rChannel.cTextBuffer.get_end_iter(), True)
                            chatTextView.scroll_to_mark(endMark,0)

                        #Search for the user and change his name.(in the treeview            
                        for user in rChannel.cUsers:
                            if user.cNick == cResp.nick:
                                print "Setting-" + cResp.msg
                                cServer.listTreeStore.set_value(user.cTreeIter,0,cResp.msg)                        
                                user.cNick = cResp.msg


                        #Search the name in the Users
    def onUsersChange(self):
        global listTreeView
        #listTreeView.expand_all()
                            

    #||IRC Events end||#

    #EntryBox Activated, Checks for any commands, like /j or /join.
    def entryBoxCheck(self,text,server):
        if "/j" in text or "/join" in text:
            IRCHelper.join(server,text.replace("/j ","").replace("/join ",""),listTreeStore)
            return True
        if "/msg" in text:
            splitText = text.replace("/msg ","").split(" ")
            count = 0     
            msg = ""       
            for i in splitText:
                if count > 0:
                    msg += i + " "
                count += 1                

            IRCHelper.sendMsg(server,splitText[0],msg)
            return True
        if "/raw" in text:
            splitText = text.replace("/raw ","").split(" ")
            rawMsg = ""
            for i in splitText:
                rawMsg += i + " "
                
            server.cSocket.send(rawMsg + "\r\n")
            return True



        return False

def main():
    gtk.gdk.threads_enter()
    gtk.main()
    gtk.gdk.threads_leave() 
    
if __name__ == "__main__":
    Initialize = MainForm()
    main()



