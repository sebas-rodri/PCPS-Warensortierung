import logging
import socket

from database import DatabaseManager

# Immutable command variables
RESET = '0'
BUCKET_ONE = '1'
BUCKET_TWO = '2'
GET_PACKAGE = '3'
PACKAGE_ON_SCALE = '4'
THRESHOLD = '5'
UPDATED_DATABASE = '9'

# Error messages
SCALE = 's'   # scale error
WEIGHT = 'w'  # weighting error
LIGHTBOX1 = 'l'   # light barrier error
LIGHTBOX2 = 'L'   # light barrier error

# Global variables
ip_address = '192.168.1.105'
PORT_ARDUINO = 80
PORT_WEBSERVER = 5001
PORT_BACKEND = 8000
PORT_ROBOT = 8001

class PackageSortingServer:
    def __init__(self, host=ip_address, port=PORT_BACKEND):
        self.host = host
        self.port = port
        self.db_manager = DatabaseManager('database.db')

    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            logging.info(f"Server started and listening on {self.host}:{self.port}")

            while True:
                conn, addr = s.accept()
                with conn:
                    logging.info(f"Connected by {addr}")
                    data = conn.recv(1024)
                    if data:
                        response = self.handle_request(data.decode('utf-8'))
                        conn.sendall(response.encode('utf-8'))

    def send_message(self, message, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                if not isinstance(message, bytes):
                    message = message.encode('utf-8')
                s.sendall(message)
                if port == PORT_ARDUINO: return
                response = s.recv(1024)
                print('Received', response.decode('utf-8'))
        except ConnectionRefusedError:
            logging.error(f"Connection to {host}:{port} refused")

    def handle_request(self, message):
        logging.info(f"Received message: {message}")

        if len(message) < 5 or message[1] != '/':
            logging.error("Invalid message format")
            return "ERROR: Invalid message format"

        command_char = message[0]
        command = None
        weight = None

        try:
            command = command_char
            weightstr = message[2:5]
            weight = int(message[2:5])
        except ValueError:
            logging.error(f"Invalid command or weight: {command_char}, {message[2:5]}")
            return "ERROR: Invalid command or weight"

        if command == RESET:
            logging.info("Reset command received - relayed and no action taken")
            self.send_message('0/000', ip_address, PORT_ROBOT)
            return "OK: Reset command"

        elif command == BUCKET_ONE:
            logging.info(f"Package sorted to bucket 1 with weight {weight}")
            self.db_manager.set(weight, 1)
            self.send_message('1/'+weightstr, ip_address, PORT_ROBOT)
            self.send_message('9/'+weightstr, ip_address, PORT_WEBSERVER)
            return f"OK: Package sorted to bucket 1 with weight {weight}"

        elif command == BUCKET_TWO:
            logging.info(f"Package sorted to bucket 2 with weight {weight}")
            self.db_manager.set(weight, 2)
            self.send_message('2/'+weightstr, ip_address, PORT_ROBOT)
            self.send_message('9/'+weightstr, ip_address, PORT_WEBSERVER)
            return f"OK: Package sorted to bucket 2 with weight {weight}"

        elif command == GET_PACKAGE:
            logging.info(f"Package transport to scale")
            self.send_message('3/000', ip_address, PORT_ROBOT)
            self.send_message('4/000','192.168.1.141',PORT_ARDUINO)
            return f"OK: Package transport to scale and 4/000 send to arduino"
        
        elif command == THRESHOLD:
            logging.info(f"Threshold updated to {weight}")
            self.send_message('5/'+weightstr,'192.168.1.141',PORT_ARDUINO)
            return f"OK: Threshold updated to {weight}"

        # Handling error messages
        elif command_char == SCALE:
            logging.error("Scale error: timeout, check MCU>HX711 wiring and pin designations")
            self.send_message('s/000', ip_address, PORT_WEBSERVER)
            return "ERROR: Scale error"

        elif command_char == WEIGHT:
            logging.error("Weight error: package weighs too little or too much")
            self.send_message('w/000', ip_address, PORT_WEBSERVER)
            return "ERROR: Weight error"

        elif command_char == LIGHTBOX1:
            logging.error("Light barrier error: the light barrier was triggered")
            self.send_message('l/000', ip_address, PORT_WEBSERVER)
            
            return "ERROR: Light barrier error"
        
        elif command_char == LIGHTBOX2:
            logging.error("Light barrier error: the light barrier was triggered")
            self.send_message('L/000', ip_address, PORT_WEBSERVER)
            return "ERROR: Light barrier error"

        else:
            logging.error("Unknown command")
            return "ERROR: Unknown command"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = PackageSortingServer()
    server.start_server()
