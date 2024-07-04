import socket
import logging
from arduino_commands import *
from robot_functions import Robot


class Server:
    """
    Starts the server and initializes connection with robot.

    :param host: The host address to bind the server to.
    :param port: The port to bind the server to.
    """

    def __init__(self, host, port) -> None:
        """
        Starts the server and initializes connection with robot.
        """
        self.host = host
        self.port = port

        self.robot = Robot()

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
            return f"OK: Package sorted to bucket 1 with weight {weight}"

        elif command == BUCKET_TWO:
            logging.info(f"Package sorted to bucket 2 with weight {weight}")
            return f"OK: Package sorted to bucket 2 with weight {weight}"

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

    def send_message(self, message, host, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            s.sendall(message.encode('utf-8'))
            response = s.recv(1024)
            print('Received', response.decode('utf-8'))

    @staticmethod
    def getLocalIP():
        """
        Returns the IP address of the local machine.
        :return: IP address
        """
        try:
            # Create a socket object
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Connect to a remote server (doesn't matter which one)
            s.connect(("8.8.8.8", 80))
            # Get the local IP address of the connected socket
            local_ip = s.getsockname()[0]
            # Close the socket
            s.close()
            return local_ip
        except Exception as e:
            logging.exception(e)
            return None


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = Server('0.0.0.0', 8000)
    server.start_server()
