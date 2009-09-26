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


    if text.startswith("/") and text.startswith("//") == False:
        server.cSocket.send(text.replace("/","") + "\r\n")
        return True




    return False
