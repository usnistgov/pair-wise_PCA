from pcatool.commonlibs import pygame, Tuple, \
    Optional, List, Dict
from pcatool.views.components import BoxedText


class LabelButton:
    def __init__(self,
                 text: str,
                 pos: Tuple[int, int],
                 size: Tuple[int, int],
                 labels: List[str],
                 labels_color: List[str],
                 font_map: Dict[int, pygame.font.SysFont],
                 fontsize: int = 30,
                 bg_color=(0, 0, 0),
                 text_color=(255, 255, 255),
                 hover_color='#00A000',
                 selection_color='#306A9E',
                 border_radius: int = 20):
        self._text = text
        self._pos = pos
        self._size = size
        self.default_bg_color = bg_color
        self._bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.selected_color = selection_color
        self.font_map = font_map
        self.fontsize = fontsize
        self.labels = labels
        self.labels_color = labels_color
        self.border_radius = border_radius
        self.rect_width = 0

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
    def text(self, new_text: str):
        self._update()
        self._text = new_text

    @property
    def bg_color(self):
        return self._bg_color

    @bg_color.setter
    def bg_color(self, new_color: str):
        self._bg_color = new_color
        self.default_bg_color = new_color
        self._update()

    def _update(self):
        self.t_x = 0
        self.t_y = self.pos[1] + self.size[1] // 2
        self.font = self.font_map[self.fontsize]
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=(0, 0))
        tw, th = self.text_surface.get_size()
        t_x, t_y = (self.pos[0] + tw // 2 + 10,
                    self.pos[1] + self.size[1] // 2)
        self.text_rect = self.text_surface.get_rect(center=(t_x, t_y))

        self.boxed_texts = []
        net_w = self.text_rect.w + 10
        for l, lc in zip(self.labels, self.labels_color):
            l_h = int(self._size[1] * 0.7)
            b_x = self.text_rect.x + net_w + 5
            b_y = self.pos[1] + self._size[1] // 2 - l_h // 2
            bx_txt = BoxedText(str(l),
                               (b_x, b_y),
                               (140, l_h),
                               font_map=self.font_map,
                               fontsize=20,
                               bg_color=lc,
                               text_color='black',
                               tight=True,
                               border_radius=10)
            self.boxed_texts.append(bx_txt)
            net_w += (bx_txt.size[0] + 5)
        self._size = (net_w + 20, self._size[1])
        self.rect = pygame.Rect(self.pos, self.size)

    def update(self, diff: int):
        self._pos = (self._pos[0], self._pos[1] + diff)
        self.rect = pygame.Rect(self._pos, self.size)
        self.text_rect = self.text_surface.get_rect(center=(0, 0))
        tw, th = self.text_surface.get_size()
        t_x, t_y = (self._pos[0] + tw // 2 + 10,
                    self._pos[1] + self.size[1] // 2)
        self.text_rect = self.text_surface.get_rect(center=(t_x, t_y))

        for bx_txt in self.boxed_texts:
            bx_txt.update(diff)

    def draw(self, surface):
        # rounded pygame rect
        if self.selected:
            self._selected_state()
        pygame.draw.rect(surface, 'white', self.rect)
        pygame.draw.rect(surface, self._bg_color, self.rect,
                         border_radius=self.border_radius)
        for bx_txt in self.boxed_texts:
            bx_txt.draw(surface)
        if self.rect_width > 0:
            pygame.draw.rect(surface, "#3E7DE8", self.rect,
                             self.rect_width, border_radius=10)
        surface.blit(self.text_surface, self.text_rect)

    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    self.selected = False if self.selected else True
                    return True
        return False

    def deselect(self):
        self.selected = False
        self.reset()

    def hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            if not self.selected:
                self._hover_state()
            return True
        else:
            self.reset()
            return False

    def _hover_state(self):
        self._bg_color = self.hover_color
        # pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        self.rect_width = 2

    def _selected_state(self):
        self._bg_color = self.selected_color
        self.rect_width = 2

    def reset(self):
        self._bg_color = self.default_bg_color
        # pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.rect_width = 0