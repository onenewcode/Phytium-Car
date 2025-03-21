from dora import Node
from Motor import _motor
import pyarrow as pa

# 字符串进行传递移动状态和方向，这里使用 scalar 进行抓换和传递
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


def main():
    node = Node()
    for event in node:
        if event["type"] == "INPUT":
            event_id = event["id"]
            if event_id == "move":
                data = event["value"]


if __name__ == "__main__":
    main()
