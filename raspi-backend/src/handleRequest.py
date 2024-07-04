import logging
import socket

from database import DatabaseManager

# Immutable command variables
RESET = 0
BUCKET_ONE = 1
BUCKET_TWO = 2

# Error messages
MALLOC = 'm'  # malloc error
SCALE = 's'   # scale error
WEIGHT = 'w'  # weighting error
LIGHT = 'l'   # light barrier error
WIFI = 'i'    # internet error
TCP = 't'     # server error


class PackageSortingServer:
    def __init__(self, host='localhost', port=8000):
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
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            if not isinstance(message, bytes):
                message = message.encode('utf-8')
            s.sendall(message)
            response = s.recv(1024)
            print('Received', response.decode('utf-8'))

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

        if command == RESET:
            logging.info("Reset command received - relayed and no action taken")
            self.send_message('0/000', 'localhost', 8001)
            return "OK: Reset command"

        elif command == BUCKET_ONE:
            logging.info(f"Package sorted to bucket 1 with weight {weight}")
            self.db_manager.set(weight, 1)
            self.send_message('1/000', 'localhost', 8001)
            self.send_message('9/000', 'localhost', 4999)
            return f"OK: Package sorted to bucket 1 with weight {weight}"

        elif command == BUCKET_TWO:
            logging.info(f"Package sorted to bucket 2 with weight {weight}")
            self.db_manager.set(weight, 2)
            self.send_message('2/000', 'localhost', 8001)
            self.send_message('9/000', 'localhost', 4999)
            return f"OK: Package sorted to bucket 2 with weight {weight}"

        # Handling error messages
        elif command_char == MALLOC:
            logging.error("Malloc error: failed to allocate memory for boxes array")
            self.send_message('m/000', 'localhost', 4999)
            return "ERROR: Malloc error"

        elif command_char == SCALE:
            logging.error("Scale error: timeout, check MCU>HX711 wiring and pin designations")
            self.send_message('s/000', 'localhost', 4999)
            return "ERROR: Scale error"

        elif command_char == WEIGHT:
            logging.error("Weight error: package weighs too little or too much")
            self.send_message('w/000', 'localhost', 4999)
            return "ERROR: Weight error"

        elif command_char == LIGHT:
            logging.error("Light barrier error: the light barrier was triggered")
            self.send_message('l/000', 'localhost', 4999)
            return "ERROR: Light barrier error"

        elif command_char == WIFI:
            logging.error("WiFi error: communication with WiFi module failed")
            self.send_message('i/000', 'localhost', 4999)
            return "ERROR: WiFi error"

        elif command_char == TCP:
            logging.error("TCP error: failed to connect to TCP server")
            self.send_message('t/000', 'localhost', 4999)
            return "ERROR: TCP error"

        else:
            logging.error("Unknown command")
            return "ERROR: Unknown command"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = PackageSortingServer()
    server.start_server()
