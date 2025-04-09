import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/../')
from dora import Node
from Motor import MotorBase,ModbusMotor
from common.move_data import MoveData


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# 使用数值作为输入 dataw 为单纯的数值，具体参考 motor.py
def main():
    node = Node()
    # 初始化电机
    car_controller:MotorBase = ModbusMotor(port="/dev/ttyUSB0") 

    for event in node:
        # 控制车的循环，也许需要加入睡眠机制防止短时间大量指令
        if event["type"] == "INPUT":
            event_id = event["id"]
            if event_id == "move":
                # 将 pyarrow Array 转换为 MoveData 对象
                data = event["value"]
                move_data = MoveData.from_arrow_array(data)
                car_controller.Control(move_data)
        elif event["type"] == "STOP":
            move_data = MoveData(0, 0)
            car_controller.Control(move_data)


if __name__ == "__main__":
    main()
