import socket
import logging


class Session:
    """
    Represents a session for the wareneingang application.

    Attributes:
        host (str): The host address for the session.
        port (int): The port number for the session.
        active (bool): Indicates whether the session is active or not.
        box1Full (bool): Indicates whether box1 is full or not.
        box2Full (bool): Indicates whether box2 is full or not.
        box1 (int): The count of items in box1.
        box2 (int): The count of items in box2.
        threshold (int): The weight threshold in grams.
    """

    def __init__(self):
        self.host = 'localhost'
        self.port = 5001
        self.active = False
        self.box1Full = False
        self.box2Full = False
        self.box1 = 0
        self.box2 = 0
        self.threshold = 50  # in grams
    
    def start_pause(self):
        """
        Toggles the session between active and paused states.
        """
        self.active = not self.active
        print(f'Active: {self.active}')
    
    def increment_box1(self):
        """
        Increments the count of items in box1 by 1.
        """
        self.box1 += 1
        
    def increment_box2(self):
        """
        Increments the count of items in box2 by 1.
        """
        self.box2 += 1

    def send_message(self, message, host, port):
        """
        Sends a message to the specified host and port.

        Args:
            message (str): The message to send.
            host (str): The host address to send the message to.
            port (int): The port number to send the message to.

        Returns:
            str: The response received from the host.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host, port))
            if not isinstance(message, bytes):
                message = message.encode('utf-8')
            s.sendall(message)
            response = s.recv(1024)
            print('Received', response.decode('utf-8'))
            return response.decode('utf-8')
