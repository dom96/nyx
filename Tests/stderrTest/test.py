#!/usr/bin/env python
import sys

class NullDevice:
    def write(self,s):
        open("/home/dominik/Desktop/Projects/Nyx/Tests/stderrTest/err", "a").write(s)
        print s

#sys.stderr=open("/home/dominik/Desktop/Projects/Nyx/Tests/stderrTest/err", "w")
sys.stderr=NullDevice()
raise test("hi")
