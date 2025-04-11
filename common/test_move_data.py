import unittest
import pyarrow as pa
from move_data import MoveData


class TestMoveData(unittest.TestCase):
    def setUp(self):
        # 测试数据初始化
        self.direct = 1
        self.speed = 100
        self.move_data = MoveData(self.direct, self.speed)

    def test_init(self):
        """测试初始化"""
        self.assertEqual(self.move_data.direct, self.direct)
        self.assertEqual(self.move_data.speed, self.speed)

    def test_to_arrow_array(self):
        """测试转换为 pyarrow Array"""
        array = self.move_data.to_arrow_array()
        self.assertIsInstance(array, pa.Array)
        data_list = array.to_pylist()
        self.assertEqual(data_list, [self.direct, self.speed])

    def test_from_arrow_array(self):
        """测试从 pyarrow Array 创建对象"""
        array = pa.array([self.direct, self.speed])
        move_data = MoveData.from_arrow_array(array)
        self.assertEqual(move_data.direct, self.direct)
        self.assertEqual(move_data.speed, self.speed)

    def test_multiple_arrays(self):
        """测试批量转换"""
        # 创建多个测试对象
        move_data_list = [MoveData(1, 100), MoveData(2, 200), MoveData(0, 0)]

        # 测试转换为数组列表
        arrays = MoveData.to_arrow_arrays(move_data_list)
        self.assertEqual(len(arrays), 3)
        for array in arrays:
            self.assertIsInstance(array, pa.Array)

        # 测试从数组列表转换回对象
        new_move_data_list = MoveData.from_arrow_arrays(arrays)
        self.assertEqual(len(new_move_data_list), 3)
        for original, new in zip(move_data_list, new_move_data_list):
            self.assertEqual(original.direct, new.direct)
            self.assertEqual(original.speed, new.speed)


if __name__ == "__main__":
    unittest.main()
