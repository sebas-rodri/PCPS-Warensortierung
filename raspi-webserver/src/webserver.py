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
SCALE = 's'  # scale error
WEIGHT = 'w'  # weighting error
LIGHTBOX1 = 'l'  # light barrier error
LIGHTBOX2 = 'L'  # light barrier error

# Global variables
ip_address = '192.168.1.105'


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
    Placeholder for implementation of further features on connection with client.
    """
    print('Client connected')


@socketio.on('get_counter_value')
def handle_get_counter_value():
    """
    Saving values of counters of current session.
    """
    print('Getting counter value')
    socketio.emit('set_counter1', {'value': activeSession.box1}, namespace='/')
    socketio.emit('set_counter2', {'value': activeSession.box2}, namespace='/')


@socketio.on('get_threshold')
def handle_get_threshold():
    """
    Saving threshold of current session.
    """
    print('Getting threshold')
    socketio.emit('set_threshold', {'value': activeSession.threshold}, namespace='/')


@socketio.on('get_if_full')
def handle_get_if_full():
    """
    Saving status of boxes of current session.
    """
    logging.info('Getting if full')
    if activeSession.box1Full:
        box1full()
    if activeSession.box2Full:
        box2full()


@socketio.on('disconnect')
def handle_disconnect():
    """
    Placeholder for implementation of further features on disconnection with client.
    """
    print('Client disconnected')


def increment(box):
    """
    Increment the counter of packages in the specified box.
    @param box: ID of box to increment.
    @type box: str
    """
    print(f'Incrementing {box}')
    if box == 'box1':
        activeSession.increment_box1()
        print(activeSession)
        socketio.emit('update_counter1', namespace='/', data={'value': activeSession.box1})
    elif box == 'box2':
        activeSession.increment_box2()
        socketio.emit('update_counter2', {'value': activeSession.box2}, namespace='/')


def box1full():
    """
    Set box 1 to full.
    """
    logging.info('Box 1 is full')
    activeSession.box1Full = True
    socketio.emit('box1_full', {'value': activeSession.box1}, namespace='/')


def box2full():
    """
    Set box 2 to full.
    """
    logging.info('Box 2 is full')
    activeSession.box2Full = True
    socketio.emit('box2_full', {'value': activeSession.box2}, namespace='/')


@socketio.on('empty_box1')
def box1empty():
    """
    Set box 1 to empty.
    """
    logging.info('Box 1 is empty')
    activeSession.box1Full = False
    socketio.emit('enable_button', namespace='/')
    socketio.emit('box1_empty', {'value': activeSession.box1}, namespace='/')


@socketio.on('empty_box2')
def box2empty():
    """
    Set box 2 to empty.
    """
    logging.info('Box 2 is empty')
    activeSession.box2Full = False
    socketio.emit('enable_button', namespace='/')
    socketio.emit('box2_empty', {'value': activeSession.box2}, namespace='/')


@socketio.on('start/pause')
def handle_start_pause():
    """
    Set a new threshold. Send fitting message to raspi-backend.
    """
    activeSession.start_pause()
    message = '3/100'
    activeSession.send_message(message, ip_address, 8000)


@socketio.on('threshold')
def update_threshold(data):
    """
    Set a new threshold. Send fitting message to raspi-backend.
    @param data: Value of threshold in gram.
    @type data: int
    """
    activeSession.threshold = int(data['threshold'])
    logging.info(f'Threshold updated to {activeSession.threshold}')
    thresholdstr = '5/' + str(activeSession.threshold)
    if activeSession.threshold < 10:
        thresholdstr = '5/00' + str(activeSession.threshold)
    elif activeSession.threshold < 100:
        thresholdstr = '5/0' + str(activeSession.threshold)
    activeSession.send_message(thresholdstr, ip_address, 8000)


def handle_request(message):
    """
    Decode and handle incoming commands.
    @param message: Message to be decoded.
    @type message: str
    @return: Success or error message.
    @rtype: str
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
        print(weight, activeSession.threshold)
        socketio.emit('enable_button', namespace='/')
        return "OK: Updated database"

    # Handling error messages
    elif command_char == SCALE:
        logging.error("Scale error: timeout, check MCU>HX711 wiring and pin designations")
        return "ERROR: Scale error"

    elif command_char == WEIGHT:
        logging.error("Weight error: package weights too little or too much")
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
    Open a server and start listening.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((ip_address, 5001))
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
    socketio.run(app, debug=False, host=ip_address, port=4999, allow_unsafe_werkzeug=True)