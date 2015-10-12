#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import socket
import select
from xml.etree.ElementTree import *

class juliusRecog():
    ### 初期化 ###
    def __init__(self):
        self.__client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ### 設定値の初期化 ####
        self.__host = "localhost"
        self.__port = 10500
        self.__bufsize = 1024
        
        ## 音声合成の声が認識されるのを防止するか
        self.__ttsOn = True
        return
  
    def setTTSFlg(self, flg):
        self.__ttsOn = flg

    ### 認識開始 ###
    def start_recog(self, dialogue, tts):
        self.__client_socket.connect((self.__host, self.__port))
        raw = ""
        isResult = False
        ttsResult = False

        while True:
            inputready, outputready, exceptready = select.select([self.__client_socket], [], [])

            for s in inputready:
                if s == self.__client_socket:
                    message = self.__client_socket.recv(self.__bufsize)
                    if "<RECOGOUT>" in message:
                        isResult = True
                    if isResult:
                        raw += message.decode('utf-8')
                    if "</RECOGOUT>" in message:
                        isResult = False

                        # 音声合成の声に反応するため、1回おきに認識結果を取得する
                        if ttsResult and self.__ttsOn: ttsResult = False
                        else: 
                            ttsResult = True

                            # 文頭/文末記号は削除しないとXML解析でエラー出る
                            raw = raw.replace("<s>", "")
                            raw = raw.replace("</s>", "")

                            # 末尾2行によけいな.と改行が入るため抜く
                            raw = ("\n").join(raw.split("\n")[0:-2])
                            raw = raw.encode('utf-8')

                            # juliusの出力から本文を抜き出す
                            recog_result = self.parse_result(raw)

                            # 取得した認識結果を雑談, 合成に投げる
                            self.dialogue_tts(recog_result, dialogue, tts)

                        # 文字列の初期化
                        raw = ""
        self.__client_socket.close()

    ### Juliusの認識結果から単語を抜き出す ###
    def parse_result(self, raw):
        elem = fromstring(raw)
        ret = ""
        for s in elem.getiterator("SHYPO"):
            for w in s.getiterator("WHYPO"):
                ret += w.attrib['WORD'] + ' '
        return ret

    ### 雑談対話 && 合成 ###
    def dialogue_tts(self, recog_result, dialogue, tts):
        print "認識結果: " + recog_result.encode('utf-8')

        if isinstance(dialogue, unicode): return
        chat = dialogue.get_chat(recog_result)
        print "雑談対話: " + chat.encode('utf-8')

        if isinstance(tts, unicode): return
        print "音声合成中..."
        tts.talk(chat)

        print "対話完了"
        return

if __name__ == '__main__':
    recog = juliusRecog()
    recog.setTTSFlg(False)
    recog.start_recog(u"dummy dialogue", u"dummy tts")
