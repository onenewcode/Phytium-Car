from dora import Node
from Motor import _motor



# 使用数值作为输入 dataw 为单纯的数值，具体参考 motor.py
def main():
    node = Node()
    # 初始化电机
    Control_Motor = _motor(1500, 1500, 1500, 1500)
    Control_Motor.Car_run = 0

    for event in node:
        # 控制车的循环，也许需要加入睡眠机制防止短时间大量指令
        if event["type"] == "INPUT":
            event_id = event["id"]
            if event_id == "move":
                data = event["value"].to_pylist()
                Control_Motor.Car_run = data[0]


if __name__ == "__main__":
    main()
