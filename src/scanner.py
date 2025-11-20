import redpitaya_scpi as scpi
from numpy import linspace

import matplotlib.pyplot as plt

from PySide6.QtCore import QObject, QThread, Signal, Slot

class ScanWorker(QObject):
    QObject
    update_signal = Signal(dict)
    finished_scan = Signal(dict)

    def __init__(self):
        super().__init__()
        self._stop = False
        IP = 'rp-f097bc.local'
        self.rp = scpi.scpi(IP)

    def do_single_scan(self):
        # parameters for signal generation and acquisition
        freq = 1
        ampl = 1
        offset = 0

        decimation_factor = 8192
        acq_duration = (decimation_factor * (2**14)) / (125e6)
        gen_duration =  1 / freq
        gen_acq_frac = gen_duration / acq_duration
        freq_factor = 0.955 # emperical factor to compensate small deviations

        num_samples_during_gen = round(2**14 * gen_acq_frac * freq_factor)
        num_samples_segment = round(num_samples_during_gen/4)
        end_seg_1 = 1 * num_samples_segment
        end_seg_2 = 3 * num_samples_segment
        end_seg_3 = 4 * num_samples_segment

        result = { "voltage": linspace(-ampl + offset, ampl + offset, 2*num_samples_segment) }

        # reset generation and acquisition
        self.rp.tx_txt('GEN:RST')
        self.rp.tx_txt('ACQ:RST')

        # setup generation
        self.rp.tx_txt('SOUR1:FUNC TRIANGLE')
        self.rp.tx_txt(f'SOUR1:FREQ:FIX {freq}')
        self.rp.tx_txt(f'SOUR1:VOLT {ampl}')
        self.rp.tx_txt(f'SOUR1:VOLT:OFFS {offset}')
        self.rp.tx_txt('SOUR1:PHAS 180')

        self.rp.tx_txt('SOUR1:BURS:STAT BURST')
        self.rp.tx_txt('SOUR1:BURS:NCYC 1')

        # setup Acqusition
        self.rp.tx_txt(f'ACQ:DEC {decimation_factor}')
        self.rp.tx_txt("ACQ:DATA:Units VOLTS")
        self.rp.tx_txt('ACQ:TRig:DLY 8192')
        self.rp.tx_txt(f'ACQ:SOUR1:GAIN HV')
        self.rp.tx_txt(f'ACQ:SOUR2:GAIN HV')

        self.rp.tx_txt('ACQ:START')
        # time.sleep(1)
        self.rp.tx_txt('ACQ:TRig AWG_NE')
        self.rp.tx_txt('OUTPUT1:STATE ON')
        # time.sleep(1)
        self.rp.tx_txt('SOUR1:TRig:INT')

        
        self.rp.tx_txt('ACQ:AXI:SOUR1:Trig:Pos?')
        signal_trig_pointer = int(self.rp.rx_txt())

        while True:
            self.rp.tx_txt('ACQ:TRig:FILL?')
            if self.rp.rx_txt() == '1':
                break

            self.rp.tx_txt('ACQ:AXI:SOUR1:Write:Pos?')
            signal_curr_pointer = int(self.rp.rx_txt())

            num = signal_curr_pointer - signal_trig_pointer
            num = num + 2**14 if num < 0 else num
            num += num_samples_segment
            if num < 0:
                continue
            num = num if num < 2*num_samples_during_gen else 2*num_samples_during_gen

            self.rp.tx_txt(f'ACQ:AXI:SOUR1:DATA:Start:N? {(signal_trig_pointer+num_samples_during_gen) % (2**14)},{num}>')

            data_string = self.rp.rx_txt()

            data_string = data_string.strip('{}\n\r').replace("  ", "").split(',')
            data = list(map(float, data_string))
            signal_result = {
                "voltage": result["voltage"][:len(data)],
                "signal_clean": data
            }
            self.update_signal.emit(signal_result)

        self.rp.tx_txt(f'ACQ:SOUR2:DATA?')
        data_string = self.rp.rx_txt()

        data_string = data_string.strip('{}\n\r').replace("  ", "").split(',')
        data = list(map(float, data_string))

        result["eit_clean"] = data[end_seg_1:end_seg_2],
        result["eit_split"] = list(reversed(data[end_seg_2:end_seg_3] + data[:end_seg_1])),

        self.rp.tx_txt(f'ACQ:SOUR1:DATA?')
        data_string = self.rp.rx_txt()

        data_string = data_string.strip('{}\n\r').replace("  ", "").split(',')
        data = list(map(float, data_string))

        result["signal_clean"] = data[end_seg_1:end_seg_2]
        result["signal_split"] = list(reversed(data[end_seg_2:end_seg_3] + data[:end_seg_1]))

        self.finished_scan.emit(result)

    def do_repeated_scan(self):
        self._stop = True
        while not self._stop:
            self.do_single_scan
