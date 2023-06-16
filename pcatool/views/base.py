from pcatool.commonlibs import \
    Tuple

class BaseView(object):
    def __init__(self, start_x: int, start_y: int, width: int, height: int):
        self.x = start_x
        self.y = start_y
        self.w = width
        self.h = height

    def point_in_view(self, point: Tuple[int, int]):
        x, y = point
        return self.x <= x < self.x + self.w \
            and self.y <= y < self.y + self.h