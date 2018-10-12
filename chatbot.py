# -*- coding: utf-8 -*-
"""
server of Flask RESTful 
"""
import urllib.request as ul_re
import json, sys
import uuid
import pandas as pd
import re
from speech_recognize import get_asr_client
from vad import vad_collector
import webrtcvad
import snowboydecoder 
from tts import TexttoSpeech
import pyaudio
import time

bot_config = {}

bot_config['OFFICE_AI'] = "24.xxxxxxxx.2592000.1540460121.282335-14282259"

with open('config.json', 'r') as f:
    bot_config = json.load(f)    
    

    
url = 'https://aip.baidubce.com/rpc/2.0/unit/bot/chat?access_token=' + \
       bot_config['QUERY_AI']
post_data  = {"bot_session": "", # 需要填充
              "log_id": "7758521", 
              "request": {"bernard_level": 0,
                          "client_session": "{\"client_results\":\"\", \"candidate_options\":[]}",
                          "query": "帮我预定高铁票", # 需要填充
                          "query_info": {"asr_candidates": [],
                                         "source": "KEYBOARD",
                                         "type": "TEXT"},
                          "updates": "",
                          "user_id": "88888" }, # 需要填充
              "bot_id": "12782", # 11552
              "version": "2.0"}



# 根据用户ID来管理对话
bot_session = {}



class ChatBot():
    
    def __init__(self, q):
        # 返回的数据字典
        self.answer = {'RetCode': 0,
                  'RetUserID': None,
                  'RetGroupID': None,
                  'RetMsg':None,
                  'RetSessionID':str(uuid.uuid1()),
                  'RetIntent':None}
        
        self.data = self._load_data()
        
        self.baidu_client = get_asr_client()
        self.q = q
        self.tts = TexttoSpeech()
            
    def _load_data(self):
        
        csv_path = 'data/customer.csv'
        
        data = pd.read_csv(csv_path)
        
        return data
    
    def _query_data(self, userid, date):
        
        data = self.data
        return data[(data.userid==userid) & (data.month==date)]
    
    def _match_date(self, s):
        
        year_pattern = '\d{4}-00-00'
        month_pattern = '\d{4}-\d{2}-00'
        day_pattern = '\d{4}-\d{2}-\d{2}'
        
        if re.match(year_pattern, s):
            return 'year'
        elif re.match(month_pattern, s):
            return 'month'
        elif re.match(day_pattern, s):
            return 'day'
        else:
            return None
        
    def do_query_bill(self, userid, slots):
        # print('query_bill', userid, slots)
        
        for slot in slots:
            
            if slot['name'] == 'user_month':
                date = slot['normalized_word'] 
                if self._match_date(date) == 'month':
                    data = self._query_data(userid, date)
                    if len(data) == 0:
                        return '您输入的月份不对，请重新输入'
                    bill = data['bill'].tolist()[0]
                    return '尊敬的客户' + userid + ',您在' + date[:7] + '的话费为' + str(bill)
        
        return '您输入的日期格式不对，请重新输入'

    def do_query_plan(self, userid, slots):
        # print('query_bill', userid, slots)
        
        for slot in slots:
            
            if slot['name'] == 'user_month':
                date = slot['normalized_word'] 
                if self._match_date(date) == 'month':
                    data = self._query_data(userid, date)
                    if len(data) == 0:
                        return '您输入的月份不对，请重新输入'
                    bill = data['plan'].tolist()[0]
                    return '尊敬的客户' + userid + ',您在' + date[:7] + '的套餐为' + str(bill)
        
        return '您输入的日期格式不对，请重新输入'

    def do_query_traffic(self, userid, slots):
        # print('query_bill', userid, slots)
        
        for slot in slots:
            
            if slot['name'] == 'user_month':
                date = slot['normalized_word'] 
                if self._match_date(date) == 'month':
                    data = self._query_data(userid, date)
                    if len(data) == 0:
                        return '您输入的月份不对，请重新输入'
                    bill = data['traffic'].tolist()[0]
                    return '尊敬的客户' + userid + ',您在' + date[:7] + '的流量为' + str(bill)
        
        return '您输入的日期格式不对，请重新输入'
        
    def do_bot_tts(self, bot_say):
        
        print(bot_say)
        say_wav = self.tts.gen(bot_say)
        audio = pyaudio.PyAudio()
        stream_out = audio.open(
            format=8,
            channels=1,
            # input_device_index=2,
            rate=16000, input=False, output=True)
        stream_out.start_stream()
        stream_out.write(say_wav)
        time.sleep(0.1)
        stream_out.stop_stream()
        stream_out.close()
        audio.terminate()
        while not self.q.empty():
            self.q.get()
    
    def __del__(self):
        pass
    
    def post(self, msg, userid='user0'):
        # args = parser.parse_args()
        # userid = 'user1' # args['userid']
        post_data['request']['query'] = msg
        post_data['request']['userid'] = userid
        post_data['bot_session'] = bot_session.get(userid, '')
        encoded_data = json.dumps(post_data).encode('utf-8')
        headers = {'Content-Type': 'application/json'}
    
        r = ul_re.Request(url, data=encoded_data, headers=headers)
        response = ul_re.urlopen(r)
        content = response.read()
        result =  json.loads(str(content.decode('utf-8')))
        if result['error_code'] != 0:
            return None
        intent = result['result']['response']['schema']['intent']
        intent_confidence = result['result']['response']['schema']['intent_confidence']
        slots = result['result']['response']['schema']['slots']
        bot_say = result['result']['response']['action_list'][0]['say']
        
        if result['result']['response']['action_list'][0]['type'] == 'satisfy':
            # 如果意图的词槽已经全部满足，则清空会话
            # bot_session[userid] = ''
            if intent in ['QUERY_BILL', 'QUERY_PLAN', 'QUERY_TRAFFIC']:
                bot_say = getattr(self, 'do_' + intent.lower())(userid, slots)
            else:
                boy_say = '请问我有什么可以帮到您'
        else:
            bot_session[userid] =  result['result']['bot_session']
        
        print(userid, 'ask:', msg)
        self.do_bot_tts(bot_say)
        
        return None

    def vad_from_queue(self):
            
        # time.sleep(1)
        vad = webrtcvad.Vad(1)
        print('waiting for order')
        snowboydecoder.play_audio_file()
        # time.sleep(0.5) # 
        while not self.q.empty():
            self.q.get()
        segments = vad_collector(16000, 30, 300, vad, self.q, False)
        # segments = list(segments) 
        if segments:
            # self.wavefile.writeframes(segments)    
            # with wave.open('vad.wav','w') as wf:
                # wf.setnchannels(1)
                # wf.setsampwidth(2)
                # wf.setframerate(16000)
                # wf.writeframes(segments)
            res = self.baidu_client.asr(segments, 'wav', 16000, {'dev_pid': 1936,})
            if res and res['err_no'] == 0:
                asr = ''.join(res['result'][0].split('，'))
                if len(asr) > 0:
                    print('')
                    # print(asr)
                    self.post(asr,'user2')
        print('waiting for hotword')
        return segments    



if __name__ == '__main__':
    
    from queue import Queue
    bot = ChatBot(Queue())
    data = bot._load_data()
    # sys.exit(0)
    bot.post('我要查话费')
    bot.post('上个月')
    bot.post('今年5月')
    bot.post('')
    bot.post('昨天')
    bot.post('去年')
    bot.post('帮我查流量')
    bot.post('8月')
    bot.post('帮我查套餐')
    bot.post('九月份')

