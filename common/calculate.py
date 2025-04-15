

class Calculate:
    """
    用于存储和处理目标检测结果的数据类
    
    属性:
        x (int): 目标在图像中的 x 坐标
        y (int): 目标在图像中的 y 坐标
        ratio (float): 目标在图像中所占的比例
    """
    def __init__(self, x, y, ratio):
        """
        初始化 Calculate 对象
        
        参数:
            x (int): 目标在图像中的 x 坐标
            y (int): 目标在图像中的 y 坐标
            ratio (float): 目标在图像中所占的比例
        """
        self.x = x
        self.y = y
        self.ratio = ratio

    @staticmethod
    def to_pa_array(calc_list):
        """将 Calculate 对象列表转换为 pyarrow 数组"""
        data = [(c.x, c.y, c.ratio) for c in calc_list]
        return pa.array(
            data,
            type=pa.struct(
                [
                    pa.field("x", pa.int64()),
                    pa.field("y", pa.int64()),
                    pa.field("ratio", pa.float64()),
                ]
            ),
        )

    @staticmethod
    def from_pa_array(pa_array):
        """将 pyarrow 数组转换回 Calculate 对象列表"""
        return [
            Calculate(item["x"].as_py(), item["y"].as_py(), item["ratio"].as_py())
            for item in pa_array
        ]
