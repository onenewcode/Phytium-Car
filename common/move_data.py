import pyarrow as pa
from typing import List


class MoveData:
    def __init__(self, direction: int, speed: int):
        self.direction = direction
        self.speed = speed

    @classmethod
    def from_arrow_array(cls, array: pa.Array) -> "MoveData":
        data_list = array.to_pylist()
        return cls(direct=data_list[0], speed=data_list[1])

    def to_arrow_array(self) -> pa.Array:
        """将 MoveData 对象转换为 pyarrow Array

        Returns:
            pa.Array: 包含 [move_type, move_data] 的 pyarrow Array
        """
        return pa.array([self.direction, self.speed])

    @classmethod
    def from_arrow_arrays(cls, arrays: List[pa.Array]) -> List["MoveData"]:
        """从多个 pyarrow Array 创建 MoveData 对象列表

        Args:
            arrays: pyarrow Array 列表

        Returns:
            List[MoveData]: MoveData 对象列表
        """
        return [cls.from_arrow_array(array) for array in arrays]

    @staticmethod
    def to_arrow_arrays(move_data_list: List["MoveData"]) -> List[pa.Array]:
        """将多个 MoveData 对象转换为 pyarrow Array 列表

        Args:
            move_data_list: MoveData 对象列表

        Returns:
            List[pa.Array]: pyarrow Array 列表
        """
        return [move_data.to_arrow_array() for move_data in move_data_list]
