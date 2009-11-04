#!/usr/bin/env python
from IRCLibrary import IRCHelper,ResponseParser
#EntryBox Activated, Checks for any commands, like /j or /join.
def entryBoxCheck(text,server,listTreeView):
    if text.startswith("/j") or text.startswith("/join"):
        IRCHelper.join(server,text.replace("/j ","").replace("/join ",""),server.listTreeStore)
        return True
    if text.startswith("/msg"):
        splitText = text.replace("/msg ","").split(" ")
        count = 0     
        msg = ""
        for i in splitText:
            if count > 0:
                msg += i + " "
            count += 1                

        IRCHelper.cmdSendMsg(server,splitText[0],msg)
        return True
    if text.startswith("/nick"):
        print "NICK " + text.replace("/nick ","")
        server.cSocket.send("NICK " + text.replace("/nick ","") + "\r\n")
        return True     

    if text.startswith("/raw"):
        splitText = text.replace("/raw ","").split(" ")
        rawMsg = ""
        for i in splitText:
            rawMsg += i + " "
                
        server.cSocket.send(rawMsg + "\r\n")
        return True

    """NEED TO MAKE THIS IN A SEPERATE FILE, ALL THE CTCP STUFF."""
    if text.startswith("/version"):
        IRCHelper.sendMsg(server,text.replace("/version ",""),"\x01VERSION\x01")
        #PRIVMSG dom96 :VERSION
        return True
    if text.startswith("/ctcp"):
        splitText = text.replace("/ctcp ","").split()
        try:
            to=splitText[0]#dom96 for example
            ctcp=splitText[1]#VERSION for example
            IRCHelper.sendMsg(server,to,"\x01" + ctcp + "\x01")
        except:
            pass
        return True

    if text.startswith("/me"):
        from IRCLibrary import ResponseParser
        fakecResp=ResponseParser.privMsg()
        fakecResp.msg="ACTION " + text[4:] + ""
        fakecResp.nick=server.cNick
        #Get the selected channel
        model, selected = listTreeView.get_selection().get_selected()
        cSelected = server.listTreeStore.get_value(selected, 0)            
        fakecResp.channel=cSelected

        IRCHelper.sendMsg(server,cSelected,"ACTION " + text[4:] + "")
        return True
    
    if text.startswith("/exec"):
        from IRCLibrary import ResponseParser
        import commands
        output = commands.getoutput(text[5:])
        #Get the selected channel
        model, selected = listTreeView.get_selection().get_selected()
        cSelected = server.listTreeStore.get_value(selected, 0)
        IRCHelper.sendMsg(server,cSelected,output)
        return True

    if text.startswith("/cycle"):
        server.cSocket.send("PART " + text.split(" ")[1] + "\r\n")
        server.cSocket.send("JOIN " + text.split(" ")[1] + "\r\n")
        return True

    if text.startswith("/quit"):
        pDebug("\033[1;34m" + "QUIT :%s" % (text[5:]) + "\\r\\n\033[1;m")
        server.cSocket.send("QUIT :%s\r\n" % (text[5:]))
        return True

    if text.startswith("/") and text.startswith("//") == False:
        pDebug("\033[1;34m" + text[1:] + "\\r\\n\033[1;m")
        server.cSocket.send(text[1:] + "\r\n")
        return True

    return False



import inspect
debugInfo=True
def pDebug(txt):
    if debugInfo:
        func = str(inspect.getframeinfo(inspect.currentframe().f_back).function)
        filename = str(inspect.getframeinfo(inspect.currentframe().f_back).filename);filename = filename.split("/")[len(filename.split("/"))-1]
        print "[\033[1;34m"+str(inspect.currentframe().f_back.f_lineno).rjust(3, '0')+"\033[1;m, " + filename +"(" + func + ")]\n    " + str(txt)
