#include "WiFi.h"
#include "AsyncUDP.h"
#include "esp_adc_cal.h"


const char * ssid = "5JO_DATA_WIFI_2";
const char * password = "12345678";

const int SENSOR_PIN1 = 32;
const int SENSOR_PIN2 = 33;
int sensor_value1 = 0, sensor_value2 = 0;

adc1_channel_t channel1 = ADC1_CHANNEL_4;  // 32번 핀
adc1_channel_t channel2 = ADC1_CHANNEL_5;  // 33번 핀
const adc_bits_width_t width = ADC_WIDTH_BIT_12;
const adc_atten_t atten = ADC_ATTEN_DB_11;
const uint32_t clk_div = 1;

const int BUFFER_SIZE = 1024;
char buffer[BUFFER_SIZE];
char char_buffer[12];
int buffer_length = 0;
unsigned long connectTimeout = 3000; // 연결 제한 시간 (30초)
unsigned long connectStartMillis = 0; // 연결 시작 시간
AsyncUDP udp;

void setup() {
  // ADC 초기화
  adc1_config_width(width);
  adc1_config_channel_atten(channel1, atten);
  adc1_config_channel_atten(channel2, atten);
  Serial.begin(115200);
  
  WiFi.mode(WIFI_AP);
 // WiFi.softAPConfig(localIP, gateway, subnet);
  WiFi.softAP(ssid, password);
  IPAddress myIP = WiFi.softAPIP();
  Serial.print("AP IP address: ");
  Serial.println(myIP);
  
  if(udp.listen(1237)) {
    Serial.print("UDP Listening on IP: ");
    Serial.println(WiFi.localIP());
  } 
}

void input_data() {
  // ADC 값을 읽어오기
  sensor_value1 = adc1_get_raw(channel1);
  sensor_value2 = adc1_get_raw(channel2);
}

void send_data() {
  //Serial.println(buffer);
  udp.broadcastTo(buffer, 1237); 
  //Serial.println(buffer_length);
  memset(buffer, 0, BUFFER_SIZE);
  memset(char_buffer, 0, sizeof(char_buffer)-1);
  char_buffer[11] = '\0' ;
  
  buffer_length = 0;
}

void cum_data() {
  if (buffer_length < BUFFER_SIZE) {
    sprintf(char_buffer, "%d,%d\n", sensor_value1, sensor_value2);
    // Serial.print(strlen(char_buffer)+ 1);
    // Serial.print(BUFFER_SIZE - buffer_length);
    // Serial.println(strlen(char_buffer)+ 1 >  BUFFER_SIZE - buffer_length);
    if (12 >=  BUFFER_SIZE - buffer_length) {
        send_data();

    }
    int len = snprintf(buffer + buffer_length, BUFFER_SIZE - buffer_length, char_buffer);
    if (len > 0) {
      //Serial.print(len);
      buffer_length += len ;
    }
  }
}

void loop() {
    // Wi-Fi 연결 시간 체크
  if (millis() - connectStartMillis >= connectTimeout) {
    WiFi.disconnect(true); // 연결 제한 시간 초과 시 Wi-Fi 연결 해제
    connectStartMillis = millis(); // 연결 시작 시간 갱신
  }
  input_data();
  cum_data();
}