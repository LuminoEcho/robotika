# Progres Praktikum Robotika — Kit iMCLab ESP32

Catatan kemajuan pengerjaan Evaluasi Tengah Semester (ETS), Program Studi
Informatika, Fakultas Ilmu Komputer, UPN "Veteran" Jawa Timur.

**Status per 23 Oktober 2026:** lima modul selesai, empat diuji di perangkat keras,
satu diverifikasi sampai firmware baru berjalan di board.

---

## Ringkasan progres

| Modul | Yang dikerjakan | Status | Bukti |
|---|---|---|---|
| 1 — ON/OFF motor | Kontrol motor lewat karakter serial `1` / `0`, LED indikator mengikuti | Selesai, teruji | `01_on_off_motor/`, laporan Modul 1 |
| 2 — Kecepatan PWM | Naik/turun bertingkat `+` `-`, set langsung `PWM:xxx`, pembatas 0–255 | Selesai, teruji | `02_kecepatan_pwm_serial/`, laporan Modul 2 |
| 3 — Kendali Python | Auto-detect port ESP32, urutan perintah otomatis, mode interaktif | Selesai, teruji | `03_python_serial_control/`, laporan Modul 3 |
| 4 — Dashboard Blynk | Slider PWM, switch ON/OFF, telemetri RPM dari sensor optik | Selesai, teruji | `04_blynk_dashboard/`, laporan Modul 4 |
| 5 — OTA firmware | Penerima update: unduh binary, tulis ke partisi `ota_1`, restart | Selesai, teruji | `05_ota_firmware/`, laporan Modul 5 |

Laporan lengkap: `docs/Laporan_Riset_Praktikum_Robotika_Kit_iMCLab_ETS.pdf` (15 halaman).

---

## 1 — Kontrol ON/OFF motor

Fondasi yang dipakai semua modul berikutnya: konfigurasi LEDC channel 0 pada 30 kHz
dan 8-bit, lalu jalur kontrol `IN1`/`IN2` untuk arah putaran. Perintah masuk
sebagai satu karakter, jadi tidak perlu parser.

Yang sudah jalan: motor berputar pada duty tetap 225, LED GPIO 2 menyala bersamaan,
dan Serial Monitor mengeluarkan `LED is on` / `LED is off` sesuai perintah.

Catatan: pembacaan satu karakter tanpa buffer baris aman untuk perintah tunggal,
tetapi tidak cukup untuk perintah bertoken — batasan ini yang mendorong modul 2.

---

## 2 — Kecepatan PWM lewat serial

Perintah sekarang ditampung di buffer sampai karakter baris baru, baru diperiksa.
Tiga jalur perintah bermuara ke satu fungsi `applyMotor()`, sehingga nilai
`dutyCycle` dan kondisi pin tidak mungkin berbeda.

Yang sudah jalan: `+` dan `-` mengubah duty sebesar 10, `PWM:xxx` menyetel langsung,
dan semua nilai dijepit ke 0–255 sebelum menyentuh register PWM.

Temuan saat pengujian: motor tidak mulai berputar pada duty rendah. Rotor butuh
lompatan awal yang cukup untuk melawan gesekan statis, jadi perintah `1` dari
kondisi 0 langsung memakai duty 200, bukan menaikkan dari nol.

---

## 3 — Kendali dari komputer (Python)

Nomor COM berubah setiap kali kabel dicabut-pasang, dan daftar port ikut memuat
perangkat Bluetooth yang tidak ada hubungannya. Skrip sekarang memindai semua port
dan memberi skor: VID/PID yang dikenal (CP210x, CH340, FTDI, ESP32 native) +100,
kata kunci pada deskripsi +50, indikasi Bluetooth −200.

Yang sudah jalan: port ESP32 terpilih otomatis, urutan demo berjalan (ON → naik
3× → turun 2× → PWM 150 → OFF), lalu mode interaktif menerima perintah manual.

Berkas: `tes_imclab_naik_turun.py` beserta tiga notebook eksperimen port.

---

## 4 — Dashboard Blynk

Virtual pin dipetakan: `V0` RPM, `V1` duty aktual, `V2` slider, `V3` switch.
Saat perangkat tersambung ulang, `BLYNK_CONNECTED()` menyelaraskan posisi slider
dan switch dengan kondisi terakhir perangkat.

Pengukuran RPM memakai sensor optik pada piringan 2 lubang. Interupsi `FALLING`
dengan atribut `IRAM_ATTR` dan filter 500 µs; setiap detik jumlah pulsa dibaca
setelah interupsi dilepas sebentar agar nilainya tidak berubah di tengah hitungan.

Hasil pengujian bertingkat:

| Duty cycle | Rasio tegangan efektif | Pulsa/detik | Kecepatan |
|---|---|---|---|
| 0 | 0.00 % | 0 | 0.0 RPM |
| 100 | 39.22 % | 24 | 720.0 RPM |
| 150 | 58.82 % | 37 | 1,110.0 RPM |
| 200 | 78.43 % | 47 | 1,420.5 RPM |
| 255 | 100.00 % | 75 | 2,240.2 RPM |

Di bawah duty 80 rotor belum bergerak (stall region). Di atas 200 responsnya stabil.
Gambar dashboard kondisi standby dan kondisi aktif ada di laporan, Gambar 4.3 dan 4.4.

---

## 5 — OTA firmware

`05_ota_firmware/imclab_ota_update.ino` menerima URL berkas `.bin` lewat
`BLYNK_WRITE(InternalPinOTA)`, mengunduhnya dengan `HTTPClient`, menulis ke partisi
yang tidak sedang dipakai lewat `Update.writeStream()`, memverifikasi dengan
`Update.end()`, lalu restart.

Handler berhenti lebih awal kalau URL bukan http(s), server tidak membalas 200,
`Content-Length` tidak diketahui, binary melebihi kapasitas partisi, atau jumlah
byte tertulis tidak cocok. Tujuannya satu: jangan pernah meninggalkan perangkat
setengah ter-update.

Yang sudah jalan: shipment `v2.1.0` (1.248.320 byte) selesai dalam 18 detik, checksum
terverifikasi, boot partition berpindah, perangkat kembali online dengan versi baru.

---

## Kendala yang sudah ditangani

| Masalah | Penanganan |
|---|---|
| Motor diam pada duty rendah | Perintah ON dari 0 langsung memakai duty 200 |
| Pembacaan pulsa palsu akibat pantulan mekanis | Filter debounce 500 µs di dalam ISR |
| Nilai pulsa berubah saat dibaca | `detachInterrupt` sebelum membaca, dipasang kembali setelahnya |
| `delay()` memutus koneksi Blynk | `BlynkTimer` untuk penjadwalan non-blokir |
| Nomor COM berubah-ubah | Pemilihan port berbasis VID/PID + skor kata kunci |
| Binary bisa melebihi partisi | `Update.begin()` menolak sebelum ada byte yang ditulis |

---

## Langkah berikutnya

1. Kompilasi ulang dan unggah tiap sketch setelah folder dirapikan, untuk memastikan
   tidak ada path yang tertinggal.
2. Pindahkan `BLYNK_AUTH_TOKEN`, `ssid`, dan `pass` ke `secrets.h` sebelum repo
   dijadikan publik.
3. Uji OTA sekali lagi dengan binary versi berikutnya sebagai bukti siklus penuh.
4. Rapikan tabel pemetaan pin di laporan bila ada perubahan kabel.

---

## Struktur repositori

```
01_on_off_motor/          on_off_Motor.ino
02_kecepatan_pwm_serial/  imclab_naik_turun.ino
03_python_serial_control/ skrip Python + notebook eksperimen port
04_blynk_dashboard/       imclab_Blynk_kelas.ino + secrets.example.h
05_ota_firmware/          imclab_ota_update.ino + secrets.example.h
docs/                     laporan PDF dan DOCX
```

## Perangkat keras

| Komponen | Pin ESP32 |
|---|---|
| Driver motor IN1 / IN2 | GPIO 27 / GPIO 26 |
| Driver motor ENA (PWM) | GPIO 12 |
| LED indikator | GPIO 2 |
| Sensor RPM | GPIO 13 (`INPUT_PULLUP`, interupsi `FALLING`) |

PWM: 30 kHz, 8-bit, channel 0. Piringan enkoder 2 lubang.

## Catatan kredensial

Kedua sketch Blynk masih memuat token dan kredensial WiFi langsung di dalam kode.
`.gitignore` sudah mengecualikan `secrets.h`; salin `secrets.example.h` menjadi
`secrets.h` lalu pindahkan nilainya ke sana sebelum repo dipublikasikan. Kalau token
sudah pernah ter-commit, revoke di Blynk Console dan buat yang baru.

## Mendorong ke GitHub

```bash
cd ETS
git init
git add .
git commit -m "Praktikum Robotika ETS: progres lima modul"
git branch -M main
git remote add origin https://github.com/<username>/<nama-repo>.git
git push -u origin main
```
