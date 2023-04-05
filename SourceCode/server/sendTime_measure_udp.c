#include "stdio.h"
#include "stdlib.h"
#include "string.h"
#include "time.h"
#include "WiFi.h"
#include "AsyncUDP.h"


// const char * ssid = "elecom-68d043";
const char * ssid = "CDSL-A910-11n";
// const char * password = "33dcu4jvm9d9";
const char * password = "11n-ky56$HDxgp";
const int port = 1234;

IPAddress src_ip;
time_t interval = 0;

AsyncUDP udp;

WiFiServer server(port);


// sequence array & push method
int seq_ary[1000] = {0};
int max_recv_size = 0;
int tmp = 0;
int ary_size = 0;

int compareInt(const void* a, const void* b) {
    int aNum = *(int*)a;
    int bNum = *(int*)b;

    return aNum - bNum;
}


void printArray(const int* array, size_t size) {
    for (size_t i = 0; i < size; ++i) {
        Serial.printf("%d ", array[i]);
    }
}

void setup()
{
    Serial.begin(115200);
    WiFi.mode(WIFI_STA);
    WiFi.begin(ssid, password);
    if (WiFi.waitForConnectResult() != WL_CONNECTED) {
        Serial.println("WiFi Failed");
        while(1) {
            delay(1000);
        }
    } else {
      Serial.println("connected!");

      // Server begin
      server.begin();
      Serial.println("server.begin()");
    }

    if (udp.listenMulticast(IPAddress(239,1,2,3), port)) {
        Serial.print("UDP Listening on IP: ");
        Serial.println(WiFi.localIP());
        udp.onPacket([](AsyncUDPPacket packet) {   

            src_ip = packet.remoteIP();

            char recvd[packet.length()];
            memcpy(recvd, packet.data(), packet.length()); 

            char *token;
            token = strtok(recvd, ":");
            
            ary_size++;
            max_recv_size = atoi(token);
            
            interval = time(NULL);
        });
    }
}


// TCP送受信部分
void loop()
{
    if ( interval && (ary_size != max_recv_size) && (time(NULL) - interval) > 1 ) {

      AsyncUDPMessage msg;                    
      msg.printf("E:ACK");
      udp.sendTo(msg, src_ip, 1234);
      Serial.printf("sended!\n");

      interval = 0;
      max_recv_size = 0;  
    }
    delay(150);
}

