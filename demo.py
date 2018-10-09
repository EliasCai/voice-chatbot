# -*- coding: utf-8 -*-
import record
import vad
from record import Recorder, RecordingFile
from threading import Thread

import hotword.snowboydecoder as snowboydecoder
import sys
import signal

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted



def after_hotword():
    with rec.open('vad.wav', 'wb') as recfile:
        t_rec = Thread(target=recfile.record_to_queue, args=(20.,))
        t_vad = Thread(target=recfile.vad_from_queue)
        print('begin to record vad')
        t_rec.start()     
        t_vad.start()
        t_rec.join()
        t_vad.join()

if __name__ == '__main__':

    rec = Recorder(channels=1, rate=16000, frames_per_buffer=480)
    
    if len(sys.argv) == 1:
        print("Error: need to specify model name")
        print("Usage: python demo.py your.model")
        sys.exit(-1)

    model = sys.argv[1]

    # capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
    print('Listening... Press Ctrl+C to exit')

    # main loop
    detector.start(detected_callback=after_hotword,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)

    detector.terminate()
