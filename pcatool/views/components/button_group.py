from pcatool.commonlibs import \
    pygame, Optional, Tuple, List, Dict
from pcatool.views import BaseView
from pcatool.views.components import NewButton


class ButtonGroup(BaseView):
    def __init__(self, start_x, start_y, width, height,
                 button_names: List[str],
                 selected: str,
                 font_map: Dict[int, pygame.font.SysFont],
                 button_align: str = 'center',
                 text: str = '',
                 bg: Optional[str] = None,
                 header_size: str = "1"):
        super().__init__(start_x, start_y, width, height)
        self.header_size = header_size
        self.text = text
        self.bg = bg
        self.btn_size = (140, 30)
        self.button_names = button_names
        self.buttons = dict()
        self.selected = selected
        for i, bn in enumerate(self.button_names):
            btn = NewButton(text=bn,
                            pos=(0, 0),
                            size=self.btn_size,
                            font_map=font_map,
                            fontsize=25,
                            tight=True)
            self.buttons[bn] = btn
            if bn == self.selected:
                btn.selected = True
        buttons_width = sum([b.size[0] for b in self.buttons.values()])
        gap = 10
        total_gap = 10 * (len(self.buttons) - 1)
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
        for bn, btn in self.buttons.items():
            if prev_btn:
                self.btn_x = prev_btn.pos[0] + prev_btn.size[0] + gap
            else:
                self.btn_x = btn_x_start
            prev_btn = btn
            btn.pos = (self.btn_x, self.btn_y)

    def draw(self, surface,
             show_update: bool = False):
        update_rect = pygame.Rect(self.x, self.y,
                                  self.w, self.h)
        if self.bg:
            pygame.draw.rect(surface, self.bg, update_rect)

        for bn, btn in self.buttons.items():
            btn.draw(surface)
            btn.hover()
            if btn.selected:
                pass

        if show_update:
            pygame.draw.rect(surface,
                             'green',
                             update_rect, width=3)
        # pygame.display.update(update_rect)

    def click(self, event):
        for bn, btn in self.buttons.items():
            res = btn.click(event)
            if res:
                self.selected = bn
                for o_bn, o_btn in self.buttons.items():
                    if o_bn != bn:
                        o_btn.selected = False
