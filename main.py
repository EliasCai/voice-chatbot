# -*- coding: utf-8 -*-



import record
import vad
from record import Recorder, RecordingFile
from threading import Thread


    

if __name__ == '__main__':
    from imp import reload
    reload(record)
    reload(vad)

    rec = Recorder(channels=1, rate=16000, frames_per_buffer=480)
    with rec.open('vad.wav', 'wb') as recfile:
        t_rec = Thread(target=recfile.record_to_queue, args=(20.,))
        t_vad = Thread(target=recfile.vad_from_queue)
        
        t_rec.start()     
        t_vad.start()
        t_rec.join()
        t_vad.join()
    
    