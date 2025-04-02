import cv2

def count_cameras(max_checks=10):
    """
    检测系统中可用的摄像头数量。
    
    :param max_checks: 最大检查的摄像头索引数（默认为10）
    :return: 可用摄像头的数量
    """
    available_cameras = 0

    for index in range(max_checks):
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            # 如果摄像头成功打开，则计数加一
            available_cameras += 1
            cap.release()  # 释放摄像头资源
        else:
            # 如果摄像头无法打开，则停止检查
            break

    return available_cameras


if __name__ == "__main__":
    num_cameras = count_cameras()
    print(f"系统中检测到 {num_cameras} 个可用摄像头。")
 