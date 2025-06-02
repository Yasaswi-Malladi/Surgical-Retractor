from machine import Pin, I2C
import time

# Adjust these pins if needed:
# I2C(0): SDA = GP0, SCL = GP1
# I2C(1): SDA = GP2, SCL = GP3

i2c = I2C(0, scl=Pin(1), sda=Pin(0), freq=400000)  # 400 kHz is typical for VL53L0X

time.sleep(1)  # Let devices boot up

devices = i2c.scan()

if devices:
    print("I2C devices found:", [hex(d) for d in devices])
else:
    print("No I2C devices found")
