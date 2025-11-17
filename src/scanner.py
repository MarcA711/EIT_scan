import redpitaya_scpi as scpi
from numpy import linspace

IP = 'rp-f097bc.local'
rp = scpi.scpi(IP)

# # generate values for testing
# def do_scan():
#     # parameters for signal generation and acquisition
#     freq = 1
#     ampl = 1
#     offset = 0

#     decimation_factor = 8192
#     acq_duration = (decimation_factor * (2**14)) / (125e6)
#     gen_duration =  1 / freq
#     gen_acq_frac = gen_duration / acq_duration

#     num_samples_during_gen = round(2**14 * gen_acq_frac)
#     num_samples_segment = round(num_samples_during_gen/4)
#     end_seg_1 = 1 * num_samples_segment
#     end_seg_2 = 3 * num_samples_segment
#     end_seg_3 = 4 * num_samples_segment

def do_scan():
    # parameters for signal generation and acquisition
    freq = 1
    ampl = 1
    offset = 0

    decimation_factor = 8192
    acq_duration = (decimation_factor * (2**14)) / (125e6)
    gen_duration =  1 / freq
    gen_acq_frac = gen_duration / acq_duration

    num_samples_during_gen = round(2**14 * gen_acq_frac)
    num_samples_segment = round(num_samples_during_gen/4)
    end_seg_1 = 1 * num_samples_segment
    end_seg_2 = 3 * num_samples_segment
    end_seg_3 = 4 * num_samples_segment

    # reset generation and acquisition
    rp.tx_txt('GEN:RST')
    rp.tx_txt('ACQ:RST')

    # setup generation
    rp.tx_txt('SOUR1:FUNC TRIANGLE')
    rp.tx_txt(f'SOUR1:FREQ:FIX {freq}')
    rp.tx_txt(f'SOUR1:VOLT {ampl}')
    rp.tx_txt(f'SOUR1:VOLT:OFFS {offset}')

    rp.tx_txt('SOUR1:BURS:STAT BURST')
    rp.tx_txt('SOUR1:BURS:NCYC 1')

    # setup Acqusition
    rp.tx_txt(f'ACQ:DEC {decimation_factor}')
    rp.tx_txt("ACQ:DATA:Units VOLTS")
    rp.tx_txt('ACQ:TRig:DLY 8192')
    rp.tx_txt(f'ACQ:SOUR1:GAIN HV')
    rp.tx_txt(f'ACQ:SOUR2:GAIN HV')

    rp.tx_txt('ACQ:START')
    # time.sleep(1)
    rp.tx_txt('ACQ:TRig AWG_NE')
    rp.tx_txt('OUTPUT1:STATE ON')
    # time.sleep(1)
    rp.tx_txt('SOUR1:TRig:INT')

    while 1:
        rp.tx_txt('ACQ:TRig:FILL?')
        if rp.rx_txt() == '1':
            break

    rp.tx_txt(f'ACQ:SOUR2:DATA?')
    data_string = rp.rx_txt()

    data_string = data_string.strip('{}\n\r').replace("  ", "").split(',')
    data = list(map(float, data_string))

    result = {
        "voltage": linspace(-ampl + offset, ampl + offset, 2*num_samples_segment),
        "eit_clean": list(reversed(data[end_seg_1:end_seg_2])),
        "eit_split": data[end_seg_2:end_seg_3] + data[:end_seg_1],
    }

    rp.tx_txt(f'ACQ:SOUR1:DATA?')
    data_string = rp.rx_txt()

    data_string = data_string.strip('{}\n\r').replace("  ", "").split(',')
    data = list(map(float, data_string))

    result["signal_clean"] = list(reversed(data[end_seg_1:end_seg_2]))
    result["signal_clean"] = data[end_seg_2:end_seg_3] + data[:end_seg_1]

    return result
