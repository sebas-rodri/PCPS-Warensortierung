from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

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

if __name__ == '__main__':
    socketio.run(app, debug=True)
