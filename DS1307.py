from machine import SoftI2C, Pin

sda = 21
scl = 22
freq = 100000

class DS1307:
    def __init__(self, i2c=None):
        self.addr = 0x68

        self.memoryMap = {}
        self.memoryMap['Start addr'] = 0x00
        self.memoryMap['Time reg'] = 0x00
        self.memoryMap['Date reg'] = 0x04
        self.memoryMap['Century reg'] = 0x08

        if i2c is None:
            self.I2C_init()
        else:
            self.i2c = i2c
            try:
                addrList = self.i2c.scan()
            except:
                self.I2C_init()
                addrList = self.i2c.scan()
            finally:
                self.present = self.addr in addrList

    def I2C_init(self):
        self.i2c = SoftI2C( sda = Pin(sda),
                            scl = Pin(scl),
                            freq = freq   )

    @staticmethod
    def bcd_to_dec(bcd):
        dec_lsd = bcd & 0x0F
        dec_msd = (bcd & 0xF0) >> 4
        return dec_lsd + dec_msd * 10

    @staticmethod
    def dec_to_bcd(dec):
        bcd_lsb = dec % 10
        bcd_msb = int(dec / 10)
        return (bcd_msb << 4) | bcd_lsb

    def read_RTC(self):
        if self.present:
            current = bytearray([0]*7)
            self.i2c.readfrom_mem_into(self.addr, self.memoryMap['Start addr'], current)
            current = list(current)

            current.reverse()
            for index, entry in enumerate(current):
                value = DS1307.bcd_to_dec(entry)
                if index == 0:
                    value += 2000
                current[index] = value

            return current
        else:
            print("RTC is not present.")

    def read_time(self):
        if self.present:
            current = bytearray([0]*3)
            self.i2c.readfrom_mem_into(self.addr, self.memoryMap['Time reg'], current)
            current = list(current)

            current.reverse()
            for index, entry in enumerate(current):
                current[index] = DS1307.bcd_to_dec(entry)

            return current
        else:
            print("RTC is not present.")

    def read_date(self):
        if self.present:
            current = bytearray([0]*3)
            self.i2c.readfrom_mem_into(self.addr, self.memoryMap['Date reg'], current)
            current = list(current)

            current.reverse()
            for index, entry in enumerate(current):
                current[index] = DS1307.bcd_to_dec(entry)

            centuryIndicator = self.i2c.readfrom_mem(self.addr, self.memoryMap['Century reg'], 1)
            # current[0] = centuryIndicator * 100 + current[0]
            print(f'centuryIndicator = {centuryIndicator}')

            return current
        else:
            print("RTC is not present.")

    def write_rtc(self, buf):
    # buf must be a list containing [year, month, day, dow, hour, minute, second]
        if self.present:
            if len(buf) != 7:
                print("Invalid input.")
                return

            centuryIndicator = bytearray([int(buf[0] / 100)])
            buf[0] %= 100

            for index, value in enumerate(buf):
                buf[index] = DS1307.dec_to_bcd(value)

            buf.reverse()
            self.i2c.writeto_mem(self.addr, self.memoryMap['Start addr'], bytearray(buf))
            self.i2c.writeto_mem(self.addr, self.memoryMap['Century reg'], bytearray(buf))
        else:
            print("RTC is not present.")

    def write_date(self, buf):
    # buf must be a list containing [year, month, day]
        if self.present:
            if len(buf) != 3:
                print("Invalid input.")
                return

            centuryIndicator = bytearray([int(buf[0] / 100)])
            buf[0] %= 100

            for index, value in enumerate(buf):
                buf[index] = DS1307.dec_to_bcd(value)

            buf.reverse()
            self.i2c.writeto_mem(self.addr, self.memoryMap['Date reg'], bytearray(buf))
            self.i2c.writeto_mem(self.addr, self.memoryMap['Century reg'], bytearray(buf))
        else:
            print("RTC is not present.")