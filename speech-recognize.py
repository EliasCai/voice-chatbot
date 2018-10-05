# -*- coding: utf-8 -*-

import glob
import codecs

from aip import AipSpeech
from os.path import join
import numpy as np
APP_ID = '11416034'
API_KEY = 'vrRYaLDc4WoImkXequrPCknQ'
SECRET_KEY = 'zD72Kp75N5CI9yc4rEepklvo7PtRTps7'
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)
wav_files = glob.glob(os.path.join(name_output,'*','*.wav'))


# 读取文件
def get_file_content(filePath):
    with open(filePath, 'rb') as fp:
        return fp.read()

# 识别本地文件
# dev_pid 语言
# 1536    普通话(支持简单的英文识别)
# 1537    普通话(纯中文识别)
# 1737    英语
# 1637    粤语
# 1837    四川话
# 1936    普通话远场

list.sort(wav_files)
with codecs.open(name_output+'.csv',mode='w', encoding='utf-8') as f:
    for wav_file in wav_files[:]:
        baidu_asr = client.asr(get_file_content(wav_file), 'wav', 16000, {'dev_pid': 1936,})
        if 'result' in baidu_asr:
            print(wav_file,baidu_asr['result'][0])
            f.write(wav_file+','+baidu_asr['result'][0].replace('，','')+','+'\n')
        else:
            print(wav_file,'error')
            f.write(wav_file+','+'error,'+'\n')