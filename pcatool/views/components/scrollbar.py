from pcatool.commonlibs import pygame, Tuple, Optional


class ScrollBar:
    def __init__(self,
                 pos: Tuple[int, int],
                 size: Tuple[int, int],
                 bar_height: int,
                 bg_color='white',
                 bar_color='gray',
                 border_radius: int = 8):
        self._pos = pos
        self._size = size
        self.default_bg_color = bg_color
        self.bg_color = bg_color
        self.bar_color = bar_color
        self.border_radius = border_radius
        self.rect_width = 0
        self.t_x = 0
        self.t_y = self._pos[1] + self.size[1] // 2
        self._bar_pos = self._pos
        self._bar_height = bar_height
        self.rect = pygame.Rect(self._pos, self.size)
        self.bar_rect = pygame.Rect(self._pos, (self.size[0], bar_height))
        self._update()
        self.selected = False

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, new_size: Tuple[int, int]):
        self._size = new_size
        self._update()

    @property
    def bar_pos(self):
        return self._bar_pos

    @bar_pos.setter
    def bar_pos(self, new_pos: Tuple[int, int]):
        self._bar_pos = new_pos
        self._update()

    @property
    def bar_height(self):
        return self._bar_height

    @bar_height.setter
    def bar_height(self, new_height: int):
        self._bar_height = new_height
        self._update()

    def update(self, new_y: int):
        self.bar_pos = self.bar_pos[0], new_y
        self._update()

    def _update(self):
        self.bar_rect.update(self.bar_pos, (self.size[0], self.bar_height))
        self.rect.update(self._pos, self.size)

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        pygame.draw.rect(surface, self.bar_color, self.bar_rect,
                            border_radius=self.border_radius)