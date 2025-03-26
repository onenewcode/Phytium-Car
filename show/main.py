from dora import Node
import cv2
import numpy as np

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

def display_images(image=None, mask=None, display_width=640, display_height=480):
    """显示图像，支持单图像或图像与掩码组合显示"""
    if image is None and mask is None:
        return
    
    # 准备显示图像
    if image is not None and mask is not None:
        # 调整两幅图像大小以匹配
        resized_image = cv2.resize(image, (display_width, display_height))
        resized_mask = cv2.resize(mask, (display_width, display_height))
        
        # 水平拼接两幅图像
        combined_image = np.hstack((resized_image, resized_mask))
        cv2.imshow("Images", combined_image)
    elif image is not None:
        resized_image = cv2.resize(image, (display_width, display_height))
        cv2.imshow("Images", resized_image)
    elif mask is not None:
        resized_mask = cv2.resize(mask, (display_width, display_height))
        cv2.imshow("Images", resized_mask)
    
    cv2.waitKey(1)

def main():
    node = Node()
    # 创建窗口
    cv2.namedWindow("Images", cv2.WINDOW_NORMAL)
    
    # 用于存储最新的图像
    latest_image = None
    latest_mask = None
    
    for event in node:
        if event["type"] == "INPUT":
            event_id = event["id"]
            
            # 处理普通图像或 mask 图像
            if event_id == "image":
                image = process_image(event["value"], event["metadata"])
                if image is not None:
                    latest_image = image
            elif event_id == "mask":
                mask = process_image(event["value"], event["metadata"])
                if mask is not None:
                    latest_mask = mask
            
            # 显示图像
            display_images(latest_image, latest_mask)

if __name__ == "__main__":
    main()
