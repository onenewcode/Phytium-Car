import cv2
import serial
import struct
import threading
import time
import base64
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import requests
from car_cv import CarCV
from common.move_data import MoveData
from motor.Motor import ModbusMotor, MotorBase
from mycv.color import ColorDetector

app = Flask(__name__)
socketio = SocketIO(app)


@app.route('/')
def index():
    return render_template('index.html')

def get_command(direction):
    commands = {
        'up': MoveData(1,10),  # 前进
        'down': MoveData(2,10),  # 后退
        'left': MoveData(5,10),  # 左转
        'right': MoveData(6,10)  # 右转
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

def cv():
    car_cv = CarCV()
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
    if not cap.isOpened():
        print("无法打开摄像头！")
        return None
    try:
        while True:
            ret, frame = cap.read()
            dector = ColorDetector([30, 70, 80], [50, 255, 255], min_area=300)
            frame, mask, data = dector.process(frame)
            move_data=car_cv.process_image(data)
            # 使用全局变量存储最新的 move_data 和 processed_frame
            global latest_move_data, processed_frame
            latest_move_data = move_data
            processed_frame = frame  # 存储处理后的图像
            # print(f"\r当前移动数据：{move_data}", end='', flush=True)
    finally:
        cap.release()

if __name__ == "__main__":
    # 添加全局变量
    latest_move_data = None
    processed_frame = None
    thread = None
    
    # 创建并启动 CV 线程
    cv_thread = threading.Thread(target=cv, daemon=True)
    cv_thread.start()
    
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
