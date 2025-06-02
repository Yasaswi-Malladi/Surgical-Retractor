from machine import Pin, I2C
from vl53l0x import VL53L0X
import time

def setup_tof():
    print("Setting up I2C...")
    sda = Pin(0)
    scl = Pin(1)
    i2c = I2C(id=0, sda=sda, scl=scl)
    print("I2C devices found:", i2c.scan())

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
    """Returns distance in mm with calibration offset"""
    return tof.ping() - 35

# Main
tof = setup_tof()

while True:
    distance = read_distance(tof)
    print(distance, "mm")
    time.sleep(0.1)  # optional delay to reduce print spam
