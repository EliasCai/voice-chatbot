# -*- coding: utf-8 -*-

from threading import Thread
from mic import Audio
from queue import Queue
import time, wave, sys
import signal
import snowboydecoder 
from vad import vad_collector
import webrtcvad
from speech_recognize import get_asr_client


interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

class ChatBot():

    def __init__(self, q):

        self.baidu_client = get_asr_client()
        self.q = q
    
    def vad_from_queue(self):
            
        # time.sleep(1)
        vad = webrtcvad.Vad(1)
        print('begin to vad')
        snowboydecoder.play_audio_file()
        # time.sleep(0.5) # 
        segments = vad_collector(16000, 30, 300, vad, self.q, False)
        # segments = list(segments) 
        if segments:
            # self.wavefile.writeframes(segments)    
            res = self.baidu_client.asr(segments, 'wav', 16000, {'dev_pid': 1936,})
            print(res)
        return segments
    
if __name__ == '__main__':
    
    if len(sys.argv) == 1:
        print("Error: need to specify model name")
        print("Usage: python demo.py your.model")
        sys.exit(-1)

    model = sys.argv[1]

    # capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    theads = []
    
    q = Queue()
    bot = ChatBot(q)
    with Audio(q=q, channels=1, rate=16000, 
               frames_per_buffer=480) as audio:
        
        audio.start()
        detector = snowboydecoder.HotwordDetector(model, 
                        sensitivity=0.9)  # 

            
        detector.config(detected_callback=bot.vad_from_queue, # snowboydecoder.play_audio_file,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.2, q=q)

        theads.append( Thread(target=detector.feed_data, args=(q,)) )
        theads.append( Thread(target=detector.start) )
        
        
        for t in theads:
            t.start()
            
        for t in theads:
            t.join()
        print('exit audio')        
        audio.stop()
    
    
    