import os
import sys
from dora import Node
import cv2
import numpy as np

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 现在可以正常导入
from untils.untils import translate_image


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
                image = translate_image(event["value"], event["metadata"])
                if image is not None:
                    latest_image = image
            elif event_id == "mask":
                mask = translate_image(event["value"], event["metadata"])
                if mask is not None:
                    latest_mask = mask

            # 显示图像
            display_images(latest_image, latest_mask)


if __name__ == "__main__":
    main()
