import sys
import socket
import time
import numpy as np
import matplotlib.pyplot as plt
import csv

UDP_IP = "0.0.0.0" 
UDP_PORT = 1237

# check_data()라는 함수 정의
def recv_data():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setblocking(0)
    sock.bind((UDP_IP, UDP_PORT))
    
    interval = 1.5

    data_buffer = bytearray()
    data_list_vib = []
    data_list_mic = []
    start_time = time.time()
    while True:
        try:
        # Data received
            data,addr= sock.recvfrom(1024)
            data_buffer.extend(data)
            # Decode the bytes to a stringx
            while b'\n' in data_buffer:
                line, data_buffer = data_buffer.split(b'\n', 1)
                line = line.decode('ascii')
                values = line.split(',') # [2888, 0]
                data_list_vib.append((values[0])) # [2888, 2888, 2888]
                data_list_mic.append((values[1])) # [0, 0, 0, 0, ]            
            elapsed_time = time.time() - start_time
            if elapsed_time >= interval: 
                # data_list를 실수화 및 전압화
                data_list_vib = list(map(float, data_list_vib))
                # print(np.max(data_list_vib))
                # print(np.min(data_list_vib))

                
                data_list_vib = list(map(lambda x: x * 5/4096, data_list_vib))
                data_list_mic = list(map(float, data_list_mic))
                print(max(data_list_mic))
                #print(np.max(data_list_mic))
                #print(np.min(data_list_mic))
                data_list_mic = list(map(lambda x: x * 3.3/4096, data_list_mic))
                # 최댓값 출력
                max_value_v = max(data_list_vib)
                min_value_v = min(data_list_vib)    
                print("v최댓값:", max_value_v, "v최솟값:", min_value_v)
                max_value_m = max(data_list_mic)
                min_value_m = min(data_list_mic)    
                print("m최댓값:", max_value_m, "m최솟값:", min_value_m)

                data_list_mic = [x for x in data_list_mic if x <= 5]
                data_list_vib = [x for x in data_list_vib if x >= 0 and x <= 5]

               # 그래프 그리기
                fig, ((ax1, ax3), (ax2, ax4)) = plt.subplots(nrows=2, ncols=2, sharex=False,figsize=(12, 10))
                fig.text(0.5, 0.95, 'VIB SENSOR DATA', ha='center', va='top', fontsize=13)
                ax1.plot(data_list_vib,color='b', label='Vib')
                ax1.set_ylabel('Voltage_VIB')
                ax1.set_xlabel('Time (ms)')
                ax1.set_ylim( [3.4, 4.2])

                # Mic subplot
                fig.text(0.5, 0.48, 'MIC SENSOR DATA', ha='center', va='top', fontsize=13) 
                ax2.plot(data_list_mic,color='orange', label='Mic')
                ax2.set_ylabel('Voltage_MIC')
                ax2.set_xlabel('Time (ms)')
                ax2.set_ylim([-1, 3.3])

                # FFT subplot
                mean_signal_mic = np.mean(data_list_mic)
                mean_signal_vib = np.mean(data_list_vib)
                data_list_mic = data_list_mic - mean_signal_mic
                data_list_vib = data_list_vib - mean_signal_vib

                N_m = len(data_list_mic)# 데이터 포인트 개수
                N_v = len(data_list_vib)
                T = interval/N_m #x`` 샘플링 주파수 (10kHz)
                x_fM = np.linspace(0.0, 1.0/(2.0*T), N_m//2) # 주파수 범위
                x_fV = np.linspace(0.0, 1.0/(2.0*T), N_v//2)
                y_fM = np.fft.fft(data_list_mic) # FFT 수행 및 정규화
                y_fM = 2.0/N_m * np.abs(y_fM[:N_m//2]) # 절반만 사용하고 정규화
                y_fV = np.fft.fft(data_list_vib)# FFT 수행 및 정규화
                y_fV = 2.0/N_v * np.abs(y_fV[:N_v//2]) # 절반만 사용하고 정규화
                y_fV_csv = np.array(y_fV)
                y_fM_csv = np.array(y_fM)

                #CSV 저장

                with open('0626v.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows([y_fV_csv.tolist()])
                with open('0626m.csv', 'a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerows([y_fM_csv.tolist()])    

                # file.close()
                ax3.plot(x_fV, y_fV,color='b', label='VIB FFT')
                ax3.set_xlabel('Frequency (Hz)')
                ax3.set_ylabel('Amplitude_VIB')
                ax3.set_xlim([0, 5000])
                ax3.set_ylim(bottom=0, top=0.007)
                ax4.plot(x_fM, y_fM, color='orange',label='MIC FFT')
                ax4.set_xlabel('Frequency (Hz)')
                ax4.set_ylabel('Amplitude_MIC')
                ax4.set_xlim([0, 5000])
                ax4.set_ylim(bottom=0, top=0.07)
                fig.subplots_adjust(hspace=0.5)

                plt.show()


                


    # If no data is received just return None
        except socket.error:
            pass

# main()이라는 함수 정의
def main():
    while True:
        # Check for UDP data
        recv_data()

if __name__ == '__main__':
    try:
        main()
    # CTRL + C pressed so exit gracefully
    except KeyboardInterrupt:
        print('Interrupted.')
        sys.exit()
