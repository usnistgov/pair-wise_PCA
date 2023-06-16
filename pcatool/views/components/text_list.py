from pcatool.views import BaseView
from pcatool.commonlibs import pygame, Path, Optional, Tuple, \
    List, Dict
from pcatool.views.components import \
    HeaderView, BoxedButton, NewButton, BoxedText, \
    ScrollBar
import pcatool.util as util


class TextList(BaseView):
    def __init__(self, start_x, start_y, width, height,
                 text_items: List[str],
                 font_map: Dict[int, pygame.font.SysFont],
                 header_text: str = '',
                 items_color: str = 'blue',
                 header_bg_color: str = 'black'):
        super().__init__(start_x, start_y, width, height)
        self.font_map = font_map
        self.header = HeaderView(font_map,start_x, start_y, width, 30,
                                 bg=header_bg_color,
                                 text=header_text,
                                 header_size="2")
        self.scrollable_h = self.h - self.header.h
        self.scrollbar = ScrollBar((start_x + width - 15,
                                    start_y + self.header.h),
                                   (15, self.scrollable_h),
                                   bar_height=15)

        self._text_items = text_items
        self.items_color = items_color
        self.bg = 'white'
        self.texts = []
        self.items_heights = 0
        self.scrollable = False
        self.current_y = 0
        self._update()

    @property
    def text_items(self):
        return self._text_items

    @text_items.setter
    def text_items(self, text_items: List[str]):
        self._text_items = text_items
        self._update()

    def _update(self):
        self.texts = []
        start_x = self.x + 10
        start_y = self.y + self.header.h
        for i, t in enumerate(self.text_items):
            text = BoxedText(t, (start_x, start_y + 10 + i * 30),
                             (self.w - 40, 20),
                             bg_color=self.bg,
                             fontsize=30,
                             text_color=self.items_color,
                             tight=True,
                             font_map=self.font_map)
            self.texts.append(text)

        if len(self.texts) > 1:
            first_text = self.texts[0]
            last_text = self.texts[-1]
            self.text_start_y = first_text.pos[1]
            self.text_end_y = last_text.pos[1] + last_text.size[1]
            self.items_heights = self.text_end_y - self.text_start_y
            if self.items_heights > self.h - self.header.h:
                self.scrollable = True
                self.scrollbar.bar_pos = (self.scrollbar.bar_pos[0],
                                          self.y + self.header.h)
                self.current_y = 0
            else:
                self.scrollable = False
        if self.scrollable:
            bar_size = (self.h - self.header.h)//(self.items_heights / (self.h - self.header.h))
            self.scrollbar.bar_height = bar_size

    def update(self, scroll: int = 0):
        if scroll and len(self.texts):
            scroll_speed = 20
            scroll *= scroll_speed
            new_start_y = self.texts[0].pos[1] + scroll
            new_end_y = self.texts[-1].pos[1] + self.texts[-1].size[1] + scroll
            if new_start_y > self.y + self.header.h + 10 or \
                    new_end_y < self.y + self.h - 10:
                return
            for text in self.texts:
                    text.pos = (text.pos[0], text.pos[1] + scroll)
            self.current_y -= scroll
            scroll_y = self.y + self.header.h
            if self.current_y > 0:
                scroll_y += self.scrollable_h // ((new_end_y - new_start_y) / self.current_y)
                new_sa_h = self.scrollable_h // ((new_end_y - new_start_y)/self.current_y)

                # print('Scrolling: ', scroll_y, self.current_y,
                #       (new_end_y - new_start_y) / self.current_y, new_sa_h, self.scrollable_h)

            self.scrollbar.update(scroll_y)

    def draw(self, surface,
             show_update: bool = False):
        update_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surface, self.bg, update_rect)

        for text in self.texts:
            if text.pos[1] + text.size[1] > self.y + self.header.h:
                text.draw(surface)
        self.header.draw(surface)
        if self.scrollable:
            self.scrollbar.draw(surface)
        if show_update:
            pygame.draw.rect(surface, 'green', update_rect, width=3)
        # pygame.display.update(update_rect)

    def click(self, event):
        pass
