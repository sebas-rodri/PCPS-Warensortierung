import socket
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
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind((host, port))  # Bind to the port
        print(f"Server listening on {host}:{port}")

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
                    print(client_address)
                    # Decode the byte string
                    self.handleCommand(command[0])
            except Exception as e:
                print(f"Error: {e}")

    def handleCommand(self, command: int) -> None:
        """
        Handles the given command.

        :param command: The command to be handled.
        :return: None
        """
        if command == RESET:
            self.robot.reset()
        elif command == BUCKET_ONE:
            self.robot.itemToBoxOne()
        elif command == BUCKET_TWO:
            self.robot.itemToBoxTwo()
        else:
            print("Invalid command")

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
            print("Error:", e)
            return None


if __name__ == "__main__":
    server = Server('0.0.0.0', 2360)

