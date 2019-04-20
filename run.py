import sys
import time
import socket

import document_manager

IP = '192.168.16.132'
#IP = '192.168.178.138'
prefix = '20190419-GRAY'
counter = 0

class siglent_sa():
    def __init__(self):
        self._set_generic_measurement()

    def _set_generic_measurement(self):
        self.send('*RST')
        self.send(':BWID 100 kHz')
        self.send(':DISPlay:WINDow:TRACe:Y:SCALe:RLEVel:OFFSet 30')
        self.send(':DISPlay:WINDow:TRACe:Y:RLEVel 40 DBM')
        self.send(':SWEep:SPEed ACCUracy')
        self.send(':CALCulate:MARKer:PEAK:TABLe 1')


    def set_2m(self):
        self._set_generic_measurement()
        self.send(':FREQuency:STOP 1.0 GHz')

    def set_70cm(self):
        self._set_generic_measurement()
        self.send(':FREQuency:STOP 2.0 GHz')

    def acquire_sweep(self):
        self.send(':INITiate:IMMediate')
        stime = float(self.read(':SWEep:TIME?'))
        time.sleep(stime+1)
        return self.read(':TRACe:DATA? 1')

    def send(self, command):
        tmc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tmc.connect((IP, 5025))
        tmc.send(command+'\n')
        tmc.close()

    def read(self, command):
        tmc = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        tmc.connect((IP, 5025))
        tmc.send(command+'\n')
        fh = tmc.makefile()
        line = fh.readline()
        tmc.close()
        return line

sa = siglent_sa()
while True:
    counter += 1
    try:
        model = raw_input('Model: ')
        #model = 'Si5351A'
    except EOFError:
        sys.exit()
    sa.set_2m()
    while True:
        freq = raw_input('Prepare for 2 m acquisition (QRG = 145.000 MHz)')
        freq_2m = 145e6 if not freq else float(freq)*1e6
        trace_2m = sa.acquire_sweep()
        if raw_input('Hit r to redo acquisituion: ') != 'r': break
    sa.set_70cm()
    while True:
        freq = raw_input('Prepare for 70 cm acquisition (QRG = 431.000 MHz)')
        freq_70cm = 431e6 if not freq else float(freq)*1e6
        trace_70cm = sa.acquire_sweep()
        if raw_input('Hit r to redo acquisituion: ') != 'r': break
    print(trace_2m)
    document_manager.process(prefix, counter, model, trace_2m, trace_70cm, freq_2m, freq_70cm)

