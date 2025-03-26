from dora import Node
import numpy as np
import cv2
from move import Move
from direcition import ColorDetector
import time

def main():
    node = Node()
    move = Move(node)
    # 网球颜色阈值范围（HSV）- 黄绿色，缩小检测范围以提高精度
    lower_tennis = [25, 100, 100]  # 提高色调下限和饱和度、亮度的最低要求
    upper_tennis = [45, 255, 255]  # 降低色调上限，保持饱和度和亮度范围
    # 初始化检测器
    detector = ColorDetector(lower_tennis, upper_tennis, min_area=300)
    
    # 添加状态变量
    last_command = "stop"
    lost_count = 0
    max_lost_frames = 15  # 连续丢失目标的最大帧数
    search_mode = False   # 搜索模式标志
    search_direction = 1  # 搜索方向 (1: 右，-1: 左)
    search_start_time = 0 # 搜索开始时间
    last_command_time = time.time()  # 上次发送命令的时间
    
    # 目标跟踪状态
    target_found = False
    last_valid_position = None
    
    # 添加调试窗口
    debug_mode = False  # 设置为 False 可关闭图像显示
    
    # 历史位置记录，用于平滑处理
    position_history = []
    max_area_history = 8
    max_history = 5
    
    # 控制参数
    command_interval = 0.2  # 命令发送间隔（秒）
    # 网球占据画面比率
    ratio=0.05
    
    for event in node:
        if event["type"] == "INPUT":
            event_id = event["id"]
            if event_id == "image":
                try:
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
                        height, width = image.shape[:2]
                    
                    if image is not None:
                        # 处理图像，检测网球
                        processed_frame, centers, mask = detector.process(image)
                        
                        # 当前控制命令
                        current_command = "unknown"
                        current_time = time.time()
                        
                        # 检查是否可以发送新命令
                        can_send_command = (current_time - last_command_time) >= command_interval
                        
                        if len(centers) == 0:
                            # 目标丢失处理
                            lost_count += 1
                            target_found = False
                            
                            if lost_count >= max_lost_frames and can_send_command:
                                if not search_mode:
                                    # 进入搜索模式
                                    search_mode = True
                                    search_start_time = current_time
                                    # 根据最后有效位置决定搜索方向
                                    if last_valid_position and last_valid_position[0] > width / 2:
                                        search_direction = 1  # 向右搜索
                                    else:
                                        search_direction = -1  # 向左搜索
                                    print("进入搜索模式，方向：", "右" if search_direction > 0 else "左")
                                
                                # 执行搜索模式
                                search_time = current_time - search_start_time
                                if search_time > 100:  # 搜索超过 10 秒
                                    # 切换搜索方向
                                    search_direction *= -1
                                    search_start_time = current_time
                                    print("切换搜索方向：", "右" if search_direction > 0 else "左")
                                
                                # 根据搜索方向旋转
                                if search_direction > 0:
                                    # 使用间歇性旋转来模拟慢速旋转
                                    if (int(current_time * 5) % 2) == 0:  # 每 0.4 秒旋转一次
                                        move.rotate_right()
                                        last_command_time = current_time
                                        current_command = "search_right"
                                else:
                                    if (int(current_time * 5) % 2) == 0:
                                        move.rotate_left()
                                        last_command_time = current_time
                                        current_command = "search_left"
                        else:
                            # 目标找到，退出搜索模式
                            search_mode = False
                            lost_count = 0
                            target_found = True
                            
                            # 获取最大面积的目标
                            current_area = 0
                            target_center = 0
                            
                            # 添加面积历史记录列表（如果不存在）
                            if not hasattr(main, 'area_history'):
                                main.area_history = []
                                
                            if len(centers) == 1:
                                contour_area = cv2.contourArea(detector.contours[0]) 
                                current_area = contour_area
                                target_center = centers[0]
                                
                                # 将当前面积添加到历史记录
                                main.area_history.append(current_area)
                                # 保持历史记录长度不超过5
                                if len(main.area_history) >max_area_history :
                                    main.area_history.pop(0)
                                    
                                # 计算加权平均面积（最近的面积权重更大）
                                weights = [0.05, 0.05, 0.1, 0.1, 0.15, 0.15, 0.2, 0.2]  # 权重和为1
                                # 增加历史记录最大长度
                                
                                # 保持历史记录长度不超过最大值
                                if len(main.area_history) > max_area_history:
                                    main.area_history.pop(0)
                                if len(main.area_history) > 0:
                                    # 根据实际历史长度裁剪权重
                                    actual_weights = weights[-len(main.area_history):]
                                    # 重新归一化权重
                                    actual_weights = [w/sum(actual_weights) for w in actual_weights]
                                    # 计算加权平均
                                    target_area = sum(a*w for a, w in zip(main.area_history, actual_weights))
                                else:
                                    target_area = current_area
                            else:
                                # 如果没有检测到目标，使用历史数据的衰减值
                                if hasattr(main, 'area_history') and len(main.area_history) > 0:
                                    target_area = main.area_history[-1] * 0.8  # 使用最后一次记录的80%
                                else:
                                    target_area = 0
                                    
                            # 更新最后有效位置
                            last_valid_position = target_center
                            
                            # 添加到历史记录
                            position_history.append(target_center)
                            if len(position_history) > max_history:
                                position_history.pop(0)
                            
                            # 计算平滑后的位置（使用最近几帧的平均位置）
                            if len(position_history) > 0:
                                smooth_center = np.mean(position_history, axis=0)
                                horizontal, vertical = smooth_center
                            else:
                                horizontal, vertical = target_center
                            
                            # 计算目标在图像中的相对位置 (0 到 1)
                            rel_x = horizontal / width
                            
                            # 计算目标面积比例，用于距离估计
                            area_ratio = target_area / (width * height)
                            
                            # 只有当可以发送新命令时才执行控制逻辑
                            if can_send_command:
                                print("目标比率",area_ratio)
                                # 根据面积比例判断是否需要停车
                                if area_ratio > ratio:  # 目标很近
                                    move.stop()
                                    if last_command != "stop":
                                        move.stop()
                                        last_command = "stop"
                                        last_command_time = current_time
                                        current_command = "stop_reached"
                                        print("目标已接近，停止")
                                else:
                                    # 根据目标位置划分更多区域，实现更精细的控制
                                    new_command = None
                                    
                                    if rel_x < 0.15:  # 极左
                                        new_command = "rotate_left"
                                        current_command = "rotate_left"
                                        print(f"目标在极左侧 ({rel_x:.2f})，左旋转")
                                    elif rel_x < 0.3:  # 左
                                        new_command = "turn_left"
                                        current_command = "turn_left"
                                        print(f"目标在左侧 ({rel_x:.2f})，左转")
                                    elif rel_x < 0.4:  # 中偏左
                                        new_command = "advance_left"
                                        current_command = "advance_left"
                                        print(f"目标在中偏左 ({rel_x:.2f})，左前")
                                    elif rel_x < 0.6:  # 中间
                                        new_command = "advance"
                                        current_command = "advance"
                                        print(f"目标在中间 ({rel_x:.2f})，直行")
                                    elif rel_x < 0.7:  # 中偏右
                                        new_command = "advance_right"
                                        current_command = "advance_right"
                                        print(f"目标在中偏右 ({rel_x:.2f})，右前")
                                    elif rel_x < 0.85:  # 右
                                        new_command = "turn_right"
                                        current_command = "turn_right"
                                        print(f"目标在右侧 ({rel_x:.2f})，右转")
                                    else:  # 极右
                                        new_command = "rotate_right"
                                        current_command = "rotate_right"
                                        print(f"目标在极右侧 ({rel_x:.2f})，右旋转")
                                    
                                    # 只有当命令变化时才发送
                                    if new_command != last_command:
                                        # 执行相应的命令
                                        if new_command == "rotate_left":
                                            move.rotate_left()
                                        elif new_command == "turn_left":
                                            move.turn_left()
                                        elif new_command == "advance_left":
                                            move.advance_left()
                                        elif new_command == "advance":
                                            move.advance()
                                        elif new_command == "advance_right":
                                            move.advance_right()
                                        elif new_command == "turn_right":
                                            move.turn_right()
                                        elif new_command == "rotate_right":
                                            move.rotate_right()
                                        
                                        last_command = new_command
                                        last_command_time = current_time
                        
                        # 显示调试信息
                        if debug_mode:
                            # 绘制区域分割线
                            cv2.line(processed_frame, (int(width*0.15), 0), (int(width*0.15), height), (0, 255, 0), 1)
                            cv2.line(processed_frame, (int(width*0.3), 0), (int(width*0.3), height), (0, 255, 0), 1)
                            cv2.line(processed_frame, (int(width*0.4), 0), (int(width*0.4), height), (0, 255, 0), 1)
                            cv2.line(processed_frame, (int(width*0.6), 0), (int(width*0.6), height), (0, 255, 0), 1)
                            cv2.line(processed_frame, (int(width*0.7), 0), (int(width*0.7), height), (0, 255, 0), 1)
                            cv2.line(processed_frame, (int(width*0.85), 0), (int(width*0.85), height), (0, 255, 0), 1)
                            
                            # 显示当前命令
                            cv2.putText(processed_frame, f"Command: {current_command}", (10, 30), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            
                            # 显示目标状态
                            status_text = "Target: " + ("Found" if target_found else f"Lost ({lost_count})")
                            cv2.putText(processed_frame, status_text, (10, 60), 
                                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                            
                            # 如果有目标，显示位置和面积信息
                            if target_found and last_valid_position:
                                h, v = last_valid_position
                                rel_x = h / width
                                cv2.putText(processed_frame, f"Pos: {rel_x:.2f}", (10, 90), 
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
                                
                                # 在目标中心画一个十字
                                cv2.drawMarker(processed_frame, (int(h), int(v)), (0, 0, 255), 
                                              markerType=cv2.MARKER_CROSS, markerSize=20, thickness=2)
                            
                            # 显示处理后的图像
                            cv2.imshow("Tennis Ball Tracking", processed_frame)
                            cv2.imshow("Mask", mask)
                            key = cv2.waitKey(1) & 0xFF
                            if key == 27:  # ESC 键退出
                                break
                
                except Exception as e:
                    print(f"处理出错：{e}")
                    move.stop()
    
    # 清理
    if debug_mode:
        cv2.destroyAllWindows()
    move.stop()

if __name__ == "__main__":
    main()

