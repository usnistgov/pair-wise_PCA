from pcatool.commonlibs import pygame, \
    Tuple, Optional, Dict
import pcatool.util as u

class NewButton:
    def __init__(self,
                 text: str,
                 pos: Tuple[int, int],
                 size: Tuple[int, int],
                 font_map: Dict[int, pygame.font.SysFont],
                 fontsize: int = 30,
                 bg_color=(0, 0, 0),
                 text_color=(255, 255, 255),
                 hover_color='#00A000',
                 selection_color='#306A9E',
                 align_text: str = "center",
                 tight: bool = False,
                 border_radius: int = 10):
        self._text = text
        self._pos = pos
        self._size = size
        self.default_bg_color = bg_color
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.selected_color = selection_color
        self.fontsize = fontsize
        self.rect_width = 0
        self.t_x = 0
        self.t_y = self.pos[1] + self.size[1] // 2
        self.padding = 20
        self.font = font_map[fontsize]
        # self._text = u.fix_text_width(self._text, self.font,
        #                               self.size[0] - self.padding,
        #                               False)
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=(0, 0))
        self.align_text = align_text
        self.tight = tight
        self.border_radius = border_radius
        if self.tight:
            new_w = self.text_rect.w + self.padding
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
    def text(self, new_text: str):
        self._text = new_text
        self._update()

    def _update(self):

        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=(0, 0))

        if self.tight:
            new_w = self.text_rect.w + self.padding
            self._size = (new_w, self.size[1])
        else:
            self._text = u.fix_text_width(self._text, self.font,
                                          self.size[0] - self.padding,
                                          False)
            self.text_surface = self.font.render(self.text, True, self.text_color)
            self.text_rect = self.text_surface.get_rect(center=(0, 0))
        self.t_x = 0
        self.t_y = self.pos[1] + self.size[1] // 2
        if self.align_text == "center":
            self.t_x = self.pos[0] + self.size[0] // 2
        elif self.align_text == "left":
            self.t_x = self.pos[0] + self.text_rect.w // 2 + self.padding // 2
        elif self.align_text == "right":
            self.t_x = self.pos[0] + self.size[0] - self.text_rect.w // 2 - self.padding // 2
        self.rect = pygame.Rect(self.pos, self.size)
        self.text_rect.center = (self.t_x, self.t_y)
        self.rect.update(self.pos, self.size)

    def draw(self, surface):
        # rounded pygame rect
        if self.selected:
            self._selected_state()
        pygame.draw.rect(surface, self.bg_color, self.rect,
                         border_radius=self.border_radius)
        if self.rect_width > 0:
            pygame.draw.rect(surface, "#3E7DE8", self.rect,
                             self.rect_width, border_radius=self.border_radius)
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
        self.bg_color = self.hover_color
        # pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        self.rect_width = 2

    def _selected_state(self):
        self.bg_color = self.selected_color
        self.rect_width = 2

    def reset(self):
        self.bg_color = self.default_bg_color
        # pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.rect_width = 0


class Button:
    """Create a button, then blit the surface in the while loop"""

    def __init__(self, text, value, pos, bg="black", text_clr='black', feedback=""):
        self.data = text
        self.value = value
        self.x, self.y = pos
        self.font = pygame.font.SysFont(None, 18)
        self.bg = bg
        self.text_clr = text_clr
        if feedback == "":
            self.feedback = "text"
        else:
            self.feedback = feedback
        self.change_text(text, bg, self.text_clr)

    def change_text(self, text, bg="black", text_clr='black'):
        """Change the text whe you click"""
        self.text = self.font.render(text, True, pygame.Color(text_clr))
        self.size = self.text.get_size()
        self.btn_surface = pygame.Surface(self.size)
        self.btn_surface.fill(bg)
        self.btn_surface.blit(self.text, (0, 0))
        self.rect = pygame.Rect(self.x, self.y, self.size[0], self.size[1])
        self.clicked = False

    def show(self, surface):
        surface.blit(self.btn_surface, (self.x, self.y))

    def click(self, event):
        x, y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(x, y):
                    self.change_text(self.data, bg="red", text_clr='white')
                    self.clicked = True
                    return True
        return False

    def hover(self):
        x, y = pygame.mouse.get_pos()
        if self.clicked:
            return
        if self.rect.collidepoint(x, y):
            self.change_text(self.data, bg="green", text_clr='black')
            return True
        else:
            self.change_text(self.data, bg="gray", text_clr='black')
        return False

    def reset(self):
        self.change_text(self.data, bg=self.bg)
        self.clicked = False

