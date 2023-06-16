from pcatool.commonlibs import \
    pygame, Optional, Tuple, List
from pcatool.views import BaseView
from pcatool.views.components import NewButton, BoxedText
class ButtonSlider(BaseView):
    def __init__(self, start_x, start_y, width, height,
                 min_val: int = 0,
                 max_val: int = 100,
                 initial_val: int = 0,
                 button_align: str = 'center',
                 text: str = '',
                 bg: str = 'black',
                 header_size: str = "1"):
        super().__init__(start_x, start_y, width, height)
        self.header_size = header_size
        self.text = text
        self.bg = bg
        self.btn_size = (60, 30)
        self.min_val = min_val
        self.max_val = max_val
        self.selected_val = initial_val
        self.dec_btn = NewButton(text='-', pos=(0, 0),
                                 size=self.btn_size, fontsize=20)
        self.inc_btn = NewButton(text='+', pos=(0, 0),
                                 size=self.btn_size, fontsize=20)
        self.text = BoxedText(str(self.selected_val),
                              (0, 0),
                              (140, self.btn_size[1]),
                              bg_color="white",
                              text_color='black')

        buttons_width = sum([self.dec_btn.size[0],
                             self.inc_btn.size[0],
                             self.text.size[0]])
        gap = 10
        total_gap = gap * (3 - 1)
        prev_btn = None
        btn_x_start = 0
        self.btn_y = start_y + height // 2 - self.btn_size[1] // 2
        if button_align == 'center':
            btn_x_start = start_x + width // 2 - buttons_width // 2
        elif button_align == 'left':
            btn_x_start = start_x + 20
        elif button_align == 'right':
            btn_x_start = start_x + width - buttons_width - 20
        btn_x_start = btn_x_start - (total_gap // 2)

        self.btn_x = btn_x_start
        self.dec_btn.pos = (self.btn_x, self.btn_y)

        self.btn_x = self.btn_x + self.dec_btn.size[0] + gap
        self.text.pos = (self.btn_x, self.btn_y)

        self.btn_x = self.btn_x + self.text.size[0] + gap
        self.inc_btn.pos = (self.btn_x, self.btn_y)

    def draw(self, surface,
             show_update: bool = False):
        update_rect = pygame.Rect(self.x, self.y,
                                  self.w, self.h)

        # pygame.draw.rect(surface, self.bg, update_rect)

        self.dec_btn.draw(surface)
        self.dec_btn.hover()
        self.text.draw(surface)
        self.inc_btn.draw(surface)
        self.inc_btn.hover()

        if show_update:
            pygame.draw.rect(surface,
                             'green',
                             update_rect, width=3)
        pygame.display.update(update_rect)

    def click(self, event):
        inc_res = self.inc_btn.click(event)
        dec_res = self.dec_btn.click(event)
        if inc_res:
            self.selected_val += 1
            self.selected_val = min(self.selected_val, self.max_val)
            self.text.text = str(self.selected_val)
            self.inc_btn.selected = False
        if dec_res:
            self.selected_val -= 1
            self.selected_val = max(self.selected_val, self.min_val)
            self.text.text = str(self.selected_val)
            self.dec_btn.selected = False
