import time
import matplotlib.pyplot as plt
import redpitaya_scpi as scpi

IP = 'rp-f097bc.local'
rp = scpi.scpi(IP)

# parameters for signal generation and acquisition
freq = 1
ampl = 1

def do_scan():
    # reset generation and acquisition
    rp.tx_txt('GEN:RST')
    rp.tx_txt('ACQ:RST')

    # setup generation
    rp.tx_txt('SOUR1:FUNC TRIANGLE')
    rp.tx_txt(f'SOUR1:FREQ:FIX {freq}')
    rp.tx_txt(f'SOUR1:VOLT {ampl}')
    # rp.tx_txt(f'SOUR1:VOLT:OFFS -0.3')

    rp.tx_txt('SOUR1:BURS:STAT BURST')
    rp.tx_txt('SOUR1:BURS:NCYC 1')

    # setup Acqusition
    rp.tx_txt('ACQ:DEC 8192')
    rp.tx_txt("ACQ:DATA:Units VOLTS")
    rp.tx_txt('ACQ:TRig:DLY 8192')
    rp.tx_txt(f'ACQ:SOUR1:GAIN HV')
    rp.tx_txt(f'ACQ:SOUR2:GAIN HV')

    rp.tx_txt('ACQ:START')
    time.sleep(1)
    rp.tx_txt('ACQ:TRig AWG_NE')
    rp.tx_txt('OUTPUT1:STATE ON')
    time.sleep(1)
    rp.tx_txt('SOUR1:TRig:INT')

    while 1:
        rp.tx_txt('ACQ:TRig:FILL?')
        if rp.rx_txt() == '1':
            break

    rp.tx_txt(f'ACQ:SOUR1:DATA?')
    data_string = rp.rx_txt()

    data_string = data_string.strip('{}\n\r').replace("  ", "").split(',')
    data_src1 = list(map(float, data_string))

    rp.tx_txt(f'ACQ:SOUR2:DATA?')
    data_string = rp.rx_txt()

    data_string = data_string.strip('{}\n\r').replace("  ", "").split(',')
    data_src2 = list(map(float, data_string))

    return (data_src1, data_src2)
