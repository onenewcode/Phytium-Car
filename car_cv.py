from dora import Node
import cv2
from traitlets import List
from move import Move
from mycv import ColorDetector
import time
from untils import Calculate


class CarCV:

    def __init__(self):
        self.node = Node()
        self.move = Move(self.node)
        self.lower_tennis = [30, 70, 80]
        self.upper_tennis = [50, 255, 255]
        self.detector = ColorDetector(
            self.lower_tennis, self.upper_tennis, min_area=300
        )

        self.last_command = "stop"
        self.lost_count = 0
        self.max_lost_frames = 20
        self.search_direction = 1
        self.search_start_time = 0
        self.last_command_time = time.time()
        self.target_found = False
        self.last_valid_position = None
        self.debug_mode = False
        self.recet_pos = (210, 354, 100, 100)
        self.center_x = 248
        self.center_y = 402
        self.width = 640
        self.height = 480
        self.arm_state_Ready = True
        self.ratio_abs = 0.01
        self.ratio_num = 0.03485026041666667

    def process_image(self, data: List[Calculate]):

        current_time = time.time()

        if  self.arm_state_Ready:
            if len(data) == 0:
                self.handle_target_lost(current_time)
            else:
                self.handle_target_found(
                    data[0].x, data[0].y, data[0].ratio, current_time
                )

    def handle_target_lost(self, current_time):
        self.lost_count += 1
        self.target_found = False

        if self.lost_count >= self.max_lost_frames:
            if not self.target_found:
                self.search_start_time = current_time
                self.search_direction = (
                    1
                    if self.last_valid_position
                    and self.last_valid_position[0] > self.width / 2
                    else -1
                )
                print(
                    "进入搜索模式，方向：", "右" if self.search_direction > 0 else "左"
                )

            search_time = current_time - self.search_start_time
            if search_time > 100:
                self.search_direction *= -1
                self.search_start_time = current_time
                print("切换搜索方向：", "右" if self.search_direction > 0 else "左")

            if self.search_direction > 0 :
                self.move.turn_right()
                self.last_command_time = current_time
            else:
                self.move.turn_left()
                self.last_command_time = current_time

    def handle_target_found(self, x, y, ratio, current_time):
        self.lost_count = 0
        self.target_found = True
        self.last_valid_position = (x, y)
        self.last_command_time = current_time
        # 计算小球与画面中心的偏移
        x_offset = x - self.center_x
        y_offset = y - self.center_y

        ratio_diff = abs(ratio - self.ratio_num)
        # 打印调试信息
        if self.debug_mode:
            print(
                f"目标位置：({x}, {y}), 偏移：({x_offset}, {y_offset}), 比率：{ratio}, 比率偏差：{ratio_diff}"
            )
        # 当比率偏差小于 0.1 时，小车停下
        if ratio_diff < self.ratio_abs:
            self.move.stop()
            return
        # 根据目标位置控制小车移动
        if abs(x_offset) > 50:  # 如果水平偏移较大
            if x_offset > 0:
                self.move.turn_left()
            else:
                self.move.turn_right()
        elif y_offset > 50:  # 如果目标在下方
            self.move.Back()
        elif y_offset < -50:  # 如果目标在上方
            self.move.advance()
        else:
            # 如果位置接近中心但比率不对，调整前后位置
            if ratio < self.ratio_abs:
                self.move.advance()
            else:
                self.move.Back()

    def run(self):
        for event in self.node:
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
    car_cv = CarCV()
    car_cv.run()
