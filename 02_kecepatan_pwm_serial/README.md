# 02 — Kontrol Kecepatan PWM lewat Serial

Pengembangan dari eksperimen 01: kecepatan motor bisa dinaikkan, diturunkan, atau
diset langsung ke nilai tertentu tanpa mengubah program.

## File

- `imclab_naik_turun.ino`

## Cara kerja

Perintah ditampung di buffer `inputString` sampai karakter baris baru (`\r` atau
`\n`) masuk. Setelah itu isi buffer diperiksa:

- diawali `PWM:` → sisa string diubah ke angka dengan `toInt()`, lalu masuk ke `setDuty()`
- satu karakter → diteruskan ke `MotorOn()`, `MotorOff()`, `naikkanKecepatan()`, atau `turunkanKecepatan()`

Semua jalur berakhir di `applyMotor()`, satu fungsi yang menulis arah putaran,
nilai PWM, dan status LED. Menaruh penulisan pin di satu tempat membuat nilai
`dutyCycle` dan kondisi perangkat keras tidak mungkin berbeda.

`setDuty()` membatasi nilai ke rentang `DUTY_MIN`–`DUTY_MAX`, jadi angka di luar
0–255 tidak merusak konfigurasi PWM.

## Perintah serial

| Input | Aksi |
|---|---|
| `1` | Motor ON, duty terakhir dipakai (default 200 kalau masih 0) |
| `0` | Motor OFF, duty 0 |
| `+` | Duty naik 10 |
| `-` | Duty turun 10 |
| `PWM:xxx` | Set duty langsung, contoh `PWM:150` |

## Keluaran yang diharapkan

```
ESP32 Motor Controller siap.
Perintah: 1=ON, 0=OFF, +=naik, -=turun, PWM:xxx=set
Motor ON, duty = 200
Kecepatan NAIK, duty = 210
Kecepatan NAIK, duty = 220
Set duty = 150
Kecepatan TURUN, duty = 140
Motor OFF, duty = 0
```

## Catatan

Saat duty mencapai 0 lalu perintah `1` dikirim, motor langsung melompat ke 200.
Lompatan ini disengaja: motor DC dengan beban kecil sering gagal start kalau duty
terlalu rendah, jadi perlu nilai awal yang cukup untuk melawan gesekan statis.
