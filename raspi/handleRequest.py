import socket 
from arduino_commands import *
host = '0.0.0.0'
port = 2360


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


def get_local_ip():
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

def startServer() -> None:
    """
    Starts the server and listens for incoming connections.
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((host, port)) # Bind to the port
    print(f"Server listening on {host}:{port}")

    while True:
        try:
            command, client_address = server_socket.recvfrom(1) # Receive 1 byte, bcs we know the command is 1 byte
            if command:
                print(client_address)
                handleCommand(command[0]) # Decode the byte string
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    print(get_local_ip())
    startServer()
