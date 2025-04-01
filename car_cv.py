from dora import Node
import numpy as np
import cv2
from move import Move
from mycv import ColorDetector
from untils import translate_image
import time

class CarCV:
    def __init__(self):
        self.node = Node()
        self.move = Move(self.node)
        self.lower_tennis = [30, 70, 80]
        self.upper_tennis = [50, 255, 255]
        self.detector = ColorDetector(self.lower_tennis, self.upper_tennis, min_area=500)

        self.last_command = "stop"
        self.lost_count = 0
        self.max_lost_frames = 20
        self.search_direction = 1
        self.search_start_time = 0
        self.last_command_time = time.time()
        self.ratio_abs=0.001
        self.target_found = False
        self.last_valid_position = None
        self.debug_mode = False
        self.command_interval = 0.2
        self.recet_pos=(210, 354, 100, 100)
        self.center_h=248
        self.center_w= 402

    def process_image(self, image, width, height):
        processed_frame, mask, contours, centers, ratio = self.detector.process(image)
        current_command = "unknown"
        current_time = time.time()
        can_send_command = (current_time - self.last_command_time) >= self.command_interval
        if can_send_command:
            if len(centers) == 0:
                self.handle_target_lost(width, current_time)
            else:
                self.handle_target_found(centers, ratio, width, height, current_time)

        if self.debug_mode:
            self.show_debug_info(processed_frame, mask, width, height, current_command, self.target_found, self.last_valid_position)

    def handle_target_lost(self, width, current_time):
        self.lost_count += 1
        self.target_found = False

        if self.lost_count >= self.max_lost_frames:
            if not self.target_found:
                self.search_start_time = current_time
                self.search_direction = 1 if self.last_valid_position and self.last_valid_position[0] > width / 2 else -1
                print("进入搜索模式，方向：", "右" if self.search_direction > 0 else "左")

            search_time = current_time - self.search_start_time
            if search_time > 100:
                self.search_direction *= -1
                self.search_start_time = current_time
                print("切换搜索方向：", "右" if self.search_direction > 0 else "左")

            if self.search_direction > 0 and (int(current_time * 5) % 2) == 0:
                self.move.rotate_right()
                self.last_command_time = current_time
            elif (int(current_time * 5) % 2) == 0:
                self.move.rotate_left()
                self.last_command_time = current_time

    def handle_target_found(self, centers, ratio, width, height, current_time):
        self.lost_count = 0
        self.target_found = True
        
        c_center = centers[0]
        h, w = c_center

        # 计算当前中心点与目标中心点的水平距离
        rel_x = (w - self.center_w) / width

        print("目标比率", ratio)
        if abs(ratio - self.ratio_abs) < self.ratio_abs:
            self.move.stop()
            if self.last_command != "stop":
                self.move.stop()
                self.last_command = "stop"
                self.last_command_time = current_time
                print("目标已接近，停止")
        else:
            new_command = self.determine_command(rel_x)
            if new_command != self.last_command:
                self.execute_command(new_command)
                self.last_command = new_command
                self.last_command_time = current_time

    def determine_command(self, rel_x):
        # 根据水平距离决定移动方向
        if rel_x < -0.1:
            return "rotate_left"
        elif rel_x > 0.1:
            return "rotate_right"
        else:
            return "advance"

    def execute_command(self, command):
        if command == "rotate_left":
            self.move.rotate_left()
        elif command == "turn_left":
            self.move.turn_left()
        elif command == "advance_left":
            self.move.advance_left()
        elif command == "advance":
            self.move.advance()
        elif command == "advance_right":
            self.move.advance_right()
        elif command == "turn_right":
            self.move.turn_right()
        elif command == "rotate_right":
            self.move.rotate_right()

    def show_debug_info(self, processed_frame, mask, width, height, current_command, target_found, last_valid_position):
        cv2.line(processed_frame, (int(width*0.15), 0), (int(width*0.15), height), (0, 255, 0), 1)
        cv2.line(processed_frame, (int(width*0.3), 0), (int(width*0.3), height), (0, 255, 0), 1)
        cv2.line(processed_frame, (int(width*0.4), 0), (int(width*0.4), height), (0, 255, 0), 1)
        cv2.line(processed_frame, (int(width*0.6), 0), (int(width*0.6), height), (0, 255, 0), 1)
        cv2.line(processed_frame, (int(width*0.7), 0), (int(width*0.7), height), (0, 255, 0), 1)
        cv2.line(processed_frame, (int(width*0.85), 0), (int(width*0.85), height), (0, 255, 0), 1)

        cv2.putText(processed_frame, f"Command: {current_command}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        status_text = "Target: " + ("Found" if target_found else f"Lost ({self.lost_count})")
        cv2.putText(processed_frame, status_text, (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        if target_found and last_valid_position:
            h, v = last_valid_position
            rel_x = h / width
            cv2.putText(processed_frame, f"Pos: {rel_x:.2f}", (10, 90),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.drawMarker(processed_frame, (int(h), int(v)), (0, 0, 255),
                           markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)

        cv2.imshow("Tennis Ball Tracking", processed_frame)
        cv2.imshow("Mask", mask)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            return

    def run(self):
        for event in self.node:
            if event["type"] == "INPUT" and event["id"] == "image":
                image = translate_image((event["value"], event["metadata"]))
                if image is not None:
                    self.process_image(image, width, height)
                else:
                    print(f"处理出错")
                    self.move.stop()

        if self.debug_mode:
            cv2.destroyAllWindows()
        self.move.stop()

if __name__ == "__main__":
    car_cv = CarCV()
    car_cv.run()

