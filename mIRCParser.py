#!/usr/bin/env python
# coding=utf-8
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

#These are turned to True when one of those is found.
bold=False #    \x02
underline=False # 

#color=False #>Digit<  \x03

def parse(msg):
    global bold
    global underline
    global color

    msg = msg.decode("utf-8")
    returnTuple=[]

    count=0
    startBCount=0
    startUCount=0
    startCCount=[]
    for i in msg:
        #BOLD
        if i == "":
            if bold == False:
                bold = True
                startBCount = count
            else:
                returnTuple.append((normalizeIndex(startBCount, msg), normalizeIndex(count, msg), msg[startBCount:count]))
                bold = False
        #Underline
        if i == "":
            if underline == False:
                underline = True
                startUCount = count
            else:
                returnTuple.append((normalizeIndex(startUCount, msg), normalizeIndex(count, msg), msg[startUCount:count]))
                underline = False
        #Color
        if i == "":
            if len(msg) > count + 2:
                if ((msg[count+1]+msg[count+2]).isdigit() or msg[count+1].isdigit()) == False and ((msg[count+1].isdigit() and 
                msg[count+2] == ",") or (msg[count+1] == "," and msg[count+2].isdigit())) == False:
                    #If there isn't a 'digit' after the ^C
                    if len(startCCount) != 0:
                        #Add all the colors started....
                        #<dom96> could anyone explain why, ^C03GreenText^C05RedText^CThis is black ? should it not be green since i'm only closing one color ?
                        #<Zuthulu> it is intended that $chr(3) without a number stops all previous color codes. if you like a color after it, add the number
                    
                        for colorCount in startCCount:
                            returnTuple.append((normalizeIndex(colorCount, msg), normalizeIndex(count, msg), msg[colorCount:count]))
                        startCCount = []
                else:
                    startCCount.insert(0, count)

            elif len(startCCount) != 0:
                for colorCount in startCCount:
                    returnTuple.append((normalizeIndex(colorCount, msg), normalizeIndex(count, msg), msg[colorCount:count]))
                startCCount = []

        #Normal or if it's the end of the message and there is a color..
        if i == "" or (len(startCCount) != 0 and (count + 1) == len(msg)) or ((count + 1) == len(msg) and (bold == True or underline == True)):
            if bold == True:
                returnTuple.append((normalizeIndex(startBCount, msg), normalizeIndex(count + 1, msg), msg[startBCount:count + 1]))
                bold = False
            if underline == True:
                returnTuple.append((normalizeIndex(startUCount, msg), normalizeIndex(count + 1, msg), msg[startUCount:count + 1]))
                underline = False
            if len(startCCount) != 0:
                #Loop through each color in the 'Colors List'(startCCount)
                for colorCount in startCCount:
                    returnTuple.append((normalizeIndex(colorCount, msg), normalizeIndex(count + 1, msg), msg[colorCount:count + 1]))
                startCCount = []

        count += 1

    returnTuple.reverse()
    return returnTuple

def normalizeIndex(index, msg):
    txtBefore = msg[:index] #Text before the index
    #print txtBefore
    number = 0

    import re
    #print txtBefore
    number = len(txtBefore) - len(removeFormatting(txtBefore))

    #print index,"-",number
    return index - number

def removeFormatting(text):
    import re
    findmIrc = re.finditer("\x03((\d+|)(,\d+|\d+)|)",text)
    txtNoMIrcStuff = text

    minusIndex = 0
    if findmIrc != None:
        for i in findmIrc:
            if "," not in i.group(0):
                startIndex = i.start(0)
                endIndex = i.end(0)         

                if endIndex - startIndex > 3: endIndex -= ((endIndex - startIndex) - 3)
                #print text[startIndex - minusIndex:endIndex - minusIndex]
                #print text[:startIndex - minusIndex] + text[endIndex - minusIndex:]
                txtNoMIrcStuff = txtNoMIrcStuff[:startIndex - minusIndex] + txtNoMIrcStuff[endIndex - minusIndex:]

                minusIndex += endIndex - startIndex
            else:
                startIndex = i.start(0)
                endIndex = i.end(0)   
                txtNoMIrcStuff = txtNoMIrcStuff[:startIndex - minusIndex] + txtNoMIrcStuff[endIndex - minusIndex:]
                minusIndex += endIndex - startIndex

    txtNoMIrcStuff = txtNoMIrcStuff.replace("\x02","").replace("","").replace("","").replace("\x03","")

    return txtNoMIrcStuff


#-------#
# Tests #
#-------#
#print "03www04.05google06.com"
#x = parse("03www04.05google06.com")
#print x

#print "03www04.05google06.com"
#x = parse("       ~    4,4###########0,0      4,4###########   Willkommen              ~")
#print x

#print "03www04.05google06.com"
x = parse("03Green05RedBlack")
print x
                
