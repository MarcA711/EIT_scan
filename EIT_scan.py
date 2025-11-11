import numpy as np
import matplotlib.pyplot as plt
import redpitaya_scpi as scpi

IP = 'rp-f097bc.local'

dec = 65536
trig_lvl = 0.055
data_units = 'volts'
data_format = 'ascii'
acq_trig = 'CH2_NE'

rp = scpi.scpi(IP)

rp.tx_txt('ACQ:RST')

rp.tx_txt(f"ACQ:DEC:Factor {dec}")
rp.tx_txt(f"ACQ:DATA:Units {data_units.upper()}")
rp.tx_txt(f"ACQ:DATA:FORMAT {data_format.upper()}")

rp.tx_txt(f"ACQ:TRig:LEV {trig_lvl}")

rp.tx_txt('ACQ:START')
rp.tx_txt(f"ACQ:TRig {acq_trig}")

while 1:
    rp.tx_txt('ACQ:TRig:FILL?')
    if rp.rx_txt() == '1':
        break

rp.tx_txt('ACQ:SOUR2:DATA?')
buff_string = rp.rx_txt()
buff_string = buff_string.strip('{}\n\r').replace("  ", "").split(',')
buff = np.array(buff_string).astype(np.float64)

plt.plot(buff)
plt.ylabel('Voltage')
plt.show()