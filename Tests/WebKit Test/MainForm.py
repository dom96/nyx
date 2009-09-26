#!/usr/bin/env python
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import gtkmozembed
import webkit

gobject.threads_init()
webkitWeb = webkit.WebView()
class WebCompare:
    def SetupForm(self,w):
        global mozWeb
        self.HBox1 = gtk.HBox()

        self.HPaned = gtk.HPaned()
        self.HPaned.connect("notify", self.move_handle)
        self.HBox1.pack_start(self.HPaned)

        self.webkitScrolledWindow = gtk.ScrolledWindow()
        self.webkitScrolledWindow.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
        self.webkitScrolledWindow.show()
        self.HPaned.add(self.webkitScrolledWindow)
        self.webkitScrolledWindow.add(webkitWeb)
        webkitWeb.show()

        self.HPaned.show()

        self.w.add(self.HBox1)
        self.HBox1.show()

    def move_handle(self, pane, gparamspec):
        # A widget property has changed.  Ignore unless it is 'position'.
        if gparamspec.name == 'position':
            print 'pane position is now', pane.get_property('position')
            #self.HBox2.set_size_request(self.HPaned.get_position(),self.HPaned.get_size_request()[1])


    def __init__(self):
        global mozWeb
        self.w = gtk.Window(gtk.WINDOW_TOPLEVEL)
    
        self.w.connect("delete_event", self.delete_event)
        self.w.connect("destroy", self.destroy)
        self.SetupForm(self.w)

        self.w.set_default_size(550,450)
        self.w.set_title("WebCompare")
        self.w.show()

        data = """\
<html>
<head>
<title>test</title>
</head>
<body style="font-family:monospace;">

<div style="float:left;text-align:right;border-right:1px solid #000000;">

<span>dom96</span>
<br/>
<span>SomeoneElse</span>
<br/>
<span>AnotherGuy</span>
<br/>
</div>

<div style="float:left;margin-left:5px;">
<span>Message</span>
<br/>
<span>Message</span>
<br/>
<span>Another message lalalala</span>
</div>


</body>
</html>
        """



        #webkitWeb.open("http://www.maddogsoftware.co.uk")
        print dir(webkitWeb)
        webkitWeb.load_html_string(data,"")

    def delete_event(self, widget, event, data=None):
        return False

    def destroy(self, widget, data=None):
        gtk.main_quit()
    def main(self):
        gtk.main()

if __name__ == "__main__":

    main = WebCompare()
    main.main()

