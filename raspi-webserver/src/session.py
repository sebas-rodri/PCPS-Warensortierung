import socket
import logging


class Session:
    def __init__(self):
        self.host = 'localhost'
        self.port = 5001
        self.active = False
        self.box1Full = False
        self.box2Full = False
        self.box1 = 0
        self.box2 = 0
        self.threshold = 100  # in grams
    
    def start_pause(self):
        self.active = not self.active
        print(f'Active: {self.active}')
    
    def increment_box1(self):
        self.box1 += 1
        
    def increment_box2(self):
       self.box2 += 1

    def send_message(self, message, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            if not isinstance(message, bytes):
                message = message.encode('utf-8')
            s.sendall(message)
            response = s.recv(1024)
            print('Received', response.decode('utf-8'))
            return response.decode('utf-8')
