import socket
import logging
from arduino_commands import *
from robot_functions import Robot
from database import DatabaseManager

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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))  # Bind to the port
        logging.info(f"Server listening on {host}:{port}")

        self.robot = Robot()
        self.db_manager = DatabaseManager('raspi/src/database.db')

    def run(self) -> None:
        """
        Listens for incoming connections, then forwards them to the handler.
        :return: 1
        """
        try:
            while True:
                try:
                    # Receive 1 byte, bcs we know the command is 1 byte
                    command, client_address = self.server_socket.recvfrom(1)
                    if command:
                        logging.debug(f"Client address: {client_address}")
                        # Decode the byte string
                        self.handleCommand(command[0])
                        self.relayCommand(str(command[0]))
                except Exception as e:
                    logging.exception(e)
        finally:
            self.db_manager.close()
            logging.debug("Server shut down and database closed")

    def relayCommand(self, message, server_address=('localhost', 5001)) -> None:
        """
        Relay a command by sending a message to a server at the specified address.

        :param message: The message to send to the server.
        :param server_address: The address of the server to connect to. Defaults to ('localhost', 5001).
        :type server_address: Tuple[str, int]
        :return: None
        :rtype: None
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            # Send message to server
            s.connect(server_address)
            s.sendall(message.encode())
            logging.debug(f"Relay command sent to {server_address}")

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
