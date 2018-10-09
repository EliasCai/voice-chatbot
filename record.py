# -*- coding: utf-8 -*-
'''recorder.py
Provides WAV recording functionality via two approaches:
Blocking mode (record for a set duration):
>>> rec = Recorder(channels=2)
>>> with rec.open('blocking.wav', 'wb') as recfile:
...     recfile.record(duration=5.0)
Non-blocking mode (start and stop recording):
>>> rec = Recorder(channels=2)
>>> with rec.open('nonblocking.wav', 'wb') as recfile2:
...     recfile2.start_recording()
...     time.sleep(5.0)
...     recfile2.stop_recording()
'''
import pyaudio
import wave
import time
from queue import Queue
from datetime import datetime
import collections, contextlib, sys, wave, os
import webrtcvad
from threading import Thread
from vad import Frame, vad_collector
from speech_recognize import get_asr_client
 
        

class Recorder(object):
    '''A recorder class for recording audio to a WAV file.
    Records in mono by default.
    '''

    def __init__(self, channels=1, rate=44100, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer

    def open(self, fname, mode='wb'):
        return RecordingFile(fname, mode, self.channels, self.rate,
                            self.frames_per_buffer)

class RecordingFile(object):

    def __init__(self, fname, mode, channels, 
                rate, frames_per_buffer):
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        if fname:
            self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None
        
        self.record_q = Queue(maxsize=0)
        self.vad_q = Queue(maxsize=0)
        self.record_quit = False
        self.baidu_client = get_asr_client()

    def __enter__(self): # 
        return self

    def __exit__(self, exception, value, traceback):
        self.close()

    def record(self, duration):
        # Use a stream with no callback function in blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer)
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            audio = self._stream.read(self.frames_per_buffer)
            # type(audio) = bytes
            self.wavefile.writeframes(audio)
        return audio

    def record_to_queue(self, duration):
        # Use a stream with no callback function in blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer)
        
        duration_per_buffer = self.frames_per_buffer * 1000 / self.rate
        timestamp = 0.
        print('begin record at %s' % datetime.now() )
        for _ in range(int(self.rate / self.frames_per_buffer * duration)):
            if self.record_quit:
                print('break record at %s' % datetime.now() )
                break
            audio = self._stream.read(self.frames_per_buffer)
            # type(audio) = bytes
            self.record_q.put(Frame(audio, timestamp , duration_per_buffer)) # '%s'%datetime.now()
            timestamp += duration_per_buffer
        # self.wavefile.writeframes(audio)
        print('finish record at %s' % datetime.now() )
        return audio
    
    def vad_from_queue(self):
        
        time.sleep(1)
        vad = webrtcvad.Vad(1)
        
        segments = vad_collector(self.rate, 30, 300, vad, self.record_q, False)
        # segments = list(segments)   
        if segments:
            self.wavefile.writeframes(segments)    
            res = self.baidu_client.asr(segments, 'wav', 16000, {'dev_pid': 1936,})
            print(res)
        self.record_quit = True
        return segments
        
    def start_recording(self):
        # Use a stream with a callback in non-blocking mode
        self._stream = self._pa.open(format=pyaudio.paInt16,
                                        channels=self.channels,
                                        rate=self.rate,
                                        input=True,
                                        frames_per_buffer=self.frames_per_buffer,
                                        stream_callback=self.get_callback())
        self._stream.start_stream()
        return self

    def stop_recording(self):
        self._stream.stop_stream()
        return self

    def get_callback(self):
        def callback(in_data, frame_count, time_info, status):
            self.wavefile.writeframes(in_data)
            return in_data, pyaudio.paContinue
        return callback


    def close(self):
        self._stream.close()
        self._pa.terminate()
        self.wavefile.close()

    def _prepare_file(self, fname, mode='wb'):
        wavefile = wave.open(fname, mode)
        wavefile.setnchannels(self.channels)
        wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt16))
        wavefile.setframerate(self.rate)
        return wavefile
        
        
if __name__ == '__main__':
    rec = Recorder(channels=1, rate=16000, frames_per_buffer=480)
    with rec.open('vad.wav', 'wb') as recfile:
        t_rec = Thread(target=recfile.record_to_queue, args=(20.,))
        t_vad = Thread(target=recfile.vad_from_queue)
        
        t_rec.start()     
        t_vad.start()
        t_rec.join()
        t_vad.join()
    # with rec.open('nonblocking.wav', 'wb') as recfile2:
        # recfile2.start_recording()
        # time.sleep(5.0)
        # recfile2.stop_recording()