from machine import Pin, I2C
import time
import MAX30100
from vl53l0x import VL53L0X
import time
# ds18b20_gpio.py
import onewire, ds18x20

def init_spo2(pin_num=3):
    global ds_sensor, roms
    try:
        i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=100000)
        sensor = MAX30100.MAX30100(i2c)

# Simple buffers to hold data for processing
        BUFFER_SIZE = 100
        ir_buffer = []
        red_buffer = []
        return sensor
    except Exception as e:
        print("spo2 initialization error:", e)
        return False 

def calculate_bpm(ir_values, fs=100):
    """Estimate BPM from IR signal peaks"""
    import math

    if len(ir_values) < 3:
        return 0

    peaks = []
    for i in range(1, len(ir_values) - 1):
        if ir_values[i] > ir_values[i-1] and ir_values[i] > ir_values[i+1] and ir_values[i] > 20000:
            peaks.append(i)

    if len(peaks) < 2:
        return 0

    # Calculate average interval between peaks in samples
    intervals = [peaks[i+1] - peaks[i] for i in range(len(peaks)-1)]
    avg_interval = sum(intervals) / len(intervals)

    bpm = 60 * fs / avg_interval
    return int(bpm)

def calculate_spo2(ir_values, red_values):
    """Estimate SpO2 from ratio of ratios method"""
    if len(ir_values) == 0 or len(red_values) == 0:
        return 0

    ir_ac = max(ir_values) - min(ir_values)
    ir_dc = sum(ir_values) / len(ir_values)

    red_ac = max(red_values) - min(red_values)
    red_dc = sum(red_values) / len(red_values)

    if ir_dc == 0 or red_dc == 0:
        return 0

    ratio = (red_ac / red_dc) / (ir_ac / ir_dc)

    # Approximate linear formula to convert ratio to SpO2%
    spo2 = 110 - 25 * ratio

    if spo2 > 100:
        spo2 = 100
    elif spo2 < 0:
        spo2 = 0

    return int(spo2)

def read_spo2_bpm():
    try:
        ir, red = sensor.read_fifo()
        ir_buffer.append(ir)
        red_buffer.append(red)
        if len(ir_buffer) > BUFFER_SIZE:
            ir_buffer.pop(0)
            red_buffer.pop(0)
            bpm = calculate_bpm(ir_buffer)
            spo2 = calculate_spo2(ir_buffer, red_buffer)
            print("BPM:", bpm, "SpO2:", spo2, "%")
            return bpm, spo2
    except Exception as e:
        print("MAX30100 read error:", e)
    return None, None


def wait_for_tof_sensor(i2c):
    #Keep scanning until VL53L0X sensor is found on I2C bus.
    print("Scanning for VL53L0X sensor...")
    while True:
        devices = i2c.scan()
        if devices:
            print("Found I2C devices:", devices)
            return
        print("No devices found, retrying...")
        time.sleep(0.5)

def setup_tof():
    print("Setting up I2C...")

    i2c = I2C(id=0, sda=Pin(0), scl=Pin(1))

    wait_for_tof_sensor(i2c)

    print("Creating VL53L0X object...")
    tof = VL53L0X(i2c)

    # Configure measurement timing budget
    budget = tof.measurement_timing_budget_us
    print("Default timing budget:", budget)
    tof.set_measurement_timing_budget(40000)

    # Set VCSEL pulse periods
    tof.set_Vcsel_pulse_period(tof.vcsel_period_type[0], 12)
    tof.set_Vcsel_pulse_period(tof.vcsel_period_type[1], 8)

    return tof

def read_distance(tof):
    #Returns distance in mm with calibration offset
    return tof.ping() - 35


def init_ds18b20(pin_num=22):
    global ds_sensor, roms
    try:
        ds_pin = Pin(pin_num)
        ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
        roms = ds_sensor.scan()
        if not roms:
            print("No DS18B20 sensors found.")
            return None
        print('Found DS18B20 ROMs:', roms)
        return ds_sensor
    except Exception as e:
        print("DS18B20 initialization error:", e)
        return None

def read_ds18b20():
    global ds_sensor, roms
    temperatures = []
    try:
        if ds_sensor is None or not roms:
            return []
        ds_sensor.convert_temp()
        time.sleep(0.75)  # allow sensor to convert temp fully
        for rom in roms:
            tempC = ds_sensor.read_temp(rom)
            print('temperature (ºC):', "{:.2f}".format(tempC))
            temperatures.append(tempC)
        return temperatures
    except Exception as e:
        print("DS18B20 read error:", e)
        return []

# Main initialization
ds_sensor = init_ds18b20()
tof = setup_tof()
sensor = init_spo2()

if not sensor:
    print("Failed to initialize SpO2 sensor")

BUFFER_SIZE_SPO2 = 10
BUFFER_SIZE_TOF = 10

ir_buffer = []
red_buffer = []
tof_buffer = []

spo2_print_counter = 0
tof_print_counter = 0
temp_print_counter = 0

while True:
    try:
        # ToF reading
        distance = tof.ping()
        if distance is not None:
            calibrated_dist = distance - 35
            tof_buffer.append(calibrated_dist)
            if len(tof_buffer) > BUFFER_SIZE_TOF:
                tof_buffer.pop(0)

        tof_print_counter += 1
        if tof_print_counter >= BUFFER_SIZE_TOF:
            avg_distance = sum(tof_buffer) / len(tof_buffer) if tof_buffer else 0
            print(f"Avg ToF distance (last {BUFFER_SIZE_TOF} samples): {avg_distance:.2f} mm")
            tof_print_counter = 0

        # SpO2 reading
        if sensor:
            ir, red = sensor.read_fifo()
            ir_buffer.append(ir)
            red_buffer.append(red)
            if len(ir_buffer) > BUFFER_SIZE_SPO2:
                ir_buffer.pop(0)
                red_buffer.pop(0)

            spo2_print_counter += 1
            if spo2_print_counter >= BUFFER_SIZE_SPO2:
                bpm = calculate_bpm(ir_buffer)
                spo2_val = calculate_spo2(ir_buffer, red_buffer)
                print(f"BPM: {bpm}, SpO2: {spo2_val}%")
                spo2_print_counter = 0

        # Temperature reading every 15 loops (~0.3s if sleep=0.02)
        temp_print_counter += 1
        if temp_print_counter > 15:
            temps = read_ds18b20()
            temp_print_counter = 0

        time.sleep(0.02)

    except Exception as e:
        print("Error:", e)
        time.sleep(1)

