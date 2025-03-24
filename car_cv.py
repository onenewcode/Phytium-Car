from dora import Node
import numpy as np
import cv2
from move import Move
from direcition import ColorDetector

def main():
    node = Node()
    move = Move(node)
    # 网球颜色阈值范围（HSV）- 黄绿色
    lower_tennis = [20, 70, 80]  # 降低饱和度和亮度的最低要求
    upper_tennis = [50, 255, 255]  # 扩大色调范围
    # 初始化检测器
    detector = ColorDetector(lower_tennis, upper_tennis, min_area=300)
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
                if image is not None:
                    # 把图像分成三块,识别中心点在中心，直走
                    processed_frame, centers, mask = detector.process(image)
                    if len(centers)==0:
                        move.stop()
                    else:
                        (horizontal,vertical)=centers[0]
                        if horizontal<width/3:
                            move.advance_left()
                        elif horizontal<2*width/3:
                            move.advance()
                        else:
                            move.advance_right()
                    # TODO  显示结果 用于测试
                    # cv2.imshow('网球检测结果', processed_frame)
                    # cv2.waitKey(1)
                    # cv2.imshow('掩膜', mask)
if __name__ == "__main__":
    main()

