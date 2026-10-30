# 05 — Pembaruan Firmware Over-The-Air (OTA)

Firmware menerima URL berkas `.bin` dari Blynk, mengunduhnya, menuliskannya ke
partisi aplikasi yang sedang tidak dipakai, lalu restart ke versi baru.

## File

- `imclab_ota_update.ino`

## Alur

1. **Kompilasi.** Di Arduino IDE: `Sketch → Export Compiled Binary`. Hasilnya
   `imclab_ota_update.ino.bin` di folder sketch.
2. **Unggah.** Buka Blynk Console → perangkat → **Blynk.Air** → *Ship Firmware*,
   unggah `.bin`, isi versi (misalnya `v2.1.0`), pilih perangkat tujuan.
3. **Terima di perangkat.** Server mengirim URL berkas lewat virtual pin internal,
   masuk ke handler `BLYNK_WRITE(InternalPinOTA)`.
4. **Unduh dan tulis.** `HTTPClient` membuka aliran data, `Update.begin()` memeriksa
   apakah ukuran binary muat di partisi, lalu `Update.writeStream()` menuliskannya
   sambil mencetak progres per 10%.
5. **Verifikasi.** `Update.end()` memeriksa hasil tulis. Kalau lolos, perangkat
   restart ke partisi baru; kalau gagal, firmware lama tetap berjalan.

## Pemeriksaan sebelum menulis

Handler berhenti lebih awal pada kondisi berikut, supaya kegagalan tidak
meninggalkan perangkat dalam keadaan setengah ter-update:

| Kondisi | Tindakan |
|---|---|
| URL bukan `http://` atau `https://` | Dibatalkan |
| Koneksi ke server gagal | Dibatalkan |
| Balasan server bukan `200 OK` | Dibatalkan |
| `Content-Length` tidak diketahui | Dibatalkan |
| Binary lebih besar dari partisi | Dibatalkan sebelum menulis |
| Byte tertulis tidak sama dengan `Content-Length` | `Update.abort()` |
| Verifikasi akhir gagal | Firmware lama tetap dipakai |

## Kenapa aman

ESP32 memakai dua partisi aplikasi (`ota_0` dan `ota_1`). Partisi yang sedang
menjalankan firmware tidak pernah ditimpa; perangkat hanya berpindah partisi
setelah unduhan selesai dan lolos verifikasi. Koneksi yang terputus di tengah
jalan tidak membuat perangkat gagal boot.

Tabel partisi harus menyediakan dua slot aplikasi — pilihan board *ESP32 Dev
Module* dengan skema **Default 4MB with spiffs** sudah memenuhinya. Kalau binary
melebihi ukuran partisi, `Update.begin()` menolak dan pesannya tercetak di serial.

## Yang perlu diperhatikan

- Perangkat harus **online** di Blynk saat shipment dikirim.
- `FIRMWARE_VERSION` di sketch dinaikkan setiap kali mengirim binary baru, supaya
  versi yang berjalan mudah dibedakan dari serial.
- Token dan kredensial WiFi ikut ter-compile ke dalam binary. Kalau token dirotasi,
  kirim OTA baru yang memuat token tersebut.

## Keluaran serial saat berhasil

```
=== Permintaan OTA diterima ===
URL: https://.../imclab_ota_update.ino.bin
Ukuran firmware: 1248320 byte
  10%
  ...
  100%
Firmware baru terverifikasi.
Restart ke partisi baru...
```
