import sys
import socket

UDP_IP = "192.168.4.2"  # ESP32 AP의 IP 주소
UDP_PORT = 1234  # ESP32에서 사용하는 UDP 포트

client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)  # UDP

# Uncomment this if you plan to broadcast from this script
#client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

# Set the socket to non blocking, allows the program to continue and not wait for data the whole time
client.setblocking(0)

# Bind to all interfaces and to port 1234
client.bind((UDP_IP, UDP_PORT))

def check_data():
    try:
        # Data received
        data, addr = client.recvfrom(8196)
        #print("received message: %s from %s" % (data,addr))

        # return the decoded bytes as a string
        return data.decode()
    # If no data is received just return None
    except socket.error:
        return None

def main():
    # Main loop
    while True:
        # Check for UDP data
        line = check_data()
        # If there is data split it and print it to console
        if line:
            split_line = line.split('|')
            print(split_line)

        # Continue with main loop
        # print("...")

if __name__ == '__main__':
    try:
        main()
    # CTRL + C pressed so exit gracefully
    except KeyboardInterrupt:
        print('Interrupted.')
        sys.exit()