from dora import Node
from Motor import Motor


# 使用数值作为输入 dataw 为单纯的数值，具体参考 motor.py
def main():
    node = Node()
    # 初始化电机
    Control_Motor = Motor(driver_type="modbus", port="/dev/ttyUSB0")

    for event in node:
        # 控制车的循环，也许需要加入睡眠机制防止短时间大量指令
        if event["type"] == "INPUT":
            event_id = event["id"]
            if event_id == "move":
                data = event["value"].to_pylist()
                Control_Motor.driver.Car_run = data[0]
        elif event["type"] == "STOP":
            Control_Motor.Car_run = 0


if __name__ == "__main__":
    main()
