import socket
import time

def send_message_to_server(message, server_address=('192.168.1.105', 8001)):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # Send message to server
        s.connect(server_address)
        s.sendall(message.encode())

if __name__=='__main__':
    while True:
        time.sleep(1)
        command = input('Enter command: ')
        send_message_to_server(command)