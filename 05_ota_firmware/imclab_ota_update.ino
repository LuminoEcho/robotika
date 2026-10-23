// ============================================================
// iMCLab + ESP32 + Blynk — Penerima Firmware Over-The-Air (OTA)
// ------------------------------------------------------------
// Perangkat menerima URL berkas .bin dari Blynk, mengunduhnya
// lewat HTTP, menuliskannya ke partisi OTA yang tidak sedang
// dipakai, memverifikasi hasilnya, lalu restart.
//
// Board   : ESP32 Dev Module
// Skema   : Default 4MB with spiffs (dua partisi aplikasi:
//           app0/ota_0 dan app1/ota_1)
// Library : Blynk, WiFi (bawaan board ESP32), HTTPClient, Update
// ============================================================

#define BLYNK_TEMPLATE_ID   "TMPL6Rm4bEWoz"
#define BLYNK_TEMPLATE_NAME "IMCLab Kelas Test"
#define BLYNK_AUTH_TOKEN    "r47DkjLWdwhrgsBQ-YYvM-FaQSwRjUr7"

#include <WiFi.h>
#include <BlynkSimpleEsp32.h>
#include <HTTPClient.h>
#include <Update.h>

// Versi firmware yang sedang berjalan. Naikkan setiap kali
// mengirim binary baru supaya versi di serial mudah dibedakan.
const char* FIRMWARE_VERSION = "2.1.0";

char auth[] = BLYNK_AUTH_TOKEN;
char ssid[] = "HOTSPOT@UPNJATIM.AC.ID";
char pass[] = "belanegara";

const int ledPin = 2;

BlynkTimer timer;

// ============================================================
// Indikator
// ============================================================

void kedipkanLed()
{
  digitalWrite(ledPin, !digitalRead(ledPin));
}

void tampilkanInfo()
{
  Serial.print("Firmware v");
  Serial.print(FIRMWARE_VERSION);
  Serial.print(" | heap bebas ");
  Serial.print(ESP.getFreeHeap());
  Serial.println(" byte");
}

// ============================================================
// Handler OTA
// Dipanggil Blynk ketika server mengirim permintaan update.
// Parameter berisi URL langsung ke berkas .bin.
// ============================================================

BLYNK_WRITE(InternalPinOTA)
{
  String url = param.asStr();

  Serial.println();
  Serial.println("=== Permintaan OTA diterima ===");
  Serial.print("URL: ");
  Serial.println(url);

  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    Serial.println("URL tidak valid, OTA dibatalkan.");
    return;
  }

  WiFiClient client;
  HTTPClient http;

  http.setFollowRedirects(HTTPC_STRICT_FOLLOW_REDIRECTS);
  http.setTimeout(20000);

  if (!http.begin(client, url)) {
    Serial.println("Gagal membuka koneksi ke server firmware.");
    return;
  }

  int httpCode = http.GET();

  if (httpCode != HTTP_CODE_OK) {
    Serial.print("Server membalas kode ");
    Serial.println(httpCode);
    http.end();
    return;
  }

  int contentLength = http.getSize();

  if (contentLength <= 0) {
    Serial.println("Ukuran berkas tidak diketahui, OTA dibatalkan.");
    http.end();
    return;
  }

  Serial.print("Ukuran firmware: ");
  Serial.print(contentLength);
  Serial.println(" byte");

  // Update.begin menolak kalau binary lebih besar dari partisi
  // yang tersedia, jadi kegagalan ketahuan sebelum menulis apa pun.
  if (!Update.begin(contentLength, U_FLASH)) {
    Serial.print("Partisi tidak cukup: ");
    Serial.println(Update.errorString());
    http.end();
    return;
  }

  Update.onProgress([](size_t sudah, size_t total) {
    static uint8_t terakhir = 100;
    uint8_t persen = (total > 0) ? (sudah * 100 / total) : 0;
    if (persen / 10 != terakhir / 10) {
      terakhir = persen;
      Serial.printf("  %u%%\n", persen);
    }
  });

  size_t ditulis = Update.writeStream(http.getStream());
  http.end();

  if (ditulis != (size_t)contentLength) {
    Serial.print("Jumlah byte tidak cocok. Ditulis ");
    Serial.print(ditulis);
    Serial.print(", seharusnya ");
    Serial.println(contentLength);
    Update.abort();
    return;
  }

  if (!Update.end()) {
    Serial.print("Verifikasi gagal: ");
    Serial.println(Update.errorString());
    return;
  }

  if (!Update.isFinished()) {
    Serial.println("Proses tulis belum selesai, OTA dibatalkan.");
    return;
  }

  Serial.println("Firmware baru terverifikasi.");
  Serial.println("Restart ke partisi baru...");
  delay(500);
  ESP.restart();
}

// ============================================================
// Setup & Loop
// ============================================================

void setup()
{
  Serial.begin(115200);
  delay(200);

  pinMode(ledPin, OUTPUT);
  digitalWrite(ledPin, LOW);

  Serial.println();
  Serial.println("================================");
  Serial.print("iMCLab OTA receiver — v");
  Serial.println(FIRMWARE_VERSION);
  Serial.println("================================");

  Blynk.begin(auth, ssid, pass);

  // Indikator hidup: kedip pelan sebagai tanda perangkat siap
  timer.setInterval(500L, kedipkanLed);
  timer.setInterval(30000L, tampilkanInfo);
}

void loop()
{
  Blynk.run();
  timer.run();
}
