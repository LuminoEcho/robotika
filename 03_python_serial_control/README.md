# 03 — Kendali Motor dari Komputer dengan Python

Eksperimen 01 dan 02 dikendalikan dari Serial Monitor. Di sini perannya diganti
skrip Python, sehingga urutan perintah bisa diotomasi dan nanti disambungkan ke
pemrosesan lain (misalnya visi komputer) di sisi PC.

## File

- `tes_imclab_naik_turun.py` — versi skrip dari notebook
- `Tes_IMCLab_naik_turun.ipynb` — notebook asli (auto-detect port + demo urutan + mode interaktif)
- `Tes_IMCLab_pilih_port_otomatis.ipynb` — eksperimen pemilihan port
- `Test_Port_Serial.ipynb` — eksperimen pembacaan port serial

## Kebutuhan

```bash
pip install pyserial
```

Firmware yang dipakai tetap `02_kecepatan_pwm_serial/imclab_naik_turun.ino`
(protokol serial 115200 baud).

## Cara kerja

**Deteksi port.** Nomor COM berubah-ubah tergantung port USB yang dipakai, jadi
skrip memindai semua port lalu memberi skor:

| Kondisi | Skor |
|---|---|
| VID:PID cocok (`0x10C4:0xEA60`, `0x10C4:0xEA70`, `0x1A86:0x7523`, `0x1A86:0x55D4`, `0x0403:0x6001`, `0x0403:0x6015`, `0x303A:0x1001`) | +100 |
| Deskripsi/manufaktur/hwid memuat kata kunci (`cp210`, `ch340`, `ftdi`, `espressif`, `esp32`, dll.) | +50 |
| Terindikasi Bluetooth | −200 |

Port dengan skor tertinggi dipakai. Kalau tidak ada kandidat tapi hanya ada satu
port non-Bluetooth, port itu yang dipilih.

**Urutan demo.** Setelah terhubung, skrip menjalankan: motor ON → naik 3 kali →
turun 2 kali → set PWM 150 → motor OFF, dengan jeda 1–2 detik antar langkah.

**Mode interaktif.** Setelah demo selesai, perintah bisa diketik manual:
`1` ON, `0` OFF, `+` naik, `-` turun, `p150` set PWM, `q` keluar.

## Contoh keluaran

```
Kandidat port ESP32 (skor tertinggi = paling mungkin):
  [ 150] COM5 : Silicon Labs CP210x USB to UART Bridge

>> Port ESP32 terpilih: COM5
--- Mulai urutan kontrol motor ---
RX <- Motor ON, duty = 200
RX <- Kecepatan NAIK, duty = 210
...
```

## Catatan

`BAUDRATE` harus sama dengan `Serial.begin()` di firmware (115200). Kalau berbeda,
gejala yang muncul bukan error, melainkan karakter acak di terminal.
