from ultralytics import YOLO
import cv2
import numpy as np
import torch
from dora import Node
import pyarrow as pa
class YOLODetector:
    def __init__(self, model_path,area_ratio=0.1):
        self.model = YOLO(model_path)
        # 用于判断是否停车
        self.area_ratio=area_ratio
    def process(self,frame):
        """
        检测图像中的网球，返回最大网球的中心点、面积比例和处理后的图像

        参数:
            image_path: 图像路径

        返回:
            center: 最大网球的中心点坐标 (x, y)
            area_ratio: 最大网球占整幅图像的面积比例
            result_image: 处理后的图像，包含检测框和中心点标记
        """
        # 获取图像尺寸
        img_height, img_width = frame.shape[:2]
        img_area = img_height * img_width

        # 使用 YOLO 进行检测
        results =self.model.predict(frame,stream=True,conf=0.1,half=True,max_det=50)

        # 创建结果图像的副本
        result_image = frame

        # 初始化返回值
        center = None
        area_ratio = 0
        max_area = 0
        # 处理检测结果
        for result in results:
            boxes = result.boxes  # Boxes object for bounding box outputs
            masks = result.masks  # Masks object for segmentation masks outputs
            # keypoints = result.keypoints  # Keypoints object for pose outputs
            probs = result.probs  # Probs object for classification outputs
            # obb = result.obb  # Oriented boxes object for OBB outputs
            result.show()
            # 遍历所有检测到的物体
            for box in boxes:
                # 获取类别
                cls = int(box.cls[0])
                cls_name = self.model.names[cls]
                print(cls_name)
        #         # 只关注网球类别 (sports ball 或 tennis ball)
        #         if cls_name in ['sports ball', 'tennis ball'] or cls == 32:  # 32 是 COCO 数据集中 sports ball 的索引
        #             # 获取边界框坐标
        #             x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        #             x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

        #             # 计算面积
        #             area = (x2 - x1) * (y2 - y1)

        #             # 如果是最大的网球，更新信息
        #             if area > max_area:
        #                 max_area = area
        #                 area_ratio = area / img_area
        #                 center = ((x1 + x2) // 2, (y1 + y2) // 2)

        #                 # 在结果图像上绘制边界框和中心点
        #                 cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
        #                 cv2.circle(result_image, center, 5, (0, 0, 255), -1)
        #                 cv2.putText(result_image, f"Tennis Ball: {area_ratio:.4f}", (x1, y1 - 10),
        #                             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        # return center, area_ratio, result_image
def train():
    dector=YOLODetector('model/yolo11n.pt')
    dector.model.train(data="model/ball.yaml", epochs=10, imgsz=640)

def main():
    # 示例用法
    image_path = r"C:\Users\29071\Desktop\微信图片_20250326202538.jpg"# 替换为您的图像路径
    dector=YOLODetector(r'runs\detect\train4\weights\best.pt')
    frame=cv2.imread(image_path)
    dector.process(frame)
    
    # try:
    #     center, area_ratio, result_image = dector.process(image_path)
        
    #     if center is None:
    #         print("未检测到网球")
    #     else:
    #         print(f"最大网球的中心点坐标：{center}")
    #         print(f"最大网球占图像面积的比例：{area_ratio:.4f}")
            
    #         # 显示结果图像
    #         cv2.imshow("Tennis Ball Detection", result_image)
    #         cv2.waitKey(0)
    #         cv2.destroyAllWindows()
            
    #         # 保存结果图像
    #         cv2.imwrite("tennis_ball_detection_result.jpg", result_image)
            
    # except Exception as e:
    #     print(f"发生错误：{e}")

if __name__ == "__main__":
    main()