import cv2
import numpy as np
import time
from move import Move
from dora import Node
from ultralytics import YOLO

class TennisBallTracker:
    def __init__(self, node):
        """
        初始化网球跟踪器
        
        Args:
            node: Dora 节点对象
        """
        self.move = Move(node)
        # 加载 YOLOv11 模型
        self.model = YOLO('yolov11n.pt')
        # 设置置信度阈值
        self.conf_threshold = 0.5
        
        # 图像中心点坐标
        self.center_x = None
        self.center_y = None
        
        # PID 控制参数
        self.kp = 0.05  # 比例系数
        self.last_error = 0
        self.kd = 0.02  # 微分系数
        
        # 跟踪状态
        self.tracking = False
        self.lost_count = 0
        self.max_lost_count = 10  # 最大丢失帧数
        
    def detect_tennis_ball(self, frame):
        """
        检测图像中的网球
        
        Args:
            frame: 输入的图像帧
            
        Returns:
            检测到的网球边界框 (x1, y1, x2, y2, confidence)，如果没有检测到则返回 None
        """
        # 使用 ultralytics 进行推理
        results = self.model(frame, classes=[32], conf=self.conf_threshold)  # 32是网球类别ID
        
        # 筛选出网球检测结果
        tennis_balls = []
        
        if len(results) > 0 and len(results[0].boxes) > 0:
            for box in results[0].boxes:
                # 获取边界框坐标和置信度
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = box.conf[0].item()
                tennis_balls.append((x1, y1, x2, y2, conf))
        
        # 如果检测到多个网球，选择置信度最高的一个
        if tennis_balls:
            return max(tennis_balls, key=lambda x: x[4])
        
        return None
    
    def track_tennis_ball(self, frame):
        """
        跟踪图像中的网球并控制移动
        
        Args:
            frame: 输入的图像帧
        """
        # 获取图像尺寸
        height, width = frame.shape[:2]
        self.center_x = width // 2
        self.center_y = height // 2
        
        # 检测网球
        ball = self.detect_tennis_ball(frame)
        
        if ball is not None:
            x1, y1, x2, y2, conf = ball
            
            # 计算网球中心点
            ball_center_x = (x1 + x2) / 2
            ball_center_y = (y1 + y2) / 2
            
            # 在图像上绘制检测结果
            cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.circle(frame, (int(ball_center_x), int(ball_center_y)), 5, (0, 0, 255), -1)
            cv2.putText(frame, f"Tennis Ball: {conf:.2f}", (int(x1), int(y1) - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # 计算网球中心与图像中心的偏差
            error_x = ball_center_x - self.center_x
            
            # 计算 PID 控制输出
            derivative = error_x - self.last_error
            control_signal = self.kp * error_x + self.kd * derivative
            self.last_error = error_x
            
            # 根据网球位置控制移动
            self.control_movement(ball_center_x, ball_center_y, width, height)
            
            # 重置丢失计数
            self.lost_count = 0
            self.tracking = True
            
        else:
            # 网球丢失，增加丢失计数
            if self.tracking:
                self.lost_count += 1
                
                # 如果连续多帧未检测到网球，停止跟踪
                if self.lost_count > self.max_lost_count:
                    self.move.stop()
                    self.tracking = False
                    print("网球丢失，停止跟踪")
        
        # 显示跟踪状态
        status = "跟踪中" if self.tracking else "未检测到网球"
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        return frame
    
    def control_movement(self, ball_x, ball_y, frame_width, frame_height):
        """
        根据网球位置控制移动
        
        Args:
            ball_x: 网球中心 x 坐标
            ball_y: 网球中心 y 坐标
            frame_width: 图像宽度
            frame_height: 图像高度
        """
        # 定义区域阈值
        left_threshold = frame_width * 0.4
        right_threshold = frame_width * 0.6
        top_threshold = frame_height * 0.4
        bottom_threshold = frame_height * 0.6
        
        # 计算网球大小（用于判断距离）
        ball_size = (ball_x - ball_y) / frame_width
        
        # 根据网球位置决定移动方向
        if ball_x < left_threshold:
            if ball_y < top_threshold:
                # 左上
                self.move.advance_left()
                print("向左上方移动")
            elif ball_y > bottom_threshold:
                # 左下
                self.move.back_left()
                print("向左下方移动")
            else:
                # 左
                self.move.turn_left()
                print("向左转向")
        elif ball_x > right_threshold:
            if ball_y < top_threshold:
                # 右上
                self.move.advance_right()
                print("向右上方移动")
            elif ball_y > bottom_threshold:
                # 右下
                self.move.back_right()
                print("向右下方移动")
            else:
                # 右
                self.move.turn_right()
                print("向右转向")
        else:
            if ball_y < top_threshold:
                # 上
                self.move.advance()
                print("向前移动")
            elif ball_y > bottom_threshold:
                # 下
                self.move.Back()
                print("向后移动")
            else:
                # 中心区域，保持静止
                self.move.stop()
                print("目标在中心区域，保持静止")

class TennisBallTrackerNode(Node):
    def __init__(self):
        super().__init__()
        self.tracker = TennisBallTracker(self)
        self.cap = None
    
    def setup(self):
        # 初始化摄像头
        self.cap = cv2.VideoCapture(0)  # 使用默认摄像头
        if not self.cap.isOpened():
            print("无法打开摄像头")
            return False
        return True
    
    def process(self):
        if self.cap is None or not self.cap.isOpened():
            print("摄像头未初始化")
            return
            
        # 读取一帧图像
        ret, frame = self.cap.read()
        if not ret:
            print("无法获取图像帧")
            return
            
        # 跟踪网球
        processed_frame = self.tracker.track_tennis_ball(frame)
        
        # 显示处理后的图像
        cv2.imshow("Tennis Ball Tracker", processed_frame)
        
        # 按 ESC 键退出
        if cv2.waitKey(1) == 27:
            self.cleanup()
    
    def cleanup(self):
        if self.cap is not None:
            self.cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    # 创建并运行节点
    node = TennisBallTrackerNode()
    if node.setup():
        try:
            while True:
                node.process()
        except KeyboardInterrupt:
            print("程序被用户中断")
        finally:
            node.cleanup()