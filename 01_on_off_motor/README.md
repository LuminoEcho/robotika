# 01 — Kontrol ON/OFF Motor DC

Eksperimen paling dasar: menyalakan dan mematikan motor DC lewat satu karakter
yang dikirim dari Serial Monitor.

## File

- `on_off_Motor.ino`

## Cara kerja

`loop()` membaca satu byte dari serial. Kalau isinya karakter `'1'`, program
memanggil `MotorOn()`; kalau `'0'`, memanggil `MotorOff()`. Selain dua karakter
itu, perintah diabaikan.

Kecepatan motor tidak diatur di sini — `MotorOn()` selalu memakai `dutyCycle = 225`
(sekitar 88% dari 255). Arah putaran ditentukan pasangan logika `IN1 = HIGH` dan
`IN2 = LOW`.

LED di GPIO 2 mengikuti perintah yang sama, jadi status motor bisa dilihat tanpa
melihat rotor.

## Perintah serial

| Input | Aksi | Duty |
|---|---|---|
| `1` | Motor berputar, LED menyala | 225 |
| `0` | Motor berhenti, LED mati | 0 |

## Keluaran yang diharapkan

```
Testing DC Motor...
LED is on !!!
LED is off !!!
```

## Catatan

Karena pembacaan serial tidak memakai buffer baris, akhiran baris (`\n`) dari
Serial Monitor ikut terbaca sebagai karakter lain dan diabaikan. Ini aman untuk
perintah satu karakter, tapi tidak cukup untuk perintah bertoken — lihat
eksperimen `02_kecepatan_pwm_serial`.
