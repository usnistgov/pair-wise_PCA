from pcatool.views import BaseView
from pcatool.commonlibs import pygame, Path, Optional, \
    Tuple, Dict
from pcatool.views.components import \
    HeaderView, BoxedButton, NewButton, ScrollBar
import pcatool.util as util
from pcatool.load import DEFAULT_DATASET


class FileBrowser(BaseView):
    def __init__(self, start_x, start_y, width, height,
                 font_map: Dict[int, pygame.font.SysFont],
                 initial_path: Path = Path('DEFAULT_DATASET')):
        super().__init__(start_x, start_y, width, height)
        self.header = HeaderView(font_map, start_x, start_y, width,
                                 text='File Browser')
        self.bg = 'white'
        self.font_map = font_map
        self.old_current_path = None
        self.current_path = Path.cwd()
        if self.current_path.exists() or self.current_path.is_file():
            self.current_path = Path.cwd()
        self.selected_file = None
        parts = self.current_path.parts
        t_path = str(Path(*parts[-3:])) if len(parts) > 3 else str(self.current_path)
        self.current_path_h = HeaderView(font_map, start_x, start_y + self.header.h, width,
                                         30,
                                         text=f'Current Path: {t_path}',
                                         bg='#1A5CC2',
                                         header_size='3',
                                         align_text='left')
        self.back_btn = BoxedButton(start_x,
                                    self.current_path_h.y + self.current_path_h.h,
                                    self.w,
                                    60,
                                    font_map=font_map,
                                    button_align='left',
                                    text='Back',
                                    bg=self.bg)
        self.scrollable_h = self.h - self.current_path_h.h - self.back_btn.h - self.header.h
        self.scrollbar = ScrollBar((start_x + width - 15,
                                    (self.back_btn.y + self.back_btn.h)),
                                    (15, self.scrollable_h),
                                    bar_height=15)
        self.path_buttons = dict()
        self.file_loaded = False
        self.show = True
        self._old_selected = None
        self.scrollable = False
        self.current_y = 0

    def update(self, scroll: int = 0):

        if scroll and len(self.path_buttons):
            scroll_speed = 20
            scroll *= scroll_speed
            vals = list(self.path_buttons.values())
            new_start_y = vals[0].pos[1] + scroll
            new_end_y = vals[-1].pos[1] + vals[-1].size[1] + scroll

            if new_start_y > self.back_btn.y + self.back_btn.h + 10 or \
                    new_end_y < self.y + self.h - 10:
                return
            for pb in self.path_buttons.values():
                pb.pos = (pb.pos[0], pb.pos[1] + scroll)

            self.current_y -= scroll
            scroll_y = self.y + self.header.h + self.current_path_h.h + self.back_btn.h
            if self.current_y > 0:
                scroll_y += self.scrollable_h // ((new_end_y - new_start_y) / self.current_y)
                new_sa_h = self.scrollable_h // ((new_end_y - new_start_y)/self.current_y)

            self.scrollbar.update(scroll_y)

    def draw(self, surface,
             show_update: bool = False):
        update_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surface, self.bg, update_rect)
        if self.show:
            self.header.draw(surface)
            self.current_path_h.draw(surface)
            if self.back_btn.btn.selected:
                self.current_path = self.current_path.parent
                self.back_btn.btn.selected = False
                t_path = str(util.subpath(self.current_path))
                self.current_path_h.text = f'Current Path: {t_path}'
            if self.old_current_path != self.current_path:
                self.path_buttons = dict()
                dirs = [p for p in self.current_path.iterdir() if p.is_dir()]
                csvs = [p for p in self.current_path.iterdir() if
                        p.is_file() and p.suffix == '.csv']
                for i, p in enumerate(dirs + csvs):
                    btn_pos = (self.x + 20,
                               (self.back_btn.y + self.back_btn.h)
                               + 10 + i * 30)

                    str_path = str(util.subpath(p, 1))

                    if p.is_file() and p.suffix == '.csv':
                        p_btn = NewButton(text=str_path,
                                          pos=btn_pos,
                                          size=(self.w - 100, 25),
                                          font_map=self.font_map,
                                          fontsize=25,
                                          bg_color="#ad97eb",
                                          text_color='#1C1C1C',
                                          hover_color="#B6D7A8",
                                          selection_color="#9FC5E8",
                                          align_text='left')
                        self.path_buttons[str(p)] = p_btn
                    elif p.is_dir():
                        p_btn = NewButton(text=str_path,
                                          pos=btn_pos,
                                          size=(self.w - 100, 25),
                                          font_map=self.font_map,
                                          fontsize=25,
                                          bg_color="#F5E4B3",
                                          text_color='#1C1C1C',
                                          hover_color="#B6D7A8",
                                          selection_color="#9FC5E8",
                                          align_text='left')
                        self.path_buttons[str(p)] = p_btn
                self.old_current_path = self.current_path

                vals = list(self.path_buttons.values())
                if len(vals):
                    new_start_y = vals[0].pos[1]
                    new_end_y = vals[-1].pos[1] + vals[-1].size[1]
                    net_height = new_end_y - new_start_y
                    if net_height > self.scrollable_h:
                        self.scrollable = True
                        bar_size = self.scrollable_h // (net_height / self.scrollable_h)
                        self.scrollbar.bar_height = bar_size
                        self.scrollbar.bar_pos = (self.scrollbar.bar_pos[0],
                                                  self.y + self.current_path_h.h + self.back_btn.h +
                                                  self.header.h)
                        self.current_y = 0
                    else:
                        self.scrollable = False
            for path, p_btn in self.path_buttons.items():
                # print(p_btn.text)
                if p_btn.pos[1] + p_btn.size[1] > self.back_btn.y + self.back_btn.h + 10:
                    p_btn.draw(surface)
                    p_btn.hover()
                    if p_btn.selected and Path(path).is_dir():
                        self.current_path = Path(path)
                        t_path = str(util.subpath(self.current_path))
                        self.current_path_h.text = f'Current Path: {t_path}'
                        self.selected_file = None
                    elif p_btn.selected and Path(path) != self._old_selected:
                        self.selected_file = Path(path)
                        self.show = False
                        self.file_loaded = True

            if self.scrollable:
                self.scrollbar.draw(surface)
            self.back_btn.draw(surface)
            # self.load_button.draw(surface)
            # if self.load_button.btn.selected and self.selected_file is not None:
            #     self.show = False
            #     self.file_loaded = True
            # self.load_button.btn.selected = False
        pygame.draw.line(surface, 'black',
                         (self.x, self.y),
                         (self.x, self.y + self.h), width=1)
        if show_update:
            pygame.draw.rect(surface, 'green', update_rect, width=3)
        # pygame.display.update(update_rect)

    def click(self, event):
        if self.show:
            # self.load_button.click(event)
            self.back_btn.click(event)
            for path, p_btn in self.path_buttons.items():
                res = p_btn.click(event)
                if res:
                    for o_path, o_p_btn in self.path_buttons.items():
                        if str(path) != str(o_path):
                            o_p_btn.selected = False
                    break
