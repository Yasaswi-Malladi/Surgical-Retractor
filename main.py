############################
##  Simple Demo
##
##  GM1 2025
##
############################


from machine import Pin, Timer, ADC
from utime import sleep, sleep_ms
from ds18b20_gpio import init_ds18b20, read_ds18b20
from sp02_working import read_spo2_bpm, init_spo2

in1   = Pin(0, Pin.IN)
in2   = Pin(1, Pin.IN)
buzz1 = Pin(2, Pin.OUT) ; buzz1.off()
led1  = Pin(3, Pin.OUT) ; led1.off()
led4  = Pin(4, Pin.OUT) ; led4.off()
led25 = Pin("LED",Pin.OUT)
adc   = ADC(Pin(26))

led25.value(1)

def in2_isr(pin):    # Interrupt Service Routine
  led4.toggle()

#Interrupt request
in2.irq(trigger=Pin.IRQ_FALLING,handler=in2_isr)

tim = Timer()
tim.init(period=500, mode=Timer.PERIODIC, callback=lambda t:led25.toggle())

ds18b20_ok = init_ds18b20()
spo2_ok = init_spo2()
print(ds18b20_ok)
print(spo2_ok)
    
if not ds18b20_ok and not spo2_ok:
        print("No sensors detected. Halting.")
else:
    while True:
        
        # Simple check of the input to pin0 then switch
        # out1 until pin0 drops
        if in1.value():
            led1.on()
        else:
            led1.off()  #or out1.value(0)


        if led1.value() & led4.value():
            buzz1.value(1)
        else:
            buzz1.value(0)

        print(adc.read_u16()) 

        #added below
        if ds18b20_ok:
            print("Reading DS18B20:")
            temps = read_ds18b20()
            for i, (c, f) in enumerate(temps):
                print(f"Sensor {i+1}: {c:.2f}°C / {f:.2f}°F")

        if spo2_ok:
            print("Reading MAX30100:")
            bpm, spo2 = read_spo2_bpm()
            if bpm is not None and spo2 is not None:
                print(f"BPM: {bpm}, SpO2: {spo2}%")
            else:
                print("Waiting for more data from MAX30100...")

        print("-" * 30)
        sleep_ms(5000)