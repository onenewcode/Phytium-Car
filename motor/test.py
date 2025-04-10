import cv2
import numpy as np
import time

# PID 控制器类
class PIDController:
    def __init__(self, Kp, Ki, Kd):
        self.Kp = Kp  # 比例系数
        self.Ki = Ki  # 积分系数
        self.Kd = Kd  # 微分系数
        self.previous_error = 0  # 上一次的误差
        self.integral = 0         # 积分累加值

    def compute(self, setpoint, measured_value, dt):
        """
        计算 PID 输出
        :param setpoint: 目标值
        :param measured_value: 当前测量值
        :param dt: 时间间隔（秒）
        :return: PID 输出值
        """
        error = setpoint - measured_value  # 计算误差
        self.integral += error * dt        # 累积误差
        derivative = (error - self.previous_error) / dt  # 计算误差变化率

        output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)

        self.previous_error = error  # 更新上一次的误差
        return output

# 初始化摄像头
cap = cv2.VideoCapture(0)

# 设置目标物体的颜色范围 (HSV 空间)
lower_color = np.array([30, 50, 50])  # 下界 (绿色为例)
upper_color = np.array([90, 255, 255])  # 上界

# 目标面积
target_area = 10000  # 目标物体的理想面积

# 初始化 PID 控制器
pid = PIDController(Kp=0.1, Ki=0.01, Kd=0.001)

# 小车速度控制函数 (伪代码)
def control_car(speed):
    if speed > 0:
        print(f"前进，速度: {speed:.2f}")
    elif speed == 0:
        print("停止")
    else:
        print(f"后退，速度: {speed:.2f}")

# 主循环
last_time = time.time()
while True:
    ret, frame = cap.read()
    if not ret:
        print("无法读取摄像头画面")
        break

    # 转换为 HSV 空间
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # 颜色阈值分割
    mask = cv2.inRange(hsv, lower_color, upper_color)

    # 查找轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    current_time = time.time()
    dt = current_time - last_time  # 计算时间间隔
    last_time = current_time

    if contours:
        # 找到最大的轮廓
        largest_contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(largest_contour)

        # 绘制轮廓
        x, y, w, h = cv2.boundingRect(largest_contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # 显示物体面积
        cv2.putText(frame, f"Area: {area}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # 使用 PID 控制器计算速度
        speed = pid.compute(target_area, area, dt)

        # 将速度限制在合理范围内
        speed = max(-100, min(100, speed))  # 限制速度在 [-100, 100] 之间

        # 控制小车
        control_car(speed)

    # 显示结果
    cv2.imshow("Frame", frame)
    cv2.imshow("Mask", mask)

    # 按下 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()