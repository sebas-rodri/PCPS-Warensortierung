import socket
from arduino_commands import *
from robot_functions import Robot
import logging


class Server:
    def __init__(self, host, port) -> None:
        """
        Starts the server and initializes connection with robot.
        """
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))  # Bind to the port
        logging.info(f"Server listening on {host}:{port}")

        self.robot = Robot()

    def run(self) -> None:
        """
        Listens for incoming connections, then forwards them to the handler.
        :return: 1
        """
        while True:
            try:
                # Receive 1 byte, bcs we know the command is 1 byte
                command, client_address = self.server_socket.recvfrom(1)
                if command:
                    logging.debug(f"Client address: {client_address}")
                    # Decode the byte string
                    self.handleCommand(command[0])
            except Exception as e:
                logging.exception(e)

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
        elif command == BUCKET_TWO:
            logging.info(f"Bucket two command received")
            self.robot.itemToBoxTwo()
        else:
            logging.error("Invalid command")

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
    server = Server('0.0.0.0', 2360)
    server.run()
