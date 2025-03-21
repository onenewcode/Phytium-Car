from dora import Node
import cv2
class ColorDetector:
    def __init__(self, lower_color, upper_color):
        """
        初始化颜色检测器
        :param lower_color: HSV 颜色空间下限值（numpy 数组）
        :param upper_color: HSV 颜色空间上限值（numpy 数组）
        """
        self.lower = lower_color
        self.upper = upper_color
        # 形态学操作核，之后可能采用更复杂的方法经行降噪处理
        self.kernel = np.ones((5, 5), np.uint8) 

    def process(self, frame):
        """
        处理当前帧并返回结果
        :return: 
            processed_frame: 处理后的帧
            centers: 检测到的物体中心坐标列表
        """
        if frame is None:
            raise ValueError("未设置输入帧，请先调用 update_frame()")

        # 转换为 HSV 颜色空间
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # 创建颜色掩膜
        mask = cv2.inRange(hsv, self.lower, self.upper)
        
        # 形态学操作（降噪）
        mask = cv2.erode(mask, self.kernel, iterations=1)
        mask = cv2.dilate(mask, self.kernel, iterations=2)
        
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        processed_frame = frame.copy()
        centers = []
        
        for cnt in contours:
            # 过滤小面积区域
            if cv2.contourArea(cnt) < 500:
                continue
                
            # 绘制轮廓
            cv2.drawContours(processed_frame, [cnt], -1, (0, 255, 0), 2)
            
            # 计算中心坐标
            M = cv2.moments(cnt)
            if M["m00"] != 0:
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                centers.append((cX, cY))
                
                # 绘制中心点
                cv2.circle(processed_frame, (cX, cY), 5, (255, 0, 0), -1)
                cv2.putText(processed_frame, f"({cX}, {cY})", (cX + 10, cY - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
        
        return processed_frame, centers

def main():
    node = Node()

    for event in node:
        if event["type"] == "INPUT":
            event_id = event["id"]
            if event_id == "image":
                data = event["value"]
                metadata = event["metadata"]

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

                # 显示图像
                if image is not None:
                    cv2.imshow("Received Image", image)
                    cv2.waitKey(1)


if __name__ == "__main__":
    main()
