import socket
import logging
from robot_functions import Robot

# Immutable command variables
RESET = '0'
BUCKET_ONE = '1'
BUCKET_TWO = '2'
GET_PACKAGE = '3'
PACKAGE_ON_SCALE = '4'
THRESHOLD = '5'
UPDATED_DATABASE = '9'

# Error messages
SCALE = 's'  # scale error
WEIGHT = 'w'  # weighting error
LIGHTBOX1 = 'l'  # light barrier error
LIGHTBOX2 = 'L'  # light barrier error

# Global variables
ip_address = '192.168.1.105'


class Server:
    """
    Starts the server and initializes connection with robot.
    """

    def __init__(self, host, port) -> None:
        """
        Starts the server and initializes connection with robot.
        :param host: Own IP address.
        :type host: str
        :param port: Port to listen on.
        :type port: int
        """
        self.host = host
        self.port = port
        self.robot = Robot()

    def start_server(self):
        """
        Open a server and start listening.
        """
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
        """
        Decode a message and forward command to robot.
        :param message: The message to be decoded.
        :type message: str
        :return: Success or error message.
        :rtype: str
        """
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
            logging.info("Reset command received - Robot will now reset")
            self.robot.reset()
            return "OK: Reset command"

        elif command == BUCKET_ONE:
            logging.info(f"Package sorted to bucket 1 with weight {weight}")
            self.robot.itemToBoxOne()
            return f"OK: Package sorted to bucket 1 with weight {weight}"

        elif command == BUCKET_TWO:
            logging.info(f"Package sorted to bucket 2 with weight {weight}")
            self.robot.itemToBoxTwo()
            return f"OK: Package sorted to bucket 2 with weight {weight}"

        elif command == GET_PACKAGE:
            logging.info(f"Get package command received")
            self.robot.get_package()
            return f"OK: Sent request to get package"

        elif command_char == SCALE:
            logging.error("Scale error: timeout, check MCU>HX711 wiring and pin designations")
            return "ERROR: Scale error"

        elif command_char == WEIGHT:
            logging.error("Weight error: package weights too little or too much")
            return "ERROR: Weight error"

        else:
            logging.error("Unknown command")
            return "ERROR: Unknown command"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = Server(ip_address, 8001)
    server.start_server()
