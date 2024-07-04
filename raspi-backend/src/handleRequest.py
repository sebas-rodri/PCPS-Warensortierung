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
            logging.info("Reset command received - no action taken")
            return "OK: Reset command"

        elif command == BUCKET_ONE:
            logging.info(f"Package sorted to bucket 1 with weight {weight}")
            self.db_manager.set(weight, 1)
            return f"OK: Package sorted to bucket 1 with weight {weight}"

        elif command == BUCKET_TWO:
            logging.info(f"Package sorted to bucket 2 with weight {weight}")
            self.db_manager.set(weight, 2)
            return f"OK: Package sorted to bucket 2 with weight {weight}"

        # Handling error messages
        elif command_char == MALLOC:
            logging.error("Malloc error: failed to allocate memory for boxes array")
            return "ERROR: Malloc error"

        elif command_char == SCALE:
            logging.error("Scale error: timeout, check MCU>HX711 wiring and pin designations")
            return "ERROR: Scale error"

        elif command_char == WEIGHT:
            logging.error("Weight error: package weighs too little or too much")
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = PackageSortingServer()
    server.start_server()
