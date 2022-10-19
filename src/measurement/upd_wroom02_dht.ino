#include <DHT.h>              // ライブラリのインクルード
 
#define DHT_PIN 5             // DHT11のDATAピンをデジタルピン7に定義
#define DHT_MODEL DHT11       // 接続するセンサの型番を定義する(DHT11やDHT22など)
#define NO 1                  // 当機を識別する番号

#include <ESP8266WiFi.h>
#include <WiFiUDP.h>

DHT dht(DHT_PIN, DHT_MODEL);  // センサーの初期化

static char *ssid = "xxxxxx"; // SSID
static const char *pass = "xxxxxx";  // password

static WiFiUDP wifiUdp; 
static const char *kRemoteIpadr = "192.168.10.105";
static const int kRmoteUdpPort = 8890;

static void WiFi_setup()
{
  static const int kLocalPort = 7000;

  Serial.println("WiFi_setup start");
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);

  Serial.println("WiFi.begin");
  
  while( WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(500);  
  }  

  Serial.println("WiFi.begin");
  
  wifiUdp.begin(kLocalPort);

  Serial.println("WiFi_setup end");

}

static void Serial_setup()
{
  Serial.begin(115200);
  Serial.println(""); // to separate line  
}

void setup() {
  Serial_setup();
  dht.begin();                // センサーの動作開始  
  WiFi_setup();
}

void loop() 
{

   delay(2000);                // センサーの読み取りを2秒間隔に
 
   float humidity = dht.readHumidity();          // 湿度の読み取り
   float temperature = dht.readTemperature();    // 温度の読み取り(摂氏)
 
   if (isnan(humidity) || isnan(temperature)) {  // 読み取りのチェック
     Serial.println("ERROR");
     return;
   }
  
  wifiUdp.beginPacket(kRemoteIpadr, kRmoteUdpPort);
  wifiUdp.println(NO + "," + String(temperature) + "," + String(humidity));
  wifiUdp.endPacket();  

  delay(3000);
}
