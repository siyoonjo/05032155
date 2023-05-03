#include "WiFi.h"
#include "AsyncUDP.h"

const char * ssid = "5JO_DATA_WIFI";
const char * password = "12345678";

const int SENSOR_PIN1 = 32;
const int SENSOR_PIN2 = 33;
int sensor_value1;

const int BUFFER_SIZE = 2048;
char buffer[BUFFER_SIZE];
int buffer_length = 0;

AsyncUDP udp;

void setup() {
  pinMode(SENSOR_PIN1, INPUT);
  Serial.begin(115200);
  
  WiFi.mode(WIFI_AP);
  WiFi.softAP(ssid, password);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);
  
  if(udp.listen(1234)) {
    Serial.print("UDP Listening on IP: ");
    Serial.println(WiFi.localIP());
  } 
}

void input_data() {
  sensor_value1 = analogRead(SENSOR_PIN1);
}

void send_data() {
  if (buffer_length < BUFFER_SIZE) {
    String builtString = String("");
    builtString += String((int)sensor_value1);
    builtString += ",";
    buffer_length += builtString.length();
    strcat(buffer, builtString.c_str());
  }
  
  if (buffer_length >= BUFFER_SIZE) {
    udp.broadcastTo(buffer, 1234);
    Serial.println(buffer);  
    buffer[0] = '\0';
    buffer_length = 0;
  }
}

void loop() {
  input_data();
  send_data();
}
