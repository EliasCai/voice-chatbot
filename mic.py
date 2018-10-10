# -*- coding: utf-8 -*-

import pyaudio
import wave
import time
from queue import Queue

class Audio(object): # 获取录音设备

    def __init__(self, q=Queue(),
                 channels=1, rate=16000, 
                 frames_per_buffer=2048, 
                 input_device_index=2):
        
        self.q = q
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self._stream = None
        self.input_device_index=input_device_index

    def __enter__(self): 
        return self

    def __exit__(self, exception, value, traceback):
        self.close()
        
    def start(self):
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        # input_device_index=self.input_device_index,
                                        stream_callback=self.get_callback())
        self._stream.start_stream()
        return self

    def stop(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            # self.wavefile.writeframes(in_data)
            self.q.put(in_data)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()

        
        
if __name__ == '__main__':
    
    q = Queue()
    with Audio(q=q) as audio:
        audio.start()
        time.sleep(2)
        audio.stop()
    
    with wave.open('mic.wav','w') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        while not q.empty():
            data = q.get()
            wf.writeframes(data)