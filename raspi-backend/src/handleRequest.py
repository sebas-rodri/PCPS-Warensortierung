import logging
import socket

from database import DatabaseManager


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

        command = int(message[0])
        weight = int(message[2:5])

        if command == 0:
            logging.info("Neutral position - no action taken")
            return "OK: Neutral position"

        elif command == 1:
            self.db_manager.set(weight, 1)
            logging.info(f"Package sorted to box 1 with weight {weight}")
            return f"OK: Package sorted to box 1 with weight {weight}"

        elif command == 2:
            self.db_manager.set(weight, 2)
            logging.info(f"Package sorted to box 2 with weight {weight}")
            return f"OK: Package sorted to box 2 with weight {weight}"

        elif command == 3:
            # Implement fetching package logic if necessary
            logging.info(f"Fetching package information")
            return "OK: Package fetched (dummy response)"

        else:
            logging.error("Unknown command")
            return "ERROR: Unknown command"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    server = PackageSortingServer()
    server.start_server()
