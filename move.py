from dora import Node
import pyarrow as pa
import time
class Move:
    def __init__(node):
        self.node = node
    def send(self):
        """
        发送运动数据给其他节点
        Args:
            direction (int): 运动的方向。

        Returns:
            bool: 是否发送成功。

        Raises:
            ZeroDivisionError: 如果除数为零，则抛出异常。
        """
        direction = pa.array([direction])
        self.node.send_output("move")
    def stop(self):
        return self.send(0)
    def advance(self):
        return self.send(1)

    def Back(self):
        return self.send(2)

    def move_left(self):
        return self.send(3)
    def move_right(self):
        return self.send(4)

    def turn_left(self):
        return self.send(5)

    def turn_right(self):
        return self.send(6)

    def advance_left(self):
        return self.send(7)

    def advance_right(self):
        return self.send(8)

    def back_left(self):
        return self.send(9)

    def back_right(self):
        return self.send(10)

    def rotate_left(self):
        return self.send(11)

    def rotate_right(self):
        return self.send(12)
