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


@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('connect')
def handle_connect():
    print('Client connected')

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
    print('Box 1 is full')
    socketio.emit('box1_full', {'value': activeSession.box1}, namespace='/')

def box1empty():
    print('Box 1 is empty')
    socketio.emit('box1_empty', {'value': activeSession.box1}, namespace='/')

@socketio.on('message_from_client')
def handle_message(data):
    print(f'Message from client: {data}')
    # Process the message and optionally emit back to the client
    socketio.emit('message_from_server', {'response': 'Message received'})

@socketio.on('start/pause')
def handle_start_pause():
    activeSession.start_pause()

@socketio.on('get_counter_value')
def handle_get_counter_value():
    print('Getting counter value')
    socketio.emit('set_counter1', {'value': activeSession.box1}, namespace='/')
    socketio.emit('set_counter2', {'value': activeSession.box2}, namespace='/')


def start_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('localhost', 5001))
        s.listen()
        logging.info(f"Server started and listening on localhost:5001")

        while True:
            conn, addr = s.accept()
            with conn:
                logging.info(f"Connected by {addr}")
                data = conn.recv(1024)
                if data:
                    response = activeSession.handle_request(data.decode('utf-8'))
                    conn.sendall(response.encode('utf-8'))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    activeSession = Session()
    thread = threading.Thread(target=start_server)
    thread.start()
    socketio.run(app, debug=False, host='localhost', port=4999, allow_unsafe_werkzeug=True)
