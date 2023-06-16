import pandas as pd

from pcatool.commonlibs import pygame, \
    Optional, Tuple, Dict
from pcatool.views import BaseView
from pcatool.views.components import \
    BoxedButton, LabelButton
from pcatool.colors import target_color, deid_color


class FeatureView(BaseView):
    def __init__(self,
                 start_x: int, start_y: int,
                 width: int, height: int,
                 feature_name: str,
                 feature_data: pd.DataFrame,
                 font_map: Dict[int, pygame.font.SysFont],
                 feature_dict: Optional[Dict[str, any]] = None,
                 feature_colors: Optional[Dict[str, str]] = None):
        super().__init__(start_x, start_y, width, height)
        self._feature_name = feature_name
        self._feature_data = feature_data.astype(int)

        self._selected = False
        self._highlighted = False
        self._color = '#000000'
        self._highlight_color = '#000000'
        self._selected_color = '#000000'
        self.fdict = feature_dict
        self.fcolors = feature_colors
        self.font_map = font_map
        self.val_btns = dict()
        # loop on label and draw labels by using wrap around
        self.selected_feature = None
        self.selected_value = None
        self._update()

    @property
    def feature_data(self):
        return self._feature_data

    @feature_data.setter
    def feature_data(self, new_data: pd.DataFrame):
        self._feature_data = new_data.astype(int)
        self._update()

    def _update(self):
        self.selected_feature = None
        self.selected_value = None
        self.val_btns = dict()
        self.feature_button = BoxedButton(self.x,
                                          self.y,
                                          self.w,
                                          40,
                                          font_map=self.font_map,
                                          button_align='left',
                                          text=self._feature_name,
                                          bg='#9FABE6',
                                          tight=True)
        new_h = self.feature_button.h + 10

        btn_rows = [[]]
        row_num = 0
        padding = 10
        # print(self._feature_name)
        # print(self._feature_data)
        # print(self.fdict)
        # print()
        for f_val, (t_count, d_count) in self._feature_data.iterrows():
            row_width = sum([btn.size[0] + padding
                             for btn in btn_rows[row_num]]) + padding
            l_x = self.x + row_width
            l_y = self.y + new_h
            labels = []
            labels_color = []
            if t_count > 0:
                labels.append(str(t_count))
                labels_color.append(target_color)
            if d_count > 0:
                labels.append(str(d_count))
                labels_color.append(deid_color)

            new_val = str(f_val)
            if self.fdict:
                if str(f_val) in self.fdict["values"]:
                    new_val = self.fdict["values"][str(f_val)][0:20]

            val_color = "#4d5d53"
            if self.selected_feature is not None:
                if self.fcolors:
                    # print(str(f_val))
                    # print(self.fcolors)
                    # print()
                    val_color = self.fcolors[str(f_val)]
            self.val_btns[f_val] = LabelButton(text=str(new_val),
                                               pos=(l_x, l_y),
                                               size=(100, 25),
                                               labels=labels,
                                               labels_color=labels_color,
                                               font_map=self.font_map,
                                               fontsize=25,
                                               border_radius=8,
                                               bg_color=val_color,
                                               hover_color="#8775bd",
                                               selection_color="#9782d3")

            if row_width == 0:
                btn_rows[row_num].append(self.val_btns[f_val])
            elif row_width + self.val_btns[f_val].size[0] + padding > self.w:
                row_num += 1
                btn_rows.append([])
                new_h += self.val_btns[f_val].size[1] + padding
                lx = self.x + padding
                ly = self.y + new_h
                self.val_btns[f_val].pos = (lx, ly)
                btn_rows[row_num].append(self.val_btns[f_val])
            else:
                btn_rows[row_num].append(self.val_btns[f_val])
        new_h += 30
        # new_h += self.val_btns[f_val].size[1]
        self.w, self.h = (self.w, new_h + padding)

    def update(self, new_y: int, container_y: int = 0):
        diff = new_y - self.y
        self.y = new_y

        self.feature_button.update(diff)
        for f_val, btn in self.val_btns.items():
            btn.update(diff)

    def update_color(self):
        if self.selected_feature:
            if self.fcolors:
                for f_val, btn in self.val_btns.items():
                    val_color = self.fcolors[str(f_val)]
                    self.val_btns[f_val].bg_color = val_color
        else:
            for f_val, btn in self.val_btns.items():
                val_color = "#4d5d53"
                self.val_btns[f_val].bg_color = val_color

    def draw(self, surface: pygame.Surface,
             show_update: bool = False):
        update_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        # pygame.draw.rect(surface, 'yellow', update_rect)
        self.feature_button.draw(surface)
        for f_val, btn in self.val_btns.items():
            btn.draw(surface)
            btn.hover()
        if show_update:
            pygame.draw.rect(surface, 'green', update_rect, width=3)
        # pygame.display.update(update_rect)

    def click(self, event: pygame.event):
        res = self.feature_button.click(event)
        if res:
            self.selected_feature = self._feature_name
            self.selected_value = None
            self.reset_buttons()
            return True

        for f_val, btn in self.val_btns.items():
            res = btn.click(event)
            if res:
                self.selected_value = f_val
                self.feature_button.btn.deselect()
                self.selected_feature = None
                self.reset_buttons()
                return True
        return False

    def reset_buttons(self):
        selected = None
        for f_val, btn in self.val_btns.items():
            if f_val != self.selected_value:
                btn.deselect()
            else:
                selected = btn
        if selected is None:
            self.selected_value = None
        self.update_color()
