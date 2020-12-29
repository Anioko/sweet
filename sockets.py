from flask import request
from flask_socketio import SocketIO, join_room

from autoapp import app
socketio = SocketIO(app, cors_allowed_origins="*")


@socketio.on('connect')
def test_connect():
    print("someone connected")


@socketio.on('programme_started')
def programme_started(data):
    room = "event_{}".format(data['event_id'])
    socketio.emit("programme_started", room=room, data={"programme_id": data['programme_id']})
    print("Programme Started", data)


@socketio.on('join_event')
def on_join(data):
    room = "event_"+data['event']
    join_room(room)
    print(f"{request.sid} joined room {room}")

#, certfile='/etc/ssl/certs/apache-selfsigned.crt', keyfile='/etc/ssl/private/apache-selfsigned.key'
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5501)
