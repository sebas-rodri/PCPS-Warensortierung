import socket
import logging
from arduino_commands import *
from robot_functions import Robot
from database import DatabaseManager

RASPI_IP = '0.0.0.0'
RASPI_PORT = 2360
ARDUINO_IP = ''
ARDUINO_PORT = 0
MSG_BYTES = 0

class Server:
    """
    Starts the server and initializes connection with robot.
    """
    def __init__(self) -> None:
        """
        Starts the server and initializes connection with robot.
        """
        # Set up a TCP/IP server
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to raspberry's address and port
        self.tcp_socket.bind((RASPI_IP, RASPI_PORT))

        # Listen for 2 clients
        self.tcp_socket.listen(2)
        logging.info(f"Server listening on {RASPI_IP}:{RASPI_PORT}")

        self.robot = Robot()
        self.db_manager = DatabaseManager('raspi/src/database.db')

    def run(self) -> None:
        """
        Listens for incoming connections, then forwards them to the handler.
        :return: 1
        """
        try:
            while True:
                print("Waiting for connection")
                connection, client = self.tcp_socket.accept()

                try:
                    print("Connected to client IP: {}".format(client))

                    # Receive and print data MSG_BYTES bytes at a time, as long as the client is sending something
                    while True:
                        data = connection.recv(MSG_BYTES) # data is in bytes, has to be formatted to ascii
                        # print("Received data: {}".format(data))
                        self.deconstructData(data)

                        if not data:
                            break

                finally:
                    connection.close()
        finally:
            self.db_manager.close()
            logging.debug("Server shut down and database closed")

    """
    deconstruct the data received.
    """
    def deconstructData(self, data: bytes) -> None:
        # data from database in * (*data*)
        # data from arduino in ! (!data!)
        self.handleCommand(-1)

    """
    handle commands to robot
    """
    def handleCommand(self, command: int) -> None:
        """
        Handles the given command.

        :param command: The command to be handled.
        :return: None
        """
        if command == RESET:
            logging.info(f"Reset command received")
            self.robot.reset()
        elif command == BUCKET_ONE:
            logging.info(f"Bucket one command received")
            self.robot.itemToBoxOne()
            weight_of_packet = 100 # tbd
            self.db_manager.set(weight_of_packet, 1)
        elif command == BUCKET_TWO:
            logging.info(f"Bucket two command received")
            self.robot.itemToBoxTwo()
            weight_of_packet = 100 # tbd
            self.db_manager.set(weight_of_packet, 2)
        else:
            logging.error("Invalid command")

    """
    send Data to arduino server
    """
    def sendData(self, message: str) -> None:
        # Create a connection to the server application on port 81
        tcp_socket = socket.create_connection(('localhost', 81))

        try:
            data = str.encode(message)
            tcp_socket.sendall(data)

        finally:
            print("Closing socket")
            tcp_socket.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = Server('0.0.0.0', 8000)
    server.run()
