from pcatool.views import BaseView
from pcatool.commonlibs import pygame, Dict

import pcatool.util as u


class HeaderView(BaseView):
    def __init__(self, font_map: Dict[int, pygame.font.SysFont],
                 start_x, start_y, width, height=40,
                 text: str = '',
                 bg: str = 'black',
                 text_color: str = 'white',
                 header_size: str = "1",
                 align_text: str = "center"):
        super().__init__(start_x, start_y, width, height)
        self.header_size = header_size
        self._text = text
        self.bg = bg
        self.text_color = text_color
        self.t_x = 0
        self.t_y = self.y + self.h // 2
        self.fontsize = 40
        self.align_text = align_text
        if self.header_size == "1":
            self.fontsize = 40
        elif self.header_size == "2":
            self.fontsize = 30
        elif self.header_size == "3":
            self.fontsize = 25
        self.font = font_map[self.fontsize]
        self.update_text()

    def update_text(self):
        self._text = u.fix_text_width(self._text, self.font, self.w - 20)
        text_surface = self.font.render(self._text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(self.x, self.y))
        if self.align_text == "center":
            self.t_x = self.x + self.w // 2
        elif self.align_text == "left":
            self.t_x = self.x + text_rect.w // 2 + 10
        elif self.align_text == "right":
            self.t_x = self.x + self.w - text_rect.w // 2 - 10

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        self.update_text()

    def draw(self, surface, show_update: object = False):
        update_rect = pygame.Rect(self.x, self.y,
                                  self.w, self.h)
        pygame.draw.rect(surface, self.bg, update_rect)
        # pygame.draw.rect(surface, 'red', self.text_rect)
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.t_x, self.t_y))
        surface.blit(text_surface, text_rect)

        if show_update:
            pygame.draw.rect(surface,
                             'green',
                             update_rect, width=3)
        pygame.display.update(update_rect)


