# ============================================================
# Program Kontrol Motor ESP32 via Serial (Auto-Detect Port)
# Fitur: ON/OFF + Naik/Turun kecepatan (PWM)
# ============================================================

import serial
import serial.tools.list_ports
import time
import sys

# ============================================
# KONFIGURASI
# ============================================
BAUDRATE = 115200

ESP32_KEYWORDS = [
    "cp210", "cp2102", "cp210x",
    "ch340", "ch341", "ch34x",
    "ftdi", "ft232",
    "usb-serial", "usb serial",
    "usb uart", "uart bridge",
    "silicon labs",
    "espressif", "esp32",
]

ESP32_VID_PID = {
    (0x10C4, 0xEA60), (0x10C4, 0xEA70),
    (0x1A86, 0x7523), (0x1A86, 0x55D4),
    (0x0403, 0x6001), (0x0403, 0x6015),
    (0x303A, 0x1001),
}

DUTY_STEP = 10   # selisih kenaikan/penurunan di sisi Python (informatif)


# ============================================
# Auto-detect port ESP32
# ============================================
def list_serial_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        print("Tidak ada port serial yang terdeteksi.")
        return []
    print("Port serial yang tersedia:")
    for p in ports:
        vid_pid = ""
        if p.vid is not None and p.pid is not None:
            vid_pid = f" [VID:PID={p.vid:04X}:{p.pid:04X}]"
        print(f"  - {p.device} : {p.description}{vid_pid}")
    return list(ports)


def deteksi_port_esp32(verbose=True):
    ports = serial.tools.list_ports.comports()
    if not ports:
        if verbose:
            print("[!] Tidak ada port serial yang terdeteksi.")
        return None

    kandidat = []
    for p in ports:
        desc = (p.description or "").lower()
        mfg  = (p.manufacturer or "").lower()
        hwid = (p.hwid or "").lower()
        teks = f"{desc} {mfg} {hwid}"

        skor = 0
        if p.vid is not None and p.pid is not None:
            if (p.vid, p.pid) in ESP32_VID_PID:
                skor += 100
        for kw in ESP32_KEYWORDS:
            if kw in teks:
                skor += 50
                break
        if "bluetooth" in teks:
            skor -= 200

        if skor > 0:
            kandidat.append((skor, p))

    if not kandidat:
        non_bt = [p for p in ports
                  if "bluetooth" not in (p.description or "").lower()]
        if len(non_bt) == 1:
            if verbose:
                print(f"[i] Hanya ada 1 port non-Bluetooth: {non_bt[0].device}")
            return non_bt[0].device
        if verbose:
            print("[!] Port ESP32 tidak dapat dideteksi otomatis.")
        return None

    kandidat.sort(key=lambda x: x[0], reverse=True)
    if verbose:
        print("Kandidat port ESP32 (skor tertinggi = paling mungkin):")
        for skor, p in kandidat:
            print(f"  [{skor:>4}] {p.device} : {p.description}")
    return kandidat[0][1].device


# ============================================
# Koneksi serial
# ============================================
def buka_koneksi(port, baudrate=115200):
    try:
        ser = serial.Serial(port, baudrate, timeout=1)
        time.sleep(2)
        print(f"Terhubung ke ESP32 di {port} @ {baudrate} baud")
        return ser
    except serial.SerialException as e:
        print(f"Gagal membuka port {port}: {e}")
        return None


# ============================================
# Kirim perintah & baca balasan
# ============================================
def kirim_perintah(ser, perintah: str):
    """
    Mengirim perintah ke ESP32 (diakhiri newline).
    Perintah valid: '0', '1', '+', '-', 'PWM:xxx'
    """
    ser.write((perintah + "\n").encode("utf-8"))
    ser.flush()
    time.sleep(0.15)

    # Baca semua baris balasan yang tersedia
    while ser.in_waiting > 0:
        balasan = ser.readline().decode("utf-8", errors="ignore").strip()
        if balasan:
            print(f"ESP32: {balasan}")
        time.sleep(0.05)


# Wrapper perintah
def motor_on(ser):
    print(">> Motor ON")
    kirim_perintah(ser, "1")

def motor_off(ser):
    print(">> Motor OFF")
    kirim_perintah(ser, "0")

def kecepatan_naik(ser, step=DUTY_STEP):
    """Naikkan kecepatan motor sebanyak `step` (default 10)."""
    print(f">> Kecepatan +{step}")
    kirim_perintah(ser, "+")

def kecepatan_turun(ser, step=DUTY_STEP):
    """Turunkan kecepatan motor sebanyak `step` (default 10)."""
    print(f">> Kecepatan -{step}")
    kirim_perintah(ser, "-")

def set_pwm(ser, duty: int):
    """Set duty cycle langsung (0-255)."""
    duty = max(0, min(255, int(duty)))
    print(f">> Set PWM = {duty}")
    kirim_perintah(ser, f"PWM:{duty}")


# ============================================
# PROGRAM UTAMA
# ============================================
if __name__ == "__main__":
    print("=" * 50)
    list_serial_ports()
    print("=" * 50)

    PORT = deteksi_port_esp32()
    if PORT is None:
        print("Program dihentikan: port ESP32 tidak ditemukan.")
        sys.exit(1)
    print(f"\n>> Port ESP32 terpilih: {PORT}")

    esp32 = buka_koneksi(PORT, BAUDRATE)

    if esp32 is None:
        print("Koneksi gagal. Periksa kembali PORT dan kabel USB.")
    else:
        try:
            # ---- Demo urutan kontrol motor ----
            print("\n--- Mulai urutan kontrol motor ---")

            motor_on(esp32)
            time.sleep(2)

            # Naikkan kecepatan 3x
            for _ in range(3):
                kecepatan_naik(esp32)
                time.sleep(1)

            # Turunkan kecepatan 2x
            for _ in range(2):
                kecepatan_turun(esp32)
                time.sleep(1)

            # Set PWM langsung
            set_pwm(esp32, 150)
            time.sleep(2)

            motor_off(esp32)
            print("--- Urutan kontrol selesai ---\n")

            # ---- Mode interaktif ----
            print("Mode interaktif:")
            print("  '1'   = Motor ON")
            print("  '0'   = Motor OFF")
            print("  '+'   = Naikkan kecepatan (+10)")
            print("  '-'   = Turunkan kecepatan (-10)")
            print("  'p'   = Set PWM langsung (mis. p150)")
            print("  'q'   = Keluar")

            while True:
                cmd = input("Perintah: ").strip()

                if cmd == "q":
                    break
                elif cmd == "1":
                    motor_on(esp32)
                elif cmd == "0":
                    motor_off(esp32)
                elif cmd == "+":
                    kecepatan_naik(esp32)
                elif cmd == "-":
                    kecepatan_turun(esp32)
                elif cmd.lower().startswith("p") and cmd[1:].isdigit():
                    set_pwm(esp32, int(cmd[1:]))
                else:
                    print("Perintah tidak valid! Gunakan 1/0/+/-/p<angka>/q.")

        except KeyboardInterrupt:
            print("\nDihentikan oleh pengguna.")

        finally:
            try:
                motor_off(esp32)
            except Exception:
                pass
            esp32.close()
            print("Koneksi serial ditutup.")
