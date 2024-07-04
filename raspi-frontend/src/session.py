import socket
import logging


# Immutable command variables
RESET = 0
BUCKET_ONE = 1
BUCKET_TWO = 2
UPDATED_DATABASE = 9

# Error messages
MALLOC = 'm'  # malloc error
SCALE = 's'   # scale error
WEIGHT = 'w'  # weighting error
LIGHT = 'l'   # light barrier error
WIFI = 'i'    # internet error
TCP = 't'     # server error


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

    def handle_request(self, message):
        logging.info(f"Received message: {message}")

        if len(message) < 5 or message[1] != '/':
            logging.error("Invalid message format")
            return "ERROR: Invalid message format"

        command_char = message[0]
        command = None
        weight = None

        try:
            command = int(command_char)
            weight = int(message[2:5])
        except ValueError:
            logging.error(f"Invalid command or weight: {command_char}, {message[2:5]}")
            return "ERROR: Invalid command or weight"

        if command == UPDATED_DATABASE:
            # TODO GET NEW DATA FROM DATABASE
            logging.info(f"Received updated database: {message}")
            response = self.send_message('get_data', 'localhost', 8000)
            self.box1 = response[0]
            self.box2 = response[1]
            raise NotImplementedError

        # Handling error messages
        elif command_char == MALLOC:
            logging.error("Malloc error: failed to allocate memory for boxes array")
            return "ERROR: Malloc error"

        elif command_char == SCALE:
            logging.error("Scale error: timeout, check MCU>HX711 wiring and pin designations")
            return "ERROR: Scale error"

        elif command_char == WEIGHT:
            logging.error("Weight error: package weights too little or too much")
            return "ERROR: Weight error"

        elif command_char == LIGHT:
            logging.error("Light barrier error: the light barrier was triggered")
            return "ERROR: Light barrier error"

        elif command_char == WIFI:
            logging.error("WiFi error: communication with WiFi module failed")
            return "ERROR: WiFi error"

        elif command_char == TCP:
            logging.error("TCP error: failed to connect to TCP server")
            return "ERROR: TCP error"

        else:
            logging.error("Unknown command")
            return "ERROR: Unknown command"
