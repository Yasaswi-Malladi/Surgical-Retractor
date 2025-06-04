from machine import Pin
import utime

dout = Pin(5, Pin.IN)    # DOUT from HX711
sck = Pin(4, Pin.OUT)    # SCK from HX711
sck.value(0)

def read_hx711():
    # Wait until HX711 is ready
    while dout.value() == 1:
        utime.sleep_us(10)

    count = 0
    for _ in range(24):
        sck.value(1)
        utime.sleep_us(1)
        count = count << 1
        sck.value(0)
        utime.sleep_us(1)
        if dout.value():
            count += 1

    # 25th pulse to set gain to 128
    sck.value(1)
    utime.sleep_us(1)
    sck.value(0)
    utime.sleep_us(1)

    # Convert from 24-bit two's complement
    if count & 0x800000:
        count |= ~0xffffff  # sign extend if negative

    return count

# Tare the scale
print("Taring... Remove any weight.")
utime.sleep(2)
zero_offset = read_hx711()
print("Tared. Zero offset =", zero_offset)

# Main loop
while True:
    raw_val = read_hx711()
    net_val = raw_val - zero_offset

    # Calibration: adjust this scale_factor based on known weight
    scale_factor = -10000  # Change this after calibration
    grams = net_val / scale_factor

    print("Raw:", raw_val, "Net:", net_val, "Grams (approx):", grams)
    utime.sleep(1)

