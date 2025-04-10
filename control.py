import serial
import struct
import threading
import time
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests

from common.move_data import MoveData
from motor.Motor import ModbusMotor, MotorBase

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')

def get_command(direction):
    commands = {
        'up': MoveData(1,100),  # 前进
        'down': MoveData(2,100),  # 后退
        'left': MoveData(5,100),  # 左转
        'right': MoveData(6,100)  # 右转
    }
    return commands.get(direction)

@socketio.on('control')
def handle_control(data):
    direction = data.get('direction')
    if direction in ['up', 'down', 'left', 'right']:
        car_controller.Control(get_command(direction))
        emit('response', {'status': 'Moving ' + direction})
    else:
        move_data = MoveData(0,0)
        car_controller.Control(move_data)
        emit('response', {'status': 'Stopped'})

@socketio.on('disable')
def handle_disable():
    move_data = MoveData(0,0)
    car_controller.Control(move_data)
    emit('response', {'status': 'Disabled'})

if __name__ == "__main__":
    port_name = '/dev/ttyUSB0'  # 串口名称，根据实际情况修改
    car_controller:MotorBase = ModbusMotor(port=port_name)

    # 在启动 Flask 服务器之前，向 HTTP 服务器发送一次数据
    http_server_url = 'http://****'  # HTTP 服务器地址，根据实际情况修改
    status_data = {
        "status": "Ready",
        "message": "Car control system is ready."
    }
    try:
        response = requests.post(http_server_url, json=status_data)
        if response.status_code == 200:
            print("Data sent successfully to the HTTP server.")
        else:
            print(f"Failed to send data to the HTTP server: {response.status_code}, {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending data to the HTTP server: {e}")

    socketio.run(app, host='0.0.0.0', port=5000)
