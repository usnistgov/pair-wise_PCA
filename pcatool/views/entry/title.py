from pcatool.commonlibs import pygame, Dict
from pcatool.views import BaseView
class TitleView(BaseView):
    def __init__(self, start_x, start_y, width, height,
                 font_map: Dict[int, pygame.font.SysFont]):
        super().__init__(start_x, start_y, width, height)
        self.texts = ['PCA Inspector Tool',
                      'For',
                      'NIST Diverse Communities Data Excerpts']
        self.texts_w = []
        self.font = font_map[40]
        for t in self.texts:
            text_surface = self.font.render(t, True, (100, 200, 255))
            text_rect = text_surface.get_rect(center=(0, 0))
            self.texts_w.append(text_rect.w)

    def draw(self, surface, show_update=False):
        for i, txt in enumerate(self.texts):
            r_x = self.x + (self.w - self.texts_w[i]) // 2 - 20
            rect = pygame.Rect(r_x, self.y + i * 35 + (i + 1) * 5, self.texts_w[i] + 40, 35)
            pygame.draw.rect(surface, '#b8c0ff', rect, border_radius=20)
            text_surface = self.font.render(txt, True, "#264653")
            text_rect = text_surface.get_rect(center=(0, 0))
            text_rect.center = (self.w // 2, 20 + i * 35 + (i + 1) * 5)
            surface.blit(text_surface, text_rect)
        update_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        if show_update:
            pygame.draw.rect(surface, 'green', update_rect, width=3)
        pygame.display.update(update_rect)
