import time
from E7_30_ImmittanceMeter import ImmittanceMeter

meter = ImmittanceMeter("COM2", 0.2)

frequency_list = [100,2000,33000, 3000000] # сканируемые частоты в Гц

for frequency in frequency_list:
    print("frequency now:", frequency)
    meter.set_frequency(frequency)
    time.sleep(1) # если скорость измерений на приборе стоит "средне", ждём первое измерение
    impedance_module, impedance_phase = meter.read_impedance()
    print("Impedance module: ", impedance_module, " Ω")
    print("Impedance phase: ", impedance_phase, " °")
    print("")


meter.close_serial()

