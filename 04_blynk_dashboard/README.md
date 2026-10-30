# 04 — Dashboard Blynk: PWM, Switch, dan Telemetri RPM

Kontrol motor lewat WiFi: slider PWM, tombol ON/OFF, dan pembacaan kecepatan
putar dari sensor optik, semuanya tampil di dashboard Blynk.

## File

- `imclab_Blynk_kelas.ino`
- `secrets.example.h` — template kredensial (salin jadi `secrets.h`)

## Virtual pin

| Pin | Tipe widget | Fungsi |
|---|---|---|
| `V0` | Value display / gauge | RPM hasil pengukuran |
| `V1` | Value display | Duty cycle aktual |
| `V2` | Slider (0–255) | Set PWM dari dashboard |
| `V3` | Switch | Motor ON/OFF |

Saat perangkat tersambung ulang, `BLYNK_CONNECTED()` memanggil `syncVirtual(V2)`
dan `syncVirtual(V3)` supaya posisi slider dan switch di dashboard sesuai kondisi
terakhir perangkat, bukan nilai default.

## Cara mengukur RPM

Sensor optik dipasang pada piringan dengan 2 lubang. Setiap celah melewati sensor,
pin GPIO 13 menghasilkan transisi turun yang memicu interupsi `FALLING`.

- `isr()` diberi atribut `IRAM_ATTR` agar eksekusinya tidak tertunda pembacaan flash.
- Interupsi yang datang lebih cepat dari `DEBOUNCE_US` (500 µs) diabaikan untuk
  menahan noise dan pantulan mekanis.
- Setiap 1 detik, interupsi dilepas sebentar (`detachInterrupt`), jumlah pulsa
  dibaca, lalu dihitung:

```
rot_per_sec = rev / HOLES
rpm         = rot_per_sec * 60        # HOLES = 2
```

Melepas interupsi sebelum membaca `rev` mencegah nilai berubah di tengah
perhitungan. Setelah itu `rev` dinolkan dan interupsi dipasang kembali.

## Kenapa memakai BlynkTimer

`kirimKeBlynk()` dijadwalkan tiap 1000 ms oleh `BlynkTimer`, bukan `delay()`.
`delay()` akan menghentikan `Blynk.run()` sehingga koneksi ke server terputus;
timer memanggil fungsi secara bergantian tanpa memblokir loop.

## Kredensial

Sketch asli memuat `BLYNK_AUTH_TOKEN`, `ssid`, dan `pass` secara langsung. Untuk
repo publik, pindahkan ketiganya ke `secrets.h`:

```cpp
// secrets.h
#define BLYNK_AUTH_TOKEN "token-dari-blynk-console"
#define WIFI_SSID        "nama-wifi"
#define WIFI_PASS        "password-wifi"
```

lalu di sketch:

```cpp
#include "secrets.h"
char ssid[] = WIFI_SSID;
char pass[] = WIFI_PASS;
```

`secrets.h` sudah masuk `.gitignore` di root repo.

## Perintah serial

Masih tersedia untuk pengujian tanpa jaringan: `1`, `0`, `+`, `-`, `PWM:xxx`, `R`.
