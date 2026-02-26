import time
from E7_30_ImmittanceMeter import ImmittanceMeter

meter = ImmittanceMeter("COM2", 0.2)
meter.set_frequency(1100) # частота в Гц
meter.set_bias_voltage(0.15) # напряжение смещения в В
time.sleep(1) # если скорость измерений на приборе стоит "средне", ждём первое измерение
impedance_module, impedance_phase = meter.read_impedance()
print("Impedance module: ", impedance_module, " Ω")
print("Impedance phase: ", impedance_phase, " °")

meter.close_serial()

