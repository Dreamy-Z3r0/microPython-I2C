import machine
import time

from DS1307 import DS1307

def main():
    sda = machine.Pin(21)
    scl = machine.Pin(22)
    freq = 100000

    i2c = machine.SoftI2C(sda=sda, scl=scl, freq=freq)
    addr = i2c.scan()[-1]

    rtc_ds1307 = DS1307(i2c=i2c)

    current = [2024,4,5,5,13,0,0]

    print("Write operation")
    rtc_ds1307.write_rtc(current)

    time.sleep(5)

    print("Read operation")
    print(rtc_ds1307.read_date())
    print(rtc_ds1307.read_time())


def parse_value(entry, entryType=None, reverse=False):
    if not reverse:
        if 'year' == entryType:
            entry -= 2000

        bcd_lsb = entry % 10
        bcd_msb = int(entry / 10)
        bcd = (bcd_msb << 4) | bcd_lsb

        return bcd 
    else:
        num_lsd = entry & 0x0F
        num_msd = (entry & 0xF0) >> 4
        num = num_lsd + num_msd * 10

        if 'year' == entryType:
            num += 2000

        return num


main()