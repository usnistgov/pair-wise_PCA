from pcatool.commonlibs import \
    Path, json, pygame, pd, List, Dict, Optional
from pcatool.views.components.button import Button

from pcatool.views import BaseView, \
    TARGET_PCA_GRID, DEID_PCA_GRID, \
    TARGET_PCA_PAIR, DEID_PCA_PAIR
from pcatool.views.components import \
    HeaderView, ButtonGroup, NewButton, BoxedText
import pcatool.util as util

MENU = 'Menu'
HIGHLIGHT_ALL_PAIRS = 'Highlight All Pairs'
SCREENSHOT = 'Screenshot'


class MenuBarView(BaseView):
    def __init__(self, start_x: int, start_y: int,
                 width: int, height: int,
                 filepath: str,
                 font_map: Dict[int, pygame.font.SysFont]):
        super().__init__(start_x, start_y, width, height)
        self.btns = dict()
        padding = 10
        btn_h = 25
        btn_w = 100
        btn_names = ['Menu', 'Highlight All Pairs', 'Screenshot']
        btn_x = padding
        self.bg_color = '#c4c7d1'
        for bn in btn_names:
            self.btns[bn] = NewButton(bn,
                                     (self.x + btn_x, self.h//2 - btn_h//2),
                                     (btn_w, btn_h),
                                      font_map=font_map,
                                     fontsize=25,
                                     tight=True,
                                     border_radius=5,
                                     bg_color='#415d93',
                                     hover_color='#418393',
                                     selection_color='#00A000')
            btn_x += self.btns[bn].size[0] + padding
        parts = Path(filepath).parts
        if len(parts) > 4:
            filepath = Path(*parts[-4:])

        self.bx_txt_title = BoxedText('Deid File:',
                                      (btn_x + padding // 2, self.h//2 - btn_h//2),
                                      (140, btn_h),
                                      font_map=font_map,
                                      fontsize=25,
                                      bg_color=self.bg_color,
                                      text_color='black',
                                      tight=True,
                                      border_radius=10)
        txt_x = self.bx_txt_title.pos[0] + self.bx_txt_title.size[0]
        self.bx_txt = BoxedText(str(filepath),
                                (txt_x,
                                 self.h//2 - btn_h//2),
                                (self.w - txt_x, btn_h),
                                font_map=font_map,
                                fontsize=25,
                                bg_color=self.bg_color,
                                text_color='black',
                                align_text='left',
                                border_radius=10)

    def update(self):
        pass

    def draw(self, surface, show_update=False):
        update_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surface, self.bg_color, update_rect)
        for btn in self.btns.values():
            btn.draw(surface)
            btn.hover()
        self.bx_txt_title.draw(surface)
        self.bx_txt.draw(surface)
        if show_update:
            pygame.draw.rect(surface, 'green', update_rect, width=3)
        pygame.display.update(update_rect)

    def click(self, event):
        updates = []
        for bn, btn in self.btns.items():
            res = btn.click(event)
            if bn == HIGHLIGHT_ALL_PAIRS and res:
                updates.extend([TARGET_PCA_GRID, DEID_PCA_GRID,
                                TARGET_PCA_PAIR, DEID_PCA_PAIR])
        return updates
