from machine import Pin, I2C
import time
import MAX30100



def init_spo2(pin_num=1):
    global ds_sensor, roms
    try:
        i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=100000)
        sensor = MAX30100.MAX30100(i2c)

# Simple buffers to hold data for processing
        BUFFER_SIZE = 100
        ir_buffer = []
        red_buffer = []
        return True
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

"""print("Starting measurement...")

while True:
    try:
        ir, red = sensor.read_fifo()

        # Append sensor values to buffers
        ir_buffer.append(ir)
        red_buffer.append(red)

        if len(ir_buffer) > BUFFER_SIZE:
            ir_buffer.pop(0)
            red_buffer.pop(0)

            bpm = calculate_bpm(ir_buffer)
            spo2 = calculate_spo2(ir_buffer, red_buffer)

            print("BPM:", bpm, "SpO2:", spo2, "%")

        time.sleep(0.10)  # 50 Hz approx

    except Exception as e:
        print("Error:", e)
        time.sleep(1)
"""