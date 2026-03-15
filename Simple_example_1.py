from E7_30_ImmittanceMeter_V2 import ImmittanceMeter

meter = ImmittanceMeter("COM2", 0.2) # некоторое время будет инициализация
print("Reading rate:", meter.measurements_rate) # вычисление выбранной на приборе скорости измерения
meter.set_frequency(1100) # частота в Гц
meter.set_bias_voltage(0.15) # напряжение смещения в В
impedance_module, impedance_phase = meter.read_impedance()
print("Impedance module: ", impedance_module, " Ω")
print("Impedance phase: ", impedance_phase, " °")
meter.close_serial()
