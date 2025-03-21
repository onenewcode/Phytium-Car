from dora import Node
from Motor import _motor
import pyarrow as pa

# Stop
# Advance
# Back
# # 平移向左
# Move_Left
# # 平移向右
# Move_Right
# # 左转
# Trun_Right
# # 前左
# Advance_Left
# # 前右
# Advance_Right
# # 后左
# Back_Left
# # 后右
# Back_Right
# # 左旋转
# Rotate_Left
# # 右旋转
# Rotate_Right

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
                data = event["value"]
                # TODO: 确认是否成功，之后找到测试方法
                Control_Motor.Car_run = data


if __name__ == "__main__":
    main()
