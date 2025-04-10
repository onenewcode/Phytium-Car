from dora import Node
import cv2
from traitlets import List
from common.move_data import MoveData
from move import Move
from mycv import ColorDetector
import time
from untils import Calculate
from simple_pid import PID


def send(node: Node, direction, speed) -> MoveData:
    """
    发送运动数据给其他节点
    Args:
        direction (int): 运动的方向。

    Returns:
        bool: 是否发送成功。

    Raises:
        ZeroDivisionError: 如果除数为零，则抛出异常。
    """
    data = MoveData(direction, speed).to_arrow_array()
    if node != None:
        node.send_output("move", data)
    return MoveData(direction, speed)


def stop(node: Node) -> MoveData:
    return send(node, 0, 0)


def advance(node: Node, speed=2) -> MoveData:
    return send(node, 1, speed)


def back(node: Node, speed=2) -> MoveData:
    return send(node, 2, speed)


def turn_left(node: Node, speed=20) -> MoveData:
    return send(node, 5, speed)


def turn_right(node: Node, speed=20) -> MoveData:
    return send(node, 6, speed)


class CarCV:

    def __init__(self):
        self.lower_tennis = [30, 70, 80]
        self.upper_tennis = [50, 255, 255]
        self.detector = ColorDetector(
            self.lower_tennis, self.upper_tennis, min_area=300
        )

        self.last_command = "stop"
        self.lost_count = 20
        self.max_lost_frames = 20
        self.search_direction = 1
        self.search_start_time = 0
        self.last_command_time = time.time()
        self.target_found = False
        self.last_valid_position = None
        self.debug_mode = False
        self.recet_pos = (210, 354, 100, 100)
        self.center_x = 278
        self.center_y = 298
        self.width = 640
        self.height = 480
        self.arm_state_Ready = True
        self.ratio_abs = 0.01
        self.ratio_num = 0.02056640625

        # 添加低通滤波器参数
        self.alpha = 0.2  # 平滑因子 (0-1)
        self.last_x_offset = 0
        self.last_y_offset = 0

        # 添加 PID 控制器
        self.pid_distance = PID(Kp=1.0, Ki=0.1, Kd=0.05, setpoint=0.9)
        self.pid_distance.output_limits = (1.0, 5.0)  # 限制输出范围

        # 添加速度平滑参数
        self.current_speed = 0.0
        self.max_acceleration = 0.5  # 最大加速度
        self.last_speed_update_time = time.time()
        self.max_speed = 100
        self.min_speed = 2

    def process_image(self, data: List[Calculate], node=None) -> MoveData:

        current_time = time.time()

        if self.arm_state_Ready:
            if len(data) == 0:
                return self.handle_target_lost(current_time, node)
            else:
                return self.handle_target_found(
                    data[0].x, data[0].y, data[0].ratio, current_time, node
                )
        else:
            return stop(node)

    def handle_target_lost(self, current_time, node) -> MoveData:
        self.lost_count += 1
        self.target_found = False

        if self.lost_count >= self.max_lost_frames:
            self.last_command_time = current_time
          
            return turn_right(node)
        else:
     
            return turn_right(node)

    def low_pass_filter(self, new_value, last_value):
        """低通滤波器"""
        return self.alpha * new_value + (1 - self.alpha) * last_value

    def handle_target_found(self, x, y, ratio, current_time, node) -> MoveData:
        self.lost_count = 0
        self.target_found = True
        self.last_valid_position = (x, y)
        self.last_command_time = current_time

        # 计算原始偏移
        raw_x_offset = x - self.center_x
        raw_y_offset = y - self.center_y

        # 应用低通滤波
        x_offset = self.low_pass_filter(raw_x_offset, self.last_x_offset)
        y_offset = self.low_pass_filter(raw_y_offset, self.last_y_offset)

        # 更新上一次的偏移值
        self.last_x_offset = x_offset
        self.last_y_offset = y_offset

        # 计算比率比值
        ratio_proportion = ratio / self.ratio_num if ratio > 0 else 0

        # 设定比率阈值，当达到这个阈值时认为已经足够接近目标
        target_ratio_threshold = 0.9

        # 如果比率比值小于阈值，说明还远，速度应该更快
        if ratio_proportion < target_ratio_threshold:
            # 使用非线性映射，随着接近目标速度逐渐降低
            # 使用指数函数实现平滑过渡
            speed_factor = 1.0 - (ratio_proportion / target_ratio_threshold)
            speed = self.min_speed + (self.max_speed - self.min_speed) * (
                speed_factor**2
            )
        else:
            # 已经非常接近目标，使用最小速度或停止
            speed = 0 if ratio_proportion > 0.95 else self.min_speed

        # 确保速度在合理范围内
        speed = max(self.min_speed, min(speed, self.max_speed))
        # 打印调试信息
        if self.debug_mode:
            print(
                f"目标位置：({x}, {y}), 偏移：({x_offset}, {y_offset}), "
                f"目标比率：{self.ratio_num:.4f}, 当前比率：{ratio:.4f}, "
                f"比率比值：{ratio_proportion:.4f}, 速度：{speed:.2f}"
            )

        # 根据偏移控制移动
        if abs(x_offset) > 50:  # 如果水平偏移较大
            # 计算转向速度系数，偏移越大速度越快
            turn_speed_factor = min(abs(x_offset) / 200, 1.0)  # 将偏移量映射到 0-1 范围
            
            # 基础转向速度
            base_turn_speed = int(speed * 5)
            
            # 根据偏移量大小计算实际转向速度
            turn_speed = base_turn_speed + int(base_turn_speed * turn_speed_factor)
            
            # 限制最大转向速度
            max_turn_speed = 100
            turn_speed = min(turn_speed, max_turn_speed)
            
            if self.debug_mode:
                print(f"水平偏移：{x_offset:.1f}, 转向速度：{turn_speed}")
                
            if x_offset > 0:
                return turn_left(node, turn_speed)  # 动态调整左转速度
            else:
                return turn_right(node, turn_speed)  # 动态调整右转速度
        elif ratio_proportion > 0.95:  # 如果已经非常接近目标
            return stop(node)  # 停止
        elif y_offset > 50:  # 如果目标在下方
            return back(node, int(speed))
        elif y_offset < -50:  # 如果目标在上方
            return advance(node, int(speed))
        else:
            return stop(node)

    def run(self, node):
        for event in node:
            if event["type"] == "INPUT":
                event_id = event["id"]
                if event_id == "data":
                    self.process_image(Calculate.from_pa_array(event["value"]))
                elif event_id == "state":
                    state = event["value"][0].as_py()
                    match state:
                        case "IDLE":
                            self.arm_state_Ready = True
                        case "MOVING":
                            self.arm_state_Ready = False
                        case "ESTOP":
                            self.arm_state_Ready = False


if __name__ == "__main__":
    node = Node()
    car_cv = CarCV()
    car_cv.run(node)
