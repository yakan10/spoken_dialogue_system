#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import pyaudio
import numpy as np
import wave
from Queue import Queue
import datetime
import threading
import urllib2
import json
import os 

API_KEY="INPUT_YOUR_API_KEY"

class googleRecog():
    def __init__(self):
        ######## config ########
        # pyaudio ------
        self.__chunk = 1024
        self.__format = pyaudio.paInt16
        self.__channels = 1
        self.__rate = 44100
        #self.__rate = 16000

        # Voice Detection ------
        # HEAD/TAIL MARGIN ... 音声区間の前後の余白
        # HEAD/TAIL DETECT DURATION ... 何frame連続してしきい値を超えたら音声区間とするか
        # DETECT_THRESHOLD ... そのframeを音声とみなすしきい値
        self.__head_margin = 10 # frame
        self.__tail_margin = 10 # frame
        self.__head_detect_duration = 10 # frame
        self.__tail_detect_duration = 10 # frame
        self.__detect_threshold = 30
        self.__out_directory = "./audio"
        os.system("mkdir -p " + self.__out_directory)

        # Google Speech API ------
        self.__api_key = API_KEY

        return

    ### 音声の書き出し(wav) ###
    def write_wav(self, data, fname):
        out = wave.open(fname, 'w')
        out.setnchannels(self.__channels)
        out.setsampwidth(2)
        out.setframerate(self.__rate)
        out.writeframes(data)
        out.close()

    ### 音声ストリームを取得し、認識/対話/合成に投げる ###
    def start_recog(self, dialogue, tts):
        p = pyaudio.PyAudio()
        stream = p.open(format = self.__format,
                        channels = self.__channels,
                        rate = self.__rate,
                        input = True,
                        frames_per_buffer = self.__chunk)


        ## 音声区間検出に使う変数を定義
        on_count = 0          # 始端カウント
        off_count = 0         # 終端カウント
        isSpeech = False      # 音声区間フラグ
        detect_tail = False   # 終端検知フラグ
        r_tail = 0            # TAIL_MARGIN > TAIL_DETECT_DURATIONのときの音声区間残り
        hq = Queue(self.__head_margin + self.__head_detect_duration)  # HEAD_MARGIN分の音声
        speech = []           # 音声区間
        print "音声認識開始"

        while(1):
            # streamからデータを読み込み
            data = stream.read(self.__chunk)

           # frameの平均値を取得
            signal = np.frombuffer(data, dtype="int16")
            avg = np.average([abs(signal[i]) for i in range(len(signal)) ])

            # 音声区間検出
            ## 音声区間じゃないとき:しきい値以上の区間が連続すればisSpeech->True
            if not isSpeech and avg > self.__detect_threshold:
                on_count += 1
                if on_count >= self.__head_detect_duration:
                    print "音声を検知しました"
                    isSpeech = True
                    speech = [hq.get_nowait() for i in range(hq.qsize())]
                    on_count = 0
            elif not isSpeech and avg <= self.__detect_threshold:
                on_count = 0
            ## 音声区間のとき:しきい値以下の区間が連続すればisSpeech->False
            elif isSpeech and avg < self.__detect_threshold:
                off_count += 1
                if off_count >= self.__tail_detect_duration:
                    print "音声の終端を検知しました"
                    isSpeech = False
                    detect_tail = True
                    off_count = 0
            elif isSpeech and avg >= self.__detect_threshold:
                off_count = 0
                
            # 音声区間じゃないとき:HEAD_MARGIN分のデータを取得
            if not isSpeech:
                if not hq.empty() and hq.full(): hq.get_nowait()
                hq.put_nowait(data)
            # 音声区間のとき:dataをspeechに追加
            else:
                speech.append(data)

            # 終端を検知した場合:音声区間のデータを取得
            if detect_tail:
                # TAIL_MARGIN分のデータをspeechに追加
                ## TAIL_MARGIN < TAIL_DETECT_DURATIONのとき:
                ## 余分なフレームを削除
                ## TAIL_MARGIN > TAIL_DETECT_DURATIONのとき:
                ## 足りない部分を追加
                if self.__tail_margin < self.__tail_detect_duration:
                    speech = speech[:len(speech) - (self.__tail_detect_duration - self.__tail_margin)]
                    detect_tail = False
                elif self.__tail_margin > self.__tail_detect_duration:
                    r_tail += 1
                    speech.append(data)
                    if r_tail > self.__tail_margin - self.__tail_detect_duration:
                        r_tail = 0
                        detect_tail = False
                else: detect_tail = False
                # detect_tail True>Falseになった瞬間がMARGIN含む音声区間取得完了
                if not detect_tail:
                    data = ''.join(speech)
                    speech = []

                    # 音声を書き出し
                    d = datetime.datetime.today()
                    fname = u"%s/%s%02d%02d_%02d%02d%02d.wav" % \
                    (self.__out_directory, d.year, d.month, d.day, d.hour, d.minute, d.second)
                    self.write_wav(data, fname)

                    ## ここから別スレッドで音声認識実行
                    # 音声合成の音を録音して認識してしまうので、streamを停止
                    stream.stop_stream()
                    # 音声認識 & 雑談対話 & 音声合成
                    t = threading.Thread(target=self.asr_dialogue_tts, args=(fname, dialogue,tts))
                    t.setDaemon(True)
                    t.start()
                    t.join()
                    # streamを再開
                    stream.start_stream()

        print "音声認識終了" 
        # 終了処理
        stream.close()
        p.terminate()

    ### 音声認識 & 雑談対話 ###
    def asr_dialogue_tts(self, fname, dialogue, tts):
        print "音声認識中..."
        recog_result = self.get_recog(fname)
        print "認識結果: " + recog_result.encode('utf-8')

        if isinstance(dialogue, unicode): return
        print "雑談取得中..."
        chat = dialogue.get_chat(recog_result)
        print "雑談対話: " + chat.encode('utf-8')

        if isinstance(tts, unicode): return
        print "音声合成中..."
        tts.talk(chat)

        print "対話完了"
        return
    
    ### google音声認識: 全体 ###
    def get_recog(self, wav):
        # 1: wavをflacに変換
        flac = self.wav2flac(wav)

        # 2: REST APIで認識結果(json)を取得
        raw = self.google_recog(flac)
        
        # 3: jsonから認識テキスト部分を抜く
        return self.json2result(raw)

    ### google音声認識1: wavをflacに変換 ###
    def wav2flac(self, wav):
        flac = wav + ".flac"
        sox_command="sox %s -r 16000 %s" % (wav, flac)
        os.system(sox_command)
        return flac

    ### google音声認識2: REST APIで認識結果(json)を取得
    def google_recog(self, flac):
        f = open(flac, 'rb')
        flac_cont = f.read()
        f.close()

        url = 'https://www.google.com/speech-api/v2/recognize?xjerr=1&client=chromium&lang=ja-JP&maxresults=10&pfilter=0&xjerr=1&key=' + self.__api_key
        hrs = {
            "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",
            'Content-type': 'audio/x-flac; rate=16000'
        }

        req = urllib2.Request(url, data=flac_cont, headers=hrs)
        p = urllib2.urlopen(req)

        raw = p.read()
        p.close()
        return raw

    ### google音声認識3: jsonから認識テキスト部分を抜く
    def json2result(self, raw):
        jsonunits = raw.split(os.linesep)
        res = ""
        
        for unit in jsonunits:
            if not unit: continue
            obj = json.loads(unit)
            alternatives = obj['result']
            if len(alternatives) > 0:
                breakflag = False
                for obj in alternatives:
                    for result in obj['alternative']:
                        res = result['transcript']
                        breakflag = True
                        break
                    if breakflag:
                        break
        return res

def main():
    recog = googleRecog()
    recog.start_recog(u"dummy dialogue", u"dummy tts")

if __name__ == '__main__': main()
