import socket


class Session:
    def __init__(self):
        self.host = 'localhost'
        self.port = 8000
        self.active = False
        self.box1 = 0
        self.box2 = 0
    
    def start_pause(self):
        self.active = not self.active
        print(f'Active: {self.active}')
    
    def update_box1(self, value):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall('4/000'.encode('utf-8'))
            response = s.recv(1024)
            print('Received', response.decode('utf-8'))
    
    def update_box2(self, value):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall('5/000'.encode('utf-8'))
            response = s.recv(1024)
            print('Received', response.decode('utf-8'))
    
    def increment_box1(self):
        raise NotImplementedError
        
    def increment_box2(self):
        raise NotImplementedError
