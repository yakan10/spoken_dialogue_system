# -*- encoding: utf-8 -*-

import urllib2
import json
from ast import literal_eval

APY_KEY = "INPUT_YOUR_API_KEY"

class docomoChat():
    def __init__(self):
        self.__context = None
        return

    def make_req_json(self, utt, nickname="ぺんぎん", sex="女"):
        req = {"utt":utt, "nickname":nickname, "sex":sex}
        if self.__context: req["context"] = self.__context
        return req

    def get_chat(self, utt):
        req_json = self.make_req_json(utt)
        url = "https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue?APIKEY=" + API_KEY
        hrs = {
            "User-Agent": "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7",
            'Content-type': 'application/json; charset=UTF-8',
            'Connection': 'keep-alive'
            }

        req = urllib2.Request(url, data=json.dumps(req_json), headers=hrs)
        p = urllib2.urlopen(req)

        raw = json.loads(p.read().decode('utf-8'))
        #print 'raw: ', raw

        utt = raw["utt"]
        if not self.__context: self.__context = raw["context"]
        return utt

if __name__ == '__main__':
    c = docomoChat()
    ret = c.get_chat("明日の天気は")
    print ret[0].encode('utf-8')
    print ret[1]

