import serial
import warnings
import time
from decimal import Decimal, ROUND_HALF_UP
import math
import struct


class ImmittanceMeter:
    def __init__(self, COM_PORT, COM_timeout, frame_timeout=3.0):
        self.COM_PORT = COM_PORT
        self.COM_timeout = COM_timeout
        self.frame_timeout = frame_timeout
        self.update_time = 0
        self.measurements_rate = "Fast"
        ser = serial.Serial(
            port=self.COM_PORT,
            baudrate=9600,
            bytesize=serial.EIGHTBITS, # для E7-30 всегда такие...
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=self.COM_timeout,
            inter_byte_timeout=0.3,
            write_timeout=1.0
        )
        self._ser = ser
        self.find_update_time()

    def close_serial(self):
        self._ser.close()

    def test_update_time(self, update_time):
        self.update_time = update_time
        self.set_frequency(25)
        response = self.read_impedance()
        if response is not None:
            return True
        else:
            return False

    def find_update_time(self):
        fast_measurement_time = 0.3
        middle_measurement_time = 1
        measurement_tries = 3

        if any([self.test_update_time(fast_measurement_time) for _ in range(measurement_tries)]):
            self.measurements_rate = "Fast"
        elif any([self.test_update_time(middle_measurement_time) for _ in range(measurement_tries)]):
            self.measurements_rate = "Middle"
        else:
            raise ConnectionError("Update time not found.")

    # ask device name
    def identity(self):
        pass # TO BE DONE

    def set_frequency(self, frequency: int):
        if frequency < 25 or frequency > 3000000:
            raise ValueError("Frequency must be an integer from 25 to 3000000 (Hz).")

        frequency_bytes = frequency.to_bytes(4, "big", signed=False)
        cmd = bytes([0xAA, 0x43]) + frequency_bytes

        self._ser.write(cmd)
        self._ser.flush()
        time.sleep(self.update_time)

    def set_bias_voltage(self, bias_voltage: float):

        if bias_voltage < 0.00 or bias_voltage > 40.00:
            raise ValueError("Bias voltage must be from 0.00 to 40.00 (V).")

        if bias_voltage != round(bias_voltage,2):
            warnings.warn("The bias voltage accuracy is two decimal places.")

        dec = Decimal(str(bias_voltage)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) # значение до сотых
        bias_voltage_x_100 = int(dec * 100)

        bias_voltage_bytes = bias_voltage_x_100.to_bytes(2, "big", signed=False)

        cmd = bytes([0xAA, 0x46]) + bias_voltage_bytes

        self._ser.write(cmd)
        self._ser.flush()
        time.sleep(self.update_time)

    @staticmethod
    def parse_frame(frame):
        if len(frame) < 18:
            raise ValueError("Wrong frame. Reading error.")
        # Два 32-битных float big-endian: |Z| и φ (рад)
        z_mag = struct.unpack('>f', frame[12:16])[0]
        phi_rad = struct.unpack('>f', frame[16:20])[0]
        phi_deg = 180.0 * phi_rad / math.pi
        return z_mag, phi_deg

    def read_impedance(self):
        #self._ser.reset_input_buffer()
        cmd = bytes([0xAA, 0x48])
        self._ser.write(cmd)
        self._ser.flush()
        time.sleep(self.update_time)

        start_time = time.monotonic()
        while time.monotonic() - start_time < self.frame_timeout:
            current_byte = self._ser.read(1)
            #print("Current byte1: ", current_byte)
            if current_byte == bytes([0xAA]):
                current_byte = self._ser.read(1)
                #print("Current byte2: ", current_byte)
                if current_byte == bytes([0x48]):
                    frame = bytes([0xAA, 0x48]) + self._ser.read(18)
                    #print(frame)
                    if len(frame) == 20:
                        return self.parse_frame(frame)
        return None # Если не нашёлся кадр с данными.
