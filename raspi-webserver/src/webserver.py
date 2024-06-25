from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
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
    

def test_thread():
    while True:
        time.sleep(1)
        command = input('Enter command: ')
        if command == '1':
            increment('box1')
        elif command == '2':
            increment('box2')
        elif command == 'full':
            box1full()
        elif command == 'empty':
            box1empty()
        elif command == 'q':
            break

def handle_data(data):
    #TODO: Implemented full functionality
    if data == b'box1':
        increment('box1')
    elif data == b'box2':
        increment('box2')
    elif data == b'full':
        box1full()
    elif data == b'empty':
        box1empty()

def listener_thread():
        print('Listener thread')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('0.0.0.0', 5001))
            s.listen()
            print('Listening on port 5001')
            while True:
                time.sleep(1)
                client, addr = s.accept()
                with client:
                    print('Connected by', addr)
                    while True:
                        data = client.recv(1024)
                        if not data:
                            break
                        handle_data(data)          

if __name__ == '__main__':
    activeSession = Session()
    thread = threading.Thread(target=listener_thread)
    thread.start()
    socketio.run(app, debug=False, host='0.0.0.0',port=4999)
