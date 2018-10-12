# coding=utf-8

import sys
import json


from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.parse import quote_plus


API_KEY = 'vrRYaLDc4WoImkXequrPCknQ' # '4E1BG9lTnlSeIf1NQFlrSq6h'
SECRET_KEY = 'zD72Kp75N5CI9yc4rEepklvo7PtRTps7' # '544ca4657ba8002e3dea3ac2f5fdd241'

TEXT = "欢迎使用小和对话机器人。";

# 发音人选择, 0为普通女声，1为普通男生，3为情感合成-度逍遥，4为情感合成-度丫丫，默认为普通女声
PER = 1
# 语速，取值0-15，默认为5中语速
SPD = 6
# 音调，取值0-15，默认为5中语调
PIT = 8
# 音量，取值0-9，默认为5中音量
VOL = 9
# 下载的文件格式, 3：mp3(default) 4： pcm-16k 5： pcm-8k 6. wav
AUE = 3
WAV = 6

FORMATS = {3: "mp3", 4: "pcm", 5: "pcm", 6: "wav"}
FORMAT = FORMATS[WAV]

CUID = "123456PYTHON"

TTS_URL = 'http://tsn.baidu.com/text2audio'


TOKEN_URL = 'http://openapi.baidu.com/oauth/2.0/token'
SCOPE = 'audio_tts_post'  # 有此scope表示有tts能力，没有请在网页里勾选


class TexttoSpeech():

    def __init__(self):
        self.token = self.fetch_token()

    def fetch_token(self):
    #    print("fetch token begin")
        params = {'grant_type': 'client_credentials',
                  'client_id': API_KEY,
                  'client_secret': SECRET_KEY}
        post_data = urlencode(params)

        post_data = post_data.encode('utf-8')
        req = Request(TOKEN_URL, post_data)
        try:
            f = urlopen(req, timeout=5)
            result_str = f.read()
        except URLError as err:
            print('token http response http code : ' + str(err.code))
            result_str = err.read()

        result_str = result_str.decode()

    #    print(result_str)
        result = json.loads(result_str)
    #    print(result)
        if ('access_token' in result.keys() and 'scope' in result.keys()):
            if not SCOPE in result['scope'].split(' '):
                raise DemoError('scope is not correct')
    #        print('SUCCESS WITH TOKEN: %s ; EXPIRES IN SECONDS: %s' % (result['access_token'], result['expires_in']))
            return result['access_token']
        else:
            raise DemoError('MAYBE API_KEY or SECRET_KEY not correct: access_token or scope not found in token response')

    def gen(self, text):
    
        tex = quote_plus(text)  # 此处TEXT需要两次urlencode
        #    print(tex)
        params = {'tok': self.token, 'tex': tex, 'per': PER, 'spd': SPD, 'pit': PIT, 'vol': VOL, 'aue': WAV, 'cuid': CUID,'lan': 'zh', 'ctp': 1}  # lan ctp 固定参数
        data = urlencode(params)
        #    print('test on Web Browser' + TTS_URL + '?' + data)

        req = Request(TTS_URL, data.encode('utf-8'))

        has_error = False
        try:
            f = urlopen(req)
            result_str = f.read()

            has_error = ('Content-Type' not in f.headers.keys() or f.headers['Content-Type'].find('audio/') < 0)
        except  URLError as err:
            print('asr http response http code : ' + str(err.code))
            result_str = err.read()
            has_error = True

        save_file = "error.txt" if has_error else 'result.' + FORMAT
        

        if has_error:
            
            result_str = str(result_str, 'utf-8')
            print("tts api  error:" + result_str)
            return None
        # print("result saved as :" + save_file)
        
        return result_str
        # with open(save_file, 'wb') as of:
            # of.write(result_str)


if __name__ == '__main__':
    
    tts = TexttoSpeech()
    tts.gen(TEXT)
    

    
