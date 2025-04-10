from dora import Node
import cv2
from traitlets import List
from common.move_data import MoveData
from move import Move
from mycv import ColorDetector
import time
from untils import Calculate
from simple_pid import PID
def send(node:Node, direction,speed)->MoveData:
        """
        发送运动数据给其他节点
        Args:
            direction (int): 运动的方向。

        Returns:
            bool: 是否发送成功。

        Raises:
            ZeroDivisionError: 如果除数为零，则抛出异常。
        """
        data=MoveData(direction,speed).to_arrow_array()
        if node!=None:
             node.send_output("move", data)
        return data
        
def stop(node:Node)->MoveData:
        return send(node,0,0)


def advance(node:Node,speed=2)->MoveData:
        return send(node,1,speed)


def back(node:Node,speed=2)->MoveData:
        return send(node,2,speed)


def turn_left(node:Node,speed=50)->MoveData:
        return send(node,5,speed)


def turn_right(node:Node,speed=50)->MoveData:
        return send(node,6,speed)
class CarCV:

    def __init__(self):
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
        
        # 添加低通滤波器参数
        self.alpha = 0.2  # 平滑因子 (0-1)
        self.last_x_offset = 0
        self.last_y_offset = 0
        
        # 修改PID控制器参数
        self.speed_pid = PID(Kp=0.5, Ki=0.1, Kd=0.05, setpoint=1.0)
        self.speed_pid.output_limits = (2, 100)  # 速度范围限制
        
        # 添加比率阈值参数
        self.ratio_threshold = 0.7  # 当比率比值小于此阈值时使用最大速度

    def process_image(self, data: List[Calculate],node=None)->MoveData:

        current_time = time.time()

        if  self.arm_state_Ready:
            if len(data) == 0:
                return self.handle_target_lost(current_time,node)
            else:
                return self.handle_target_found(
                    data[0].x, data[0].y, data[0].ratio, current_time,node
                )

    def handle_target_lost(self, current_time,node)->MoveData:
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
                self.last_command_time = current_time
                return  turn_right(node)
            else:
                self.last_command_time = current_time
                return turn_left(node)
                

    def low_pass_filter(self, new_value, last_value):
        """低通滤波器"""
        return self.alpha * new_value + (1 - self.alpha) * last_value

    def handle_target_found(self, x, y, ratio, current_time, node)->MoveData:
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
        
        # 计算比率比值并根据阈值决定速度
        ratio_proportion = ratio / self.ratio_num if ratio > 0 else 0
        
        # 当比率比值小于阈值时，使用最大速度
        if ratio_proportion < self.ratio_threshold:
            speed = 100  # 使用最大速度
        else:
            # 否则使用PID控制器计算速度
            speed = int(self.speed_pid(ratio_proportion))
        
        # 打印调试信息
        if self.debug_mode:
            print(f"目标位置：({x}, {y}), 偏移：({x_offset}, {y_offset}), "
                  f"目标比率：{self.ratio_num:.4f}, 当前比率：{ratio:.4f}, "
                  f"比率比值：{ratio_proportion:.4f}, 速度：{speed}")
        
        # 根据偏移控制移动
        if abs(x_offset) > 50:  # 如果水平偏移较大
            if x_offset > 0:
               return turn_left(node,speed)
            else:
                return turn_right(node,speed)
        elif y_offset > 50:  # 如果目标在下方
            return back(node,speed)
        elif y_offset < -50:  # 如果目标在上方
            return advance(node,speed)
        else:
            return stop(node)

    def run(self,node):
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
