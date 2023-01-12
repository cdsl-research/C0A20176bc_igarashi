#include "WiFi.h"
#include "AsyncUDP.h"
// AsyncUDP udp;

const char * ssid = "elecom-68d043";
const char * password = "33dcu4jvm9d9";
const int port = 1234; 
int sum = 0;

WiFiServer server(port);

void setup()
{
    Serial.begin(115200);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    if ( WiFi.waitForConnectResult() != WL_CONNECTED ) {
        Serial.println("WiFi Failed");
        while(1) {
            delay(1000);
        }
    } else {
        Serial.println("connected!");
        Serial.println();
        Serial.printf("IP Address : ");
        Serial.println(WiFi.localIP());

        server.begin();
        Serial.println("server.begin()");
    }
}

void loop() {
    WiFiClient client = server.available();
    int count = 0;

    if ( client ) {

      Serial.println("New Client Created");
      while ( client.connected() ) {
        int size = client.available();
        if( size ) {
          char input[1024];
          memset(input, 0, sizeof(input));
          client.read((uint8_t*)input, sizeof(input) - 1);
          // Serial.printf("get: [%s]\n", input);
        }
        delay(1);
      }
      client.stop();
      Serial.println("client stopped");
    }
}
