from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import logging
import time
from session import Session
import socket

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')

# Immutable command variables
RESET = '0'
BUCKET_ONE = '1'
BUCKET_TWO = '2'
GET_PACKAGE = '3'
PACKAGE_ON_SCALE = '4'
THRESHOLD = '5'
UPDATED_DATABASE = '9'

# Error messages
SCALE = 's'   # scale error
WEIGHT = 'w'  # weighting error
LIGHTBOX1 = 'l'   # light barrier error
LIGHTBOX2 = 'L'   # light barrier error

# Global variables
ip_address = '192.168.1.105'
PORT_WEBSITE = 4999
PORT_WEBSERVER = 5001
PORT_BACKEND = 8000

############################################
# SocketIO event handlers

@app.route('/')
def index():
    """
    Renders a website.
    @return: The rendered website.
    """
    return render_template('index.html')


@socketio.on('connect')
def handle_connect():
    """
    Handles the connection with a client.

    This function is called when a client connects to the server.
    It prints a message indicating that a client has connected.

    Parameters:
        None

    Returns:
        None
    """
    logging.info('Client connected')


@socketio.on('get_counter_value')
def handle_get_counter_value():
    """
    Handles the retrieval of counter values and emits them to the clients.

    This function retrieves the values of the counters from the active session
    and emits them to the clients using the socketio library.

    Parameters:
        None

    Returns:
        None
    """
    logging.info('Getting counter value')
    socketio.emit('set_counter1', {'value': activeSession.box1}, namespace='/')
    socketio.emit('set_counter2', {'value': activeSession.box2}, namespace='/')


@socketio.on('get_threshold')
def handle_get_threshold():
    """
    Handles the GET request for retrieving the threshold value.

    Emits the threshold value to the client using the 'set_threshold' event.

    Parameters:
        None

    Returns:
        None
    """
    logging.info('Getting threshold')
    socketio.emit('set_threshold', {'value': activeSession.threshold}, namespace='/')


@socketio.on('get_if_full')
def handle_get_if_full():
    """
    Handles the GET request to check if the boxes are full.
    
    This function checks if the boxes (box1 and box2) are full in the active session.
    If box1 is full, it calls the `box1full` function.
    If box2 is full, it calls the `box2full` function.
    
     Parameters:
        None

    Returns:
        None
    """
    logging.info('Getting if full')
    if activeSession.box1Full:
        box1full()
    if activeSession.box2Full:
        box2full()


@socketio.on('disconnect')
def handle_disconnect():
    """
    Handles the event when a client disconnects from the server.
    """
    logging.info('Client disconnected')



@socketio.on('empty_box1')
def box1empty():
    """
    Marks Box 1 as empty and emits events to update the client-side UI.

    This function sets the `box1Full` attribute of the `activeSession` object to False,
    indicating that Box 1 is empty. It then emits two events using the `socketio` object:
    - 'enable_button': Enables a button on the client-side UI.
    - 'box1_empty': Sends a dictionary with the value of `activeSession.box1` to update the client-side UI.

    Note: This function assumes that the `activeSession` and `socketio` objects are already defined.

    """
    logging.info('Box 1 is empty')
    activeSession.box1Full = False
    socketio.emit('enable_button', namespace='/')
    socketio.emit('box1_empty', {'value': activeSession.box1}, namespace='/')


@socketio.on('empty_box2')
def box2empty():
    """
    Marks Box 2 as empty and emits events to update the client-side UI.

    This function sets the `box2Full` attribute of the `activeSession` object to False,
    indicating that Box 2 is now empty. It then emits two events using the `socketio`
    object to update the client-side UI. The first event, 'enable_button', enables a
    button on the UI, and the second event, 'box2_empty', sends the updated value of
    `activeSession.box2` to the client.

    """
    logging.info('Box 2 is empty')
    activeSession.box2Full = False
    socketio.emit('enable_button', namespace='/')
    socketio.emit('box2_empty', {'value': activeSession.box2}, namespace='/')

@socketio.on('message_from_client')
def handle_message(data):
    logging.info(f'Message from client: {data}')
    # Process the message and optionally emit back to the client
    socketio.emit('message_from_server', {'response': 'Message received'})


@socketio.on('start/pause')
def handle_start_pause():
    """
    Handles the Pickup button event.

    Parameters:
        None

    Returns:
        None
    """
    activeSession.start_pause()
    message = '3/100'
    activeSession.send_message(message, ip_address, PORT_BACKEND)


@socketio.on('threshold')
def update_threshold(data):
    """
    Updates the threshold value for the active session.

    Args:
        data: SocketIO event data containing the new threshold value.

    Returns:
        None

    """
    activeSession.threshold = int(data['theshold'])
    logging.info(f'Threshold updated to {activeSession.threshold}')
    thresholdstr = '5/' + str(activeSession.threshold)
    if activeSession.threshold < 10:
        thresholdstr = '5/00' + str(activeSession.threshold)
    elif activeSession.threshold < 100:
        thresholdstr = '5/0' + str(activeSession.threshold)
    activeSession.send_message(thresholdstr, ip_address, PORT_BACKEND)

############################################
# Server functions

def increment(box):
    """
    Increments the counter for the specified box and emits an update event.

    Args:
        box (str): The name of the box to increment ('box1' or 'box2').

    Returns:
        None
    """
    logging.info(f'Incrementing {box}')
    if box == 'box1':
        activeSession.increment_box1()
        logging.info(activeSession)
        socketio.emit('update_counter1', namespace='/', data={'value': activeSession.box1})
    elif box == 'box2':
        activeSession.increment_box2()
        socketio.emit('update_counter2', {'value': activeSession.box2}, namespace='/')



def box1full():
    """
    This function is called when Box 1 is full.
    It logs the event, updates the `box1Full` flag in the active session, and emits a socketio event to notify the clients.

    Parameters:
    None

    Returns:
    None
    """
    logging.info('Box 1 is full')
    activeSession.box1Full = True
    socketio.emit('box1_full', {'value': activeSession.box1}, namespace='/')

def box2full():
    """
    Sets the 'box2Full' flag to True and emits a socketio event indicating that Box 2 is full.

    This function is called when Box 2 is detected to be full.

    Parameters:
        None

    Returns:
        None
    """
    logging.info('Box 2 is full')
    activeSession.box2Full = True
    socketio.emit('box2_full', {'value': activeSession.box2}, namespace='/')



def handle_request(message):
    """
    Handles the incoming request message and performs the necessary actions based on the command and weight.

    Args:
        message (str): The incoming request message.

    Returns:
        str: The response message indicating the result of the request.

    Raises:
        ValueError: If the command or weight is invalid.

    """
    logging.info(f"Received message: {message}")

    if len(message) < 5 or message[1] != '/':
        logging.error("Invalid message format")
        return "ERROR: Invalid message format"

    command_char = message[0]
    command = None
    weight = None

    try:
        command = command_char
        weight = int(message[2:5])
    except ValueError:
        logging.error(f"Invalid command or weight: {command_char}, {message[2:5]}")
        return "ERROR: Invalid command or weight"

    if command == UPDATED_DATABASE:
        logging.info(f"Received updated database: {message}")
        if weight > activeSession.threshold:
            increment('box2')

        else:
            increment('box1')
        # handle_get_counter_value()
        logging.info(weight,activeSession.threshold)
        socketio.emit('enable_button', namespace='/')
        return "OK: Updated database"

    # Handling error messages
    elif command_char == SCALE:
        logging.error("Scale error: timeout, check MCU>HX711 wiring and pin designations")
        return "ERROR: Scale error"

    elif command_char == WEIGHT:
        logging.error("Weight error: package weights too little or too much")
        socketio.emit('weight_error', namespace='/')
        socketio.emit('enable_button', namespace='/')
        return "ERROR: Weight error"

    elif command_char == LIGHTBOX1:
        logging.error("Light barrier error: the light barrier was triggered")
        box1full()
        return "ERROR: Light barrier error"

    elif command_char == LIGHTBOX2:
        logging.error("Light barrier error: the light barrier was triggered")
        box2full()
        return "ERROR: Light barrier error"

    else:
        logging.error("Unknown command")
        return "ERROR: Unknown command"


def start_server():
    """
    Listens for incoming connections.

    The server binds to the specified IP address and port 5001. It accepts incoming connections,
    receives data from the client, and sends a response back.

    Returns:
        None
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip_address, PORT_WEBSERVER))
        s.listen()
        logging.info(f"Server started and listening on {ip_address}:5001")

        while True:
            conn, addr = s.accept()
            with conn:
                logging.info(f"Connected by {addr}")
                data = conn.recv(1024)
                if data:
                    response = handle_request(data.decode('utf-8'))
                    conn.sendall(response.encode('utf-8'))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    activeSession = Session()
    thread = threading.Thread(target=start_server)
    thread.start()
    socketio.run(app, debug=False, host=ip_address, port=PORT_WEBSITE, allow_unsafe_werkzeug=True)

