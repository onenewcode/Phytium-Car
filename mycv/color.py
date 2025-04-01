import cv2
import numpy as np
from dora import Node
import pyarrow as pa

def process_image(data, metadata):
    """处理图像数据，支持不同编码格式"""
    # 转换为 NumPy 数组
    np_array = data.to_numpy()

    # 根据编码处理数据
    encoding = metadata["encoding"]
    if encoding in ["bgr8", "rgb8"]:
        # 原始像素格式
        height = metadata["height"]
        width = metadata["width"]
        image = np_array.reshape((height, width, 3))
        if encoding == "rgb8":
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    elif encoding in ["jpeg", "png"]:
        # 压缩格式，需要解码
        byte_data = np_array.tobytes()
        image = cv2.imdecode(np.frombuffer(byte_data, np.uint8), cv2.IMREAD_COLOR)
    else:
        return None
    
    return image
class ColorDetector:
    def __init__(self, lower_hsv, upper_hsv, ratio_value=0.0322265625,min_area=500):
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
        # 锁眼位置
        self.recet_pos=(210, 354, 100, 100)
        self.center=(320,240)
        self.h=480
        self.w=640
        self.ratio_value=ratio_value
    def set_threshold(self, lower_hsv, upper_hsv):
        """动态设置颜色阈值范围"""
        self.lower = np.array(lower_hsv)
        self.upper = np.array(upper_hsv)
    def ratio(self,h,w):
        """
        计算轮廓的长宽比
        :param height:
        :param width: 
        :return: 长宽比列表
        """
        return (h / self.h)* w / self.w
        
    def process(self, frame):
        """处理图像帧以识别单个网球。
        
        该方法对输入图像进行预处理、颜色阈值分割和轮廓检测，以识别单个网球。
        当检测到多个符合条件的轮廓时，会选择面积最大的一个作为网球。
        
        Args:
            frame: 输入的图像帧，BGR 格式的 numpy 数组。
            
        Returns:
            tuple: 包含三个元素:
                - processed_frame: 处理后的图像，带有标记的网球位置。
                - centers: 网球中心点坐标列表，格式为 [(x, y)]。
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
        # 定义结构元素（核），例如 5x5 的矩形
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1) 
        mask  = cv2.GaussianBlur(mask, (5, 5), 0)
        cv2.imshow('mask', mask)
        
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        centers = []
        processed_frame = frame.copy()
        ratio=0
        # 如果有多个轮廓，只选择面积最大的一个（假设是网球）
        if contours:
            # 按面积排序轮廓
            contours = sorted(contours, key=cv2.contourArea, reverse=True)
            # 只处理面积最大的轮廓
            cnt = contours[0]
            x, y, w, h = cv2.boundingRect(cnt)
            # 计算矩形的面积
            area = w*h
            if area > self.min_area:
                # 计算中心坐标
                center_x = x + w // 2
                center_y = y + h // 2
                centers.append((center_x, center_y))
                
                # 绘制矩形框和中心点
                cv2.rectangle(processed_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                cv2.circle(processed_frame, (center_x, center_y), 5, (0, 0, 255), -1)
                
                # 在图像上显示中心点坐标
                cv2.putText(processed_frame, f"网球：({center_x}, {center_y})", 
                           (center_x - 60, center_y - 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                
                # 显示面积信息
                cv2.putText(processed_frame, f"面积：{int(area)}", 
                           (center_x - 60, center_y + 20), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                # 显示长宽比信息
                ratio = self.ratio(h,w)
                print(centers)
        return processed_frame, mask,contours, centers,ratio
# 接受传入的图像，发送处理后的图像，轮廓，中心点，掩膜
def main():
    node = Node()
    dector=ColorDetector([20, 70, 80], [50, 255, 255], min_area=300)
    for event in node:
        if event["type"] == "INPUT":
            event_id = event["id"]
            # 处理普通图像或 mask 图像
            if event_id == "image":
                image = process_image(event["value"], event["metadata"])
                if image is not None:
                    image=cv2.flip(image, 0)
                    processed_frame, mask,contours, centers,_=dector.process(image)
                    node.send_output("image",event["value"],event["metadata"])
                    # node.send_output("mask", pa.array(mask.ravel()),event["metadata"])
                    # node.send_output("contours", contours)

def test():
    dector=ColorDetector([30, 70, 80], [50, 255, 255], min_area=300)

    # 打开默认摄像头（通常是设备上的第一个摄像头）
    cap = cv2.VideoCapture(0)
    # 图片形状 640*480
    if not cap.isOpened():
        print("无法打开摄像头")
        exit()

    while True:
        # 逐帧捕获
        ret, frame = cap.read()
        image=cv2.flip(frame, 0)
        processed_frame, mask,contours, centers,_=dector.process(image)
        # 如果正确读取帧，ret 为 True
        if not ret:
            print("无法读取摄像头画面")
            break

        # 显示当前帧
        cv2.imshow('Camera Feed', frame)
        cv2.imshow('processed_frame', processed_frame)
        # cv2.imshow('mask', mask)

        # 按下键盘上的 'q' 键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 释放摄像头资源
    cap.release()
    # 关闭所有 OpenCV 窗口
    cv2.destroyAllWindows()

# 使用示例
if __name__ == "__main__":
    test()