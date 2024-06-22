from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import threading
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='threading')


class Session:
    def __init__(self):
        self.active = True
        self.box1 = 0
        self.box2 = 0
        self.lock = threading.Lock()
    
    def start_pause(self):
        self.active = not self.active
        print(f'Active: {self.active}')
    
    def update_box1(self, value):
        with self.lock:
            self.box1 = value
            print(f'Box1: {self.box1}')
    
    def update_box2(self, value):
        self.box2 = value
        print(f'Box2: {self.box2}')
    
    def increment_box1(self):
        with self.lock:
            self.box1 += 1
            print(f'Box1: {self.box1}')
        
    def increment_box2(self):
        with self.lock:
            self.box2 += 1
            print(f'Box2: {self.box2}')
    
    def decrement_box1(self):
        if self.box1 > 0:
            self.box1 -= 1
        print(f'Box1: {self.box1}')
    
    def decrement_box2(self):
        if self.box2 > 0:
            self.box2 -= 1
        print(f'Box2: {self.box2}')
    

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

if __name__ == '__main__':
    activeSession = Session()
    thread = threading.Thread(target=test_thread)
    thread.start()
    socketio.run(app, debug=False)
