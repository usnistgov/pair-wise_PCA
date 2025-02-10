import pandas as pd

from pcatool.commonlibs import pygame, Tuple, \
    Optional, Dict

class BarChart:
    def __init__(self,
                 data: pd.DataFrame,
                 pos: Tuple[int, int],
                 size: Tuple[int, int],
                 font_map: Dict[int, pygame.font.SysFont],
                 fontsize: int = 30,
                 bg_color=(0, 0, 0),
                 text_color=(255, 255, 255),
                 border_radius: int = 20):
        self._data = data
        self._data = data.sort_values(by=data.columns.tolist(),
                                      ascending=False)
        self._pos = pos
        self._size = size
        self.default_bg_color = bg_color
        self.bg_color = bg_color
        self.text_color = text_color
        self.border_radius = border_radius
        self.rect_width = 0
        self.t_x = 0
        self.t_y = self.pos[1] + self.size[1] // 2
        self.font = font_map[fontsize]

        self.rect = pygame.Rect(self.pos, self.size)
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
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, new_pos: Tuple[int, int]):
        self._pos = new_pos
        self._update()

    def update(self, diff: int):
        self.pos = (self.pos[0], self.pos[1] + diff)
        self._update()

    def _update(self):
        self.t_x = 0
        self.t_y = self.pos[1] + self.size[1] // 2
        self.rect.update(self.pos, self.size)

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)

        max_val = self._data.abs().max().item()
        x_center = self.pos[0] + self.size[0] // 2
        max_bar_w = self.size[0] // 2 - 10
        bar_height = ((self.size[1] - 20 - self._data.shape[0] * 10) // self._data.shape[0])
        bar_height = min(40, bar_height)
        bar_height = max(20, bar_height)
        for i, (idx, row) in enumerate(self._data.iterrows()):
            y = self.pos[1] + 20 + i * bar_height + i * 10
            x = x_center
            w = int((max_bar_w / max_val) * abs(row[0]))
            h = bar_height

            if row.iloc[0] > 0:
                bar_rect = pygame.Rect(x, y, w, h)
                pygame.draw.rect(surface, "green", bar_rect)
                text_surface = self.font.render(f'{idx}({round(row.iloc[0], 2)})',
                                                True, 'black')
                text_rect = text_surface.get_rect(center=(0, 0))
                text_rect.center = (x_center - text_rect.w//2 - 10, y + h // 2)
                surface.blit(text_surface, text_rect)
            elif row.iloc[0] <= 0:
                x = x_center - w
                bar_rect = pygame.Rect(x, y, w, h)
                pygame.draw.rect(surface, "red", bar_rect)
                text_surface = self.font.render(f'{idx}({round(row.iloc[0], 2)})',
                                                True, 'black')
                text_rect = text_surface.get_rect(center=(0, 0))
                text_rect.center = (x_center + text_rect.w//2 + 10, y + h // 2)
                surface.blit(text_surface, text_rect)

        if self.rect_width > 0:
            pygame.draw.rect(surface, "#3E7DE8", self.rect,
                             self.rect_width, border_radius=10)