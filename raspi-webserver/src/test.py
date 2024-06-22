from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


class Session:
    def __init__(self):
        self.active = True
        self.box1 = 0
        self.box2 = 0
    
    def start_pause(self):
        self.active = not self.active
        print(f'Active: {self.active}')
    
    def update_box1(self, value):
        self.box1 = value
        print(f'Box1: {self.box1}')
    
    def update_box2(self, value):
        self.box2 = value
        print(f'Box2: {self.box2}')
    
    def increment_box1(self):
        self.box1 += 1
        print(f'Box1: {self.box1}')
    
    def increment_box2(self):
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

@socketio.on('message_from_client')
def handle_message(data):
    print(f'Message from client: {data}')
    # Process the message and optionally emit back to the client
    emit('message_from_server', {'response': 'Message received'})

@socketio.on('start/pause')
def handle_start_pause():
    session.start_pause()

if __name__ == '__main__':
    session = Session()
    socketio.run(app, debug=True)
