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
THRESHOLD = '5'
UPDATED_DATABASE = '9'

# Error messages
MALLOC = 'm'  # malloc error
SCALE = 's'   # scale error
WEIGHT = 'w'  # weighting error
LIGHTBOX1 = 'l'   # light barrier error
LIGHTBOX2 = 'L'   # light barrier error
WIFI = 'i'    # internet error
TCP = 't'     # server error


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('get_counter_value')
def handle_get_counter_value():
    print('Getting counter value')
    socketio.emit('set_counter1', {'value': activeSession.box1}, namespace='/')
    socketio.emit('set_counter2', {'value': activeSession.box2}, namespace='/')

@socketio.on('get_threshold')
def handle_get_threshold():
    print('Getting threshold')
    socketio.emit('set_threshold', {'value': activeSession.threshold}, namespace='/')

@socketio.on('get_if_full')
def handle_get_if_full():
    logging.info('Getting if full')
    if activeSession.box1Full:
        box1full()
    if activeSession.box2Full:
        box2full()
@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def increment(box):
    print(f'Incrementing {box}')
    if box == 'box1':
        activeSession.increment_box1()
        print(activeSession)
        socketio.emit('update_counter1',namespace='/', data={'value': activeSession.box1})
    elif box == 'box2':
        activeSession.increment_box2()
        socketio.emit('update_counter2', {'value': activeSession.box2},namespace='/')

def box1full():
    logging.info('Box 1 is full')
    activeSession.box1Full = True
    socketio.emit('box1_full', {'value': activeSession.box1}, namespace='/')

def box2full():
    logging.info('Box 2 is full')
    activeSession.box2Full = True
    socketio.emit('box2_full', {'value': activeSession.box2}, namespace='/')

@socketio.on('empty_box1')
def box1empty():
    logging.info('Box 1 is empty')
    activeSession.box1Full = False
    socketio.emit('enable_button', namespace='/')
    socketio.emit('box1_empty', {'value': activeSession.box1}, namespace='/')

@socketio.on('empty_box2')
def box2empty():
    logging.info('Box 2 is empty')
    activeSession.box2Full = False
    socketio.emit('enable_button', namespace='/')
    socketio.emit('box2_empty', {'value': activeSession.box2}, namespace='/')

@socketio.on('message_from_client')
def handle_message(data):
    print(f'Message from client: {data}')
    # Process the message and optionally emit back to the client
    socketio.emit('message_from_server', {'response': 'Message received'})

@socketio.on('start/pause')
def handle_start_pause():
    activeSession.start_pause()
    message = '3/100'
    activeSession.send_message(message, 'localhost', 8000)


@socketio.on('threshold')
def update_threshold(data):
    activeSession.threshold = int(data['theshold'])
    logging.info(f'Threshold updated to {activeSession.threshold}')
    activeSession.send_message('5/'+str(activeSession.threshold), 'localhost', 8000)

def handle_request(message):
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
        # TODO GET NEW DATA FROM DATABASE
        logging.info(f"Received updated database: {message}")
        # response = activeSession.send_message('get_data', 'localhost', 8000)
        if weight > activeSession.threshold:
            
            increment('box2')
            
        else:
            increment('box1')
        # handle_get_counter_value()
        print(weight,activeSession.threshold)
        socketio.emit('enable_button', namespace='/')
        return "OK: Updated database"

    
    # Handling error messages
    elif command_char == MALLOC:
        logging.error("Malloc error: failed to allocate memory for boxes array")
        return "ERROR: Malloc error"

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

    elif command_char == WIFI:
        logging.error("WiFi error: communication with WiFi module failed")
        return "ERROR: WiFi error"

    elif command_char == TCP:
        logging.error("TCP error: failed to connect to TCP server")
        return "ERROR: TCP error"

    else:
        logging.error("Unknown command")
        return "ERROR: Unknown command"


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('192.168.1.105', 5001))
        s.listen()
        logging.info(f"Server started and listening on 192.168.1.105:5001")

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
    socketio.run(app, debug=False, host='0.0.0.0', port=4999, allow_unsafe_werkzeug=True)


