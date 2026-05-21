# ICM-20948 minimal MicroPython test for Raspberry Pi Pico (Thonny)
# - Scans I2C
# - Reads WHO_AM_I (expected 0xEA)
# - Streams accel/gyro/temp in raw units and rough SI units

from machine import Pin, I2C
import time

# -----------------------------
# CONFIG: set these to match your wiring
# -----------------------------
I2C_ID = 0          # Pico: I2C(0) or I2C(1)
SDA_PIN = 0         # GPIO number (GP0 default for I2C0 SDA)
SCL_PIN = 1         # GPIO number (GP1 default for I2C0 SCL)
FREQ = 400_000

# ICM-20948 default I2C addresses: 0x68 or 0x69 (depends on AD0/SDO)
POSSIBLE_ADDRS = (0x68, 0x69)

# -----------------------------
# ICM-20948 register constants
# -----------------------------
REG_BANK_SEL = 0x7F

# Bank 0
WHO_AM_I = 0x00
PWR_MGMT_1 = 0x06
PWR_MGMT_2 = 0x07
INT_PIN_CFG = 0x0F

ACCEL_XOUT_H = 0x2D  # accel/gyro/temp block starts here in bank 0
GYRO_XOUT_H  = 0x33
TEMP_OUT_H   = 0x39

# Bank 2 (gyro/accel config)
GYRO_SMPLRT_DIV = 0x00
GYRO_CONFIG_1   = 0x01
ACCEL_SMPLRT_DIV_1 = 0x10
ACCEL_SMPLRT_DIV_2 = 0x11
ACCEL_CONFIG    = 0x14

# Expected WHO_AM_I for ICM-20948
WHO_AM_I_EXPECTED = 0xEA

def _u16be(b0, b1):
    return (b0 << 8) | b1

def _s16be(b0, b1):
    v = _u16be(b0, b1)
    return v - 65536 if v & 0x8000 else v

class ICM20948:
    def __init__(self, i2c, addr):
        self.i2c = i2c
        self.addr = addr
        self.bank = None

        # Wake up device
        self.set_bank(0)
        self.write8(PWR_MGMT_1, 0x01)  # auto selects best clock; clears sleep
        time.sleep_ms(50)
        self.write8(PWR_MGMT_2, 0x00)  # enable accel + gyro
        time.sleep_ms(10)

        # Configure gyro + accel (simple, known-good settings)
        self.set_bank(2)
        # Sample rate dividers (0 => max ODR for chosen DLPF settings)
        self.write8(GYRO_SMPLRT_DIV, 0x00)
        self.write8(ACCEL_SMPLRT_DIV_1, 0x00)
        self.write8(ACCEL_SMPLRT_DIV_2, 0x00)

        # Gyro: FS=±2000 dps (bits [2:1]=11), DLPF enabled, DLPFCFG=3 (decent smoothing)
        # GYRO_CONFIG_1: [7:5]=GYRO_DLPFCFG, [4]=GYRO_FCHOICE, [2:1]=GYRO_FS_SEL
        # We'll use: DLPFCFG=3 (0b00011 -> <<5), FCHOICE=1 (enable DLPF), FS_SEL=3 (±2000)
        self.write8(GYRO_CONFIG_1, (3 << 5) | (1 << 4) | (3 << 1))

        # Accel: FS=±16g (bits [2:1]=11), DLPF enabled, DLPFCFG=3
        self.write8(ACCEL_CONFIG, (3 << 5) | (1 << 4) | (3 << 1))

        time.sleep_ms(20)
        self.set_bank(0)

    def set_bank(self, bank):
        bank &= 0x03
        if self.bank != bank:
            self.i2c.writeto_mem(self.addr, REG_BANK_SEL, bytes([bank << 4]))
            self.bank = bank
            time.sleep_ms(1)

    def read8(self, reg):
        return self.i2c.readfrom_mem(self.addr, reg, 1)[0]

    def write8(self, reg, val):
        self.i2c.writeto_mem(self.addr, reg, bytes([val & 0xFF]))

    def who_am_i(self):
        self.set_bank(0)
        return self.read8(WHO_AM_I)

    def read_accel_gyro_temp_raw(self):
        self.set_bank(0)
        # Read accel (6), gyro (6), temp (2) from their registers
        # We'll do three reads for clarity (you can optimize later)
        a = self.i2c.readfrom_mem(self.addr, ACCEL_XOUT_H, 6)
        g = self.i2c.readfrom_mem(self.addr, GYRO_XOUT_H, 6)
        t = self.i2c.readfrom_mem(self.addr, TEMP_OUT_H, 2)

        ax = _s16be(a[0], a[1])
        ay = _s16be(a[2], a[3])
        az = _s16be(a[4], a[5])

        gx = _s16be(g[0], g[1])
        gy = _s16be(g[2], g[3])
        gz = _s16be(g[4], g[5])

        temp = _s16be(t[0], t[1])
        return ax, ay, az, gx, gy, gz, temp

    def convert(self, ax, ay, az, gx, gy, gz, temp_raw):
        # With FS=±16g => 2048 LSB/g
        # With FS=±2000 dps => 16.4 LSB/(dps)
        # Temp conversion per InvenSense family: Temp(C) = (TEMP_OUT / 333.87) + 21
        # (This is approximate but good enough for validation.)
        accel_lsb_per_g = 2048.0
        gyro_lsb_per_dps = 16.4

        ax_g = ax / accel_lsb_per_g
        ay_g = ay / accel_lsb_per_g
        az_g = az / accel_lsb_per_g

        gx_dps = gx / gyro_lsb_per_dps
        gy_dps = gy / gyro_lsb_per_dps
        gz_dps = gz / gyro_lsb_per_dps

        temp_c = (temp_raw / 333.87) + 21.0
        return ax_g, ay_g, az_g, gx_dps, gy_dps, gz_dps, temp_c

def find_imu(i2c):
    devices = i2c.scan()
    print("I2C devices found:", [hex(d) for d in devices])

    for addr in POSSIBLE_ADDRS:
        if addr in devices:
            try:
                imu = ICM20948(i2c, addr)
                who = imu.who_am_i()
                print("Found candidate at", hex(addr), "WHO_AM_I =", hex(who))
                if who == WHO_AM_I_EXPECTED:
                    print("ICM-20948 confirmed at", hex(addr))
                    return imu
                else:
                    print("Address responds but WHO_AM_I not expected; still continuing scan.")
            except Exception as e:
                print("Error initializing at", hex(addr), ":", e)
    return None

def main():
    i2c = I2C(I2C_ID, sda=Pin(SDA_PIN), scl=Pin(SCL_PIN), freq=FREQ)
    print("\n--- ICM-20948 MicroPython Test ---")
    print("I2C:", I2C_ID, "SDA=GP{}".format(SDA_PIN), "SCL=GP{}".format(SCL_PIN), "FREQ=", FREQ)

    imu = find_imu(i2c)
    if imu is None:
        print("\nNo confirmed ICM-20948 found.")
        print("Fixes to try:")
        print("- Confirm SDA/SCL pins match your wiring")
        print("- Confirm 3.3V power + GND")
        print("- Check pullups on SDA/SCL (often on breakout already)")
        print("- Try the other I2C bus (I2C_ID=1) or other pins")
        return

    print("\nStreaming accel(g), gyro(dps), temp(C). Move/rotate the board to see changes.\n")

    while True:
        ax, ay, az, gx, gy, gz, t = imu.read_accel_gyro_temp_raw()
        axg, ayg, azg, gxd, gyd, gzd, tc = imu.convert(ax, ay, az, gx, gy, gz, t)

        # Raw and converted print
        print(
            "Araw: {:6d} {:6d} {:6d} | Graw: {:6d} {:6d} {:6d} | Traw: {:6d} || "
            "A(g): {:+.3f} {:+.3f} {:+.3f} | G(dps): {:+.2f} {:+.2f} {:+.2f} | T(C): {:.2f}".format(
                ax, ay, az, gx, gy, gz, t, axg, ayg, azg, gxd, gyd, gzd, tc
            )
        )
        time.sleep_ms(200)

main()
