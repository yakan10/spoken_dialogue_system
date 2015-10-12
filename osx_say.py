#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import os

class osxSay():
    def __init__(self):
        return
    
    # 話す
    def talk(self, utter):
        os.system("echo %s | say" % utter.encode('utf-8'))
        return

if __name__ == '__main__':
    s = osxSay()
    s.talk(u"庭には二羽にわとりがいる")
