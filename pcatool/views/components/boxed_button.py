from pcatool.commonlibs import pygame, \
    Optional, Tuple, Dict
from pcatool.views import BaseView
from pcatool.views.components import NewButton


class BoxedButton(BaseView):
    def __init__(self, start_x, start_y, width, height,
                 font_map: Dict[int, pygame.font.SysFont],
                 button_align: str = 'center',
                 text: str = '',
                 bg: str = 'black',
                 header_size: str = "1",
                 tight: bool = False):
        super().__init__(start_x, start_y, width, height)
        self.header_size = header_size
        self._text = text
        self.bg = bg
        self.btn_size = (140, 30)
        self.btn_x = 0
        self.tight = tight
        self.align = button_align
        self.btn_y = 0
        self.btn = None
        self.font_map = font_map
        self._update()

    @property
    def pos(self):
        return self.x, self.y

    @pos.setter
    def pos(self, pos: Tuple[int, int]):
        if self.x == pos[0] and self.y != pos[1]:
            self.x, self.y = pos
            self.btn_y = self.y + self.h // 2 - self.btn_size[1] // 2
            self.btn.pos = (self.btn_x, self.btn_y)
        else:
            self.x, self.y = pos
            self._update()

    @property
    def text(self):
        return self.btn.text

    @text.setter
    def text(self, value):
        self._text = value
        self.btn = NewButton(font_map=self.font_map,
                             text=self._text,
                             pos=(self.btn_x,
                                  self.btn_y),
                             size=self.btn_size,
                             fontsize=30,
                             tight=self.tight)

    def _update(self):
        self.btn_y = self.y + self.h // 2 - self.btn_size[1] // 2

        if self.btn:
            pass
        else:
            self.btn = NewButton(font_map=self.font_map,
                                 text=self._text,
                                 pos=(0, 0),
                                 size=self.btn_size,
                                 fontsize=30,
                                 tight=self.tight)
        if self.tight:
            self.btn_size = self.btn.size

        if self.align == 'center':
            self.btn_x = self.x + self.w // 2 - self.btn_size[0] // 2
        elif self.align == 'left':
            self.btn_x = self.x + 20
        elif self.align == 'right':
            self.btn_x = self.x + self.w - 20
        self.btn.pos = (self.btn_x, self.btn_y)

    def update(self, diff: int):
        self.y = self.y + diff
        self.btn_y = self.btn_y + diff
        self.btn.pos = (self.btn_x, self.btn_y)

    def draw(self, surface,
             show_update: bool = False):
        update_rect = pygame.Rect(self.x, self.y,
                                  self.w, self.h)

        pygame.draw.rect(surface, self.bg, update_rect)

        self.btn.draw(surface)
        self.btn.hover()
        if self.btn.selected:
            pass

        if show_update:
            pygame.draw.rect(surface,
                             'green',
                             update_rect, width=3)

    def click(self, event):
        return self.btn.click(event)