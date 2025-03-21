import cv2
import numpy as np


class ColorDetector:
    def __init__(self, lower_hsv, upper_hsv, min_area=500):
        """
        颜色识别器构造函数
        :param lower_hsv: HSV 颜色空间下限阈值 (list/tuple)
        :param upper_hsv: HSV 颜色空间上限阈值 (list/tuple)
        :param min_area: 最小识别区域面积（过滤噪声）
        """
        self.lower = np.array(lower_hsv)
        self.upper = np.array(upper_hsv)
        self.min_area = min_area
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    def set_threshold(self, lower_hsv, upper_hsv):
        """动态设置颜色阈值范围"""
        self.lower = np.array(lower_hsv)
        self.upper = np.array(upper_hsv)

    def process(self, frame):
        """
        处理图像帧的主方法
        :return: 处理后的图像，中心点坐标列表
        """
        # 预处理减少噪声和反光的影响
        # 高斯模糊
        blurred_img = cv2.GaussianBlur(img, (11, 11), 0)

        median_blur = cv2.medianBlur(blurred_img , 5)
        #  基于亮度的掩膜，之后亮度影响较大的时候可以使用
        # 转换为 HSV 颜色空间
        cv2.imshow("mask",median_blur)
        cv2.waitKey(0)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
       
       
        # 创建颜色掩膜
        mask = cv2.inRange(hsv, self.lower, self.upper)
        cv2.imshow("mask",hsv)
        cv2.waitKey(0)
        # 形态学操作（消除噪声）
        mask = cv2.erode(mask, self.kernel, iterations=1)
        mask = cv2.dilate(mask, self.kernel, iterations=2)
        
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        centers = []
        processed_frame = frame.copy()
        
        for cnt in contours:
            # 过滤小面积区域
            area = cv2.contourArea(cnt)
            if area > self.min_area:
                # 获取外接矩形
                x, y, w, h = cv2.boundingRect(cnt)
                
                # 计算中心坐标
                center_x = x + w // 2
                center_y = y + h // 2
                centers.append((center_x, center_y))
                
                # 绘制矩形框和中心点
                cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.circle(processed_frame, (center_x, center_y), 5, (0, 0, 255), -1)
        
        return processed_frame, centers

# 使用示例
if __name__ == "__main__":
    # 黑色阈值范围（HSV）
    lower_black = [0, 0, 0]      # 最低阈值
    upper_black = [179, 50, 50]  # 最高阈值
    
    # 初始化检测器
    detector = ColorDetector(lower_black, upper_black)
    img=cv2.imread(r"C:\Users\29071\Desktop\90.jpg")
    processed_frame, centers = detector.process(img)
    # 显示结果
    cv2.imshow('Color Detection', processed_frame)
    