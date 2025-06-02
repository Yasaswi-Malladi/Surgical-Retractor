from machine import I2C
import time

MAX30100_ADDRESS = 0x57

REG_MODE_CONFIGURATION = 0x06
REG_SPO2_CONFIGURATION = 0x07
REG_LED_CONFIGURATION = 0x09
REG_FIFO_WR_PTR = 0x02
REG_FIFO_RD_PTR = 0x04
REG_FIFO_DATA = 0x05

MODE_SPO2 = 0x03

class MAX30100:
    def __init__(self, i2c):
        self.i2c = i2c
        self.address = MAX30100_ADDRESS

        # Reset device
        self._write_reg(REG_MODE_CONFIGURATION, 0x40)  # Reset command
        time.sleep(0.1)

        # Setup mode to SPO2
        self.set_mode(MODE_SPO2)

        # Configure SPO2 sample rate and pulse width
        self._write_reg(REG_SPO2_CONFIGURATION, 0x27)  # 100 Hz sample rate, 1600 us pulse width

        # LED current (red and IR)
        self._write_reg(REG_LED_CONFIGURATION, 0x24)  # 27.1mA red and IR LED current

        # Reset FIFO pointers
        self._write_reg(REG_FIFO_WR_PTR, 0)
        self._write_reg(REG_FIFO_RD_PTR, 0)

    def _write_reg(self, reg, val):
        self.i2c.writeto_mem(self.address, reg, bytes([val]))

    def _read_reg(self, reg, nbytes=1):
        return self.i2c.readfrom_mem(self.address, reg, nbytes)

    def set_mode(self, mode):
        self._write_reg(REG_MODE_CONFIGURATION, mode)

    def read_fifo(self):
        data = self._read_reg(REG_FIFO_DATA, 4)
        # Each measurement is 16 bits (2 bytes)
        ir = (data[0] << 8) | data[1]
        red = (data[2] << 8) | data[3]
        return ir, red
