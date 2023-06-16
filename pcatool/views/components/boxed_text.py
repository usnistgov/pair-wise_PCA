from pcatool.commonlibs import \
    pygame, Tuple, Optional, Dict
from pcatool.fonts import font_path
import pcatool.util as u


class BoxedText:
    def __init__(self,
                 text: str,
                 pos: Tuple[int, int],
                 size: Tuple[int, int],
                 font_map: Dict[int, pygame.font.SysFont],
                 fontsize: int = 30,
                 bg_color=(0, 0, 0),
                 text_color=(255, 255, 255),
                 align_text: str = "center",
                 tight: bool = False,
                 border_radius: int = 20):
        self._text = text
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
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=(0, 0))
        self.align_text = align_text
        self.tight = tight
        if tight:
            new_w = self.text_rect.w + 20
            self._size = (new_w, self.size[1])

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

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text: str):
        self._text = text
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=(0, 0))
        self._update()

    def update(self, diff: int):
        self.pos = (self.pos[0], self.pos[1] + diff)
        self._update()

    def _update(self):
        if self.tight:
            new_w = self.text_rect.w + 20
            self._size = (new_w, self.size[1])
        else:
            self._text = u.fix_text_width(self._text, self.font,
                                          self.size[0] - 20,
                                          False)
            self.text_surface = self.font.render(self.text, True, self.text_color)
            self.text_rect = self.text_surface.get_rect(center=(0, 0))
        self.t_x = 0
        self.t_y = self.pos[1] + self.size[1] // 2
        if self.align_text == "center":
            self.t_x = self.pos[0] + self.size[0] // 2
        elif self.align_text == "left":
            self.t_x = self.pos[0] + self.text_rect.w // 2 + 10
        elif self.align_text == "right":
            self.t_x = self.pos[0] + self.size[0] - self.text_rect.w // 2 - 10
        self.text_rect.center = (self.t_x, self.t_y)
        self.rect.update(self.pos, self.size)

    def draw(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect,
                         border_radius=10)
        if self.rect_width > 0:
            pygame.draw.rect(surface, "#3E7DE8", self.rect,
                             self.rect_width, border_radius=10)
        surface.blit(self.text_surface, self.text_rect)