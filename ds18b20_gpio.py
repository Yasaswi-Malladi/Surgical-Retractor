# ds18b20_gpio.py
import machine, onewire, ds18x20, time

ds_sensor = None
roms = []

def init_ds18b20(pin_num=22):
    global ds_sensor, roms
    try:
        ds_pin = machine.Pin(pin_num)
        ds_sensor = ds18x20.DS18X20(onewire.OneWire(ds_pin))
        roms = ds_sensor.scan()
        if not roms:
            print("No DS18B20 sensors found.")
            return False
        print('Found DS18B20 ROMs:', roms)
        return True
    except Exception as e:
        print("DS18B20 initialization error:", e)
        return False

def read_ds18b20():
    temperatures = []
    try:
        ds_sensor.convert_temp()
        time.sleep_ms(750)
        for rom in roms:
            tempC = ds_sensor.read_temp(rom)
            tempF = tempC * (9 / 5) + 32
            temperatures.append((tempC, tempF))
            print('ROM:', rom)
            print('temperature (ºC):', "{:.2f}".format(tempC))
            print('temperature (ºF):', "{:.2f}".format(tempF))
        return temperatures
    except Exception as e:
        print("DS18B20 read error:", e)
        return []