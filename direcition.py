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
        self.contours=[]
        self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    
    def set_threshold(self, lower_hsv, upper_hsv):
        """动态设置颜色阈值范围"""
        self.lower = np.array(lower_hsv)
        self.upper = np.array(upper_hsv)

    def process(self, frame):
        """处理图像帧以识别单个网球。
        
        该方法对输入图像进行预处理、颜色阈值分割和轮廓检测，以识别单个网球。
        当检测到多个符合条件的轮廓时，会选择面积最大的一个作为网球。
        
        Args:
            frame: 输入的图像帧，BGR格式的numpy数组。
            
        Returns:
            tuple: 包含三个元素:
                - processed_frame: 处理后的图像，带有标记的网球位置。
                - centers: 网球中心点坐标列表，格式为[(x, y)]。
                - mask: 二值化掩膜图像。
                
        Raises:
            None
        """
        # 预处理 - 高斯模糊减少噪声
        blurred_img = cv2.GaussianBlur(frame, (5, 5), 0)
        
        # 中值滤波进一步减少噪声
        median_blur = cv2.medianBlur(blurred_img, 5)

        # 转换为 HSV 颜色空间
        hsv = cv2.cvtColor(median_blur, cv2.COLOR_BGR2HSV)
       
        # 创建颜色掩膜
        mask = cv2.inRange(hsv, self.lower, self.upper)
        
        # 形态学操作（消除噪声）
        mask = cv2.erode(mask, self.kernel, iterations=1)
        mask = cv2.dilate(mask, self.kernel, iterations=2)
        
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        centers = []
        processed_frame = frame.copy()
        
        # 如果有多个轮廓，只选择面积最大的一个（假设是网球）
        if contours:
            
            # 按面积排序轮廓
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            self.contours=contours
            # 只处理面积最大的轮廓
            cnt = contours[0]
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
                
                # 在图像上显示中心点坐标
                cv2.putText(processed_frame, f"网球: ({center_x}, {center_y})", 
                           (center_x - 60, center_y - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # 显示面积信息
                cv2.putText(processed_frame, f"面积: {int(area)}", 
                           (center_x - 60, center_y + 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return processed_frame, centers, mask

# 使用示例
if __name__ == "__main__":
    # 网球颜色阈值范围（HSV）- 黄绿色
    lower_tennis = [20, 70, 80]  # 降低饱和度和亮度的最低要求
    upper_tennis = [50, 255, 255]  # 扩大色调范围
    
    
    # 初始化检测器
    detector = ColorDetector(lower_tennis, upper_tennis, min_area=300)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("无法打开摄像头")
        exit()
        
    while True:
        ret, frame = cap.read()
        if not ret:
            print("无法获取画面")
            break
            
        processed_frame, centers, mask = detector.process(frame)
        
        # 显示结果
        cv2.imshow('网球检测结果', processed_frame)
        cv2.imshow('掩膜', mask)
        
        # 按ESC键退出
        if cv2.waitKey(1) == 27:
            break
            
    cap.release()
    cv2.destroyAllWindows()
