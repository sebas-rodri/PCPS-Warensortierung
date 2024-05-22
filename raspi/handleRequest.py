import socket 
from arduino_commands import *
from robot_functions import Robot
host = '0.0.0.0'
port = 12345


def handleCommand(command) -> None:
    """
    Handles the given command.

    Parameters:
    command (int): The command to be handled.

    Returns:
    None

    Raises:
    None
    """
    command = int(command) # Convert the string to an integer
    if command == RESET:
        print("Reset")
    elif command == BUCKET_ONE:
        print("Bucket one")
    elif command == BUCKET_TWO:
        print("Bucket two")
    else:
        print("Invalid command")


def startServer() -> None:
    """
    Starts the server and listens for incoming connections.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port)) # Bind to the port
    server_socket.listen(5)
    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        try:
            command = client_socket.recv(1) # Receive 1 byte, bcs we know the command is 1 byte
            if command:
                handleCommand(command.decode("utf-8")) # Decode the byte string
            client_socket.close()
        except Exception as e:
            print(f"Error: {e}")
            client_socket.close()

if __name__ == "__main__":
    startServer()
