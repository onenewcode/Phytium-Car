from common.move_data import MoveData
from untils import translate_direction


class ViewData:
    def __init__(self, data: MoveData):
        self.direction = translate_direction(data.direction)
        self.speed = data.speed
