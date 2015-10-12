#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from optparse import OptionParser
import gapi
import julius
import docomo_chat
import osx_say

def main():
    # オプション設定
    usage = u"他力本願音声対話システム" + "\n"
    usage += u"オプションの指定方法はREADME.mdを読んでください" + "\n"
    usage += "usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-r", dest="recog", help="speech recognition system [default: google speech api]")
    parser.add_option("-d", dest="dialogue", help="dialogue system [default: docomo api]")
    parser.add_option("-s", dest="tts", help="text to speech system [default: Mac OSX say command]")

    # オプション解析
    (options, args) = parser.parse_args()
    recog_system="google"
    dialogue_system="docomo"
    tts_system="say"
    if options.recog: recog_system = options.recog
    if options.dialogue: dialogue_system = options.dialogue
    if options.tts: tts_system = options.tts
    
    # 認識,対話,合成システムをセット
    recog = None
    dialogue = None
    tts = None
    if recog_system == "google":
        recog = gapi.googleRecog()
    elif recog_system == "julius":
        recog = julius.juliusRecog()
    else:
        print "ERROR: 認識システムの指定がおかしいです"
    
    if dialogue_system == "docomo":
        dialogue = docomo_chat.docomoChat()
    else:
        print "ERROR: 対話システムの指定がおかしいです"
 
    if tts_system == "say":
        tts = osx_say.osxSay()
    else:
        print "ERROR: 合成システムの指定がおかしいです"

    recog.start_recog(dialogue, tts)

if __name__ == '__main__': main()
