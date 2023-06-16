from pcatool.commonlibs import pygame, Tuple


class NewButton:
    def __init__(self,
                 text: str,
                 pos: Tuple[int, int],
                 size: Tuple[int, int],
                 fontsize: int = 30,
                 bg_color=(0, 0, 0),
                 text_color=(255, 255, 255),
                 hover_color='#00A000'):
        self.text = text
        self.pos = pos
        self.size = size
        self.default_bg_color = bg_color
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.rect_width = 0
        self.font = pygame.font.SysFont('Arial', fontsize)
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect(center=(self.pos[0] + self.size[0] / 2,
                                                            self.pos[1] + self.size[1] / 2))
        self.rect = pygame.Rect(self.pos, self.size)
        self.selected = False

    def draw(self, surface):
        # rounded pygame rect
        if self.selected:
            self._selected_state()
        pygame.draw.rect(surface, self.bg_color, self.rect,
                         border_radius=10)
        if self.rect_width > 0:
            pygame.draw.rect(surface, "#3E7DE8", self.rect,
                             self.rect_width, border_radius=10)
        surface.blit(self.text_surface, self.text_rect)

    def click(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if pygame.mouse.get_pressed()[0]:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    self.selected = False if self.selected else True
                    return True
        return False

    def deselect(self):
        self.selected = False
        self.reset()

    def hover(self):
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            self._hover_state()
            return True
        else:
            self.reset()
            return False

    def _hover_state(self):
        self.bg_color = self.hover_color
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        self.rect_width = 2

    def _selected_state(self):
        self.bg_color = '#306A9E'
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
        self.rect_width = 2

    def reset(self):
        self.bg_color = self.default_bg_color
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.rect_width = 0


class Button:
    """Create a button, then blit the surface in the while loop"""

    def __init__(self, text, value, pos, bg="black", text_clr='black', feedback=""):
        self.data = text
        self.value = value
        self.x, self.y = pos
        self.font = pygame.font.SysFont("Arial", 18)
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
