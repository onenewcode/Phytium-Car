
def translate_image(data, metadata):
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