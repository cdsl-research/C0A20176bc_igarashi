#include "stdio.h"
#include "stdlib.h"
#include "string.h"
#include "time.h"
#include "WiFi.h"
#include "AsyncUDP.h"


const char * ssid;
const char * password;
const int port = 1234;

IPAddress src_ip;
time_t st = 0;

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
            
            max_recv_size = atoi(token);

            token = strtok(NULL, ":");
            
            int add_item = atoi(token);

            seq_ary[ary_size] = add_item;
            ary_size++;

            st = time(NULL);
        });
    }
}


// TCP送受信部分
void loop()
{
    if ( ary_size != max_recv_size && st && (time(NULL) - st) > 1 ) {

      qsort(seq_ary, ary_size, sizeof(int), compareInt);
      
      // search loss packets
      char loss[2000] = "";
      char buf[6];
      int counter = 0;

      // recv packet 0 case is Abbreviated...

      // count...seq counter
      // ex) seq_ary[3,4,5,6,7] / [1,2] loss search

      if ( seq_ary[0] != 1 ) {
        for ( counter=1; counter < seq_ary[0]; counter++ ) {
          snprintf(buf, sizeof(buf), "%d", counter);
          strcat(loss, buf);
          strcat(loss, ",");
        }
      }

      counter = seq_ary[0] + 1;
      for ( tmp=1; tmp < ary_size; tmp++ ) {
        while ( counter < seq_ary[ary_size-1] ) {
          if ( seq_ary[tmp] < counter ) break;

          if ( seq_ary[tmp] == counter ) {
              counter++;
              break;
          } else {
              snprintf(buf, sizeof(buf), "%d", counter);
              strcat(loss, buf);
              strcat(loss, ",");
              counter++;
          }
        }
      }
      
      // ex) seq_ary[3,4,5,6,7] / [8,9,10] loss search
      // 10 = 最大シーケンス番号
      if ( seq_ary[ary_size-1] != max_recv_size ) {
        for ( counter=seq_ary[ary_size-1]+1; counter <= max_recv_size; counter++ ) {
            snprintf(buf, sizeof(buf), "%d", counter);
            strcat(loss, buf);
            strcat(loss, ",");
        }
      }
      

      WiFiClient client = server.available();
      client.connect(src_ip, port);
      
      client.println(loss);
      Serial.printf("%s sended!\n", loss);

      if ( client ) {
        Serial.println("New Client Created");

        while ( client.connected() ) {
          // recv packet loss data from server
          int size = client.available();
          if( size ) {
            // Serial.printf("size: %d\n", size);

            // for (int i = 0; i < size; i++) {
              // uint8_t...8ビット整数型
              // c 10進数. ex) M = 77 = 0x4c  
              // uint8_t c = client.read();
              // 1byteを1文字に変換
              // Serial.printf("get: %c\n", c);

              char input[1024];
              memset(input, 0, sizeof(input));
              client.read((uint8_t*)input, sizeof(input) - 1);
            }
            delay(1);
          }
          client.stop();
          Serial.println("client.stop");  
        }   
             
        for (int i = 0; i < ary_size; ++i) {
          seq_ary[i] = 0;
        }

        st = 0;
        max_recv_size = 0;
        ary_size = 0;
    }
    delay(100);
}

