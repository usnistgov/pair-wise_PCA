from pcatool.commonlibs import \
    Path, json, pygame, pd, List, Dict, Tuple, Optional, \
    BIN_FEATURES
import copy
from pcatool.views.components.button import Button

from pcatool.views import BaseView, \
    TARGET_PCA_GRID, DEID_PCA_GRID, \
    TARGET_PCA_PAIR, DEID_PCA_PAIR
from pcatool.views.main.controls import FeatureView
from pcatool.views.components import \
    HeaderView, ScrollBar
import pcatool.util as util


def compute_combined_counts(target_data: pd.DataFrame,
                            deid_data: pd.DataFrame):
    combined_counts = dict()
    for col in target_data.columns:
        if col in BIN_FEATURES:
            continue
        if col == 'DENSITY':
            target_data[col] = target_data[col].astype(int)
            deid_data[col] = deid_data[col].astype(int)

        target_counts = target_data[col].value_counts()
        deid_counts = deid_data[col].value_counts()
        combined_counts[col] = pd.concat([target_counts, deid_counts],
                                         axis=1, sort=False).fillna(0)
        # combined_counts[col].sort_index(inplace=True)
    return combined_counts


class AllFeaturesControlView(BaseView):
    def __init__(self, start_x: int, start_y: int,
                 width: int, height: int,
                 container_height: int,
                 target_data: pd.DataFrame,
                 deid_data: pd.DataFrame,
                 data_colors_map: Dict[str, any],
                 data_dictionary: Dict[str, any],
                 font_map: Dict[int, pygame.font.SysFont],
                 feature_set_name: str = '',
                 title: str = 'Inspect Feature Values'):
        super().__init__(start_x, start_y, width, height)
        self.container_height = container_height
        self.data = deid_data
        self.target_data = target_data
        self.data_colors_map = data_colors_map
        self.title = title
        if len(feature_set_name):
            self.title = title + f' : {feature_set_name} features'
        self.selected_ids = []

        self.scroll = 0
        self.ddict = data_dictionary
        self.header = HeaderView(font_map,
                                 self.x, self.y, self.w, 30,
                                 text=self.title, header_size='2')

        self.combined_counts = compute_combined_counts(self.target_data, self.data)
        self.feature_views = dict()
        self.default_feature_views = dict()
        self.default_y = dict()
        self.prev_fview_height = 0
        for i, col in enumerate(self.data.columns):
            if col in BIN_FEATURES:
                continue
            c_dict = None
            if col not in self.ddict:
                c_dict = dict()
                c_dict['values'] = dict()
                # print(col)
                for v, g in self.target_data.groupby(col):
                    orig_c = col.split('_')[0]
                    min_v = g[orig_c].min()
                    c_dict['values'][str(v)] = f'{min_v}'
            elif 'values' in self.ddict[col] and 'min' in self.ddict[col]['values']:
                c_dict = dict()
                c_dict['values'] = dict()
                min_v = int(self.ddict[col]['values']['min'])
                max_v = int(self.ddict[col]['values']['max'])
                if col == 'DENSITY':
                    density_unique = self.data[col].astype(int).unique().tolist()
                    density_unique = density_unique + self.target_data[col].astype(int).unique().tolist()
                    density_unique = list(set(density_unique))
                    u_vals = [(str(i), str(i)) for i in density_unique]
                    # print('u_vals ', u_vals)
                else:
                    u_vals = [(str(i), str(i)) for i in range(min_v, max_v + 1)]
                    if "N" in self.ddict[col]['values']:
                        u_vals.append(("N", self.ddict[col]['values']["N"]))
                    if "0" in self.ddict[col]['values']:
                        u_vals.append(("0", self.ddict[col]['values']["0"]))
                c_dict['values'] = dict(u_vals)
            else:
                c_dict = self.ddict[col]
            self.feature_views[col] = FeatureView(self.x,
                                                  self.y + self.header.h + self.prev_fview_height,
                                                  self.w,
                                                  100,
                                                  col,
                                                  self.combined_counts[col],
                                                  font_map=font_map,
                                                  feature_dict=c_dict,
                                                  feature_colors=self.data_colors_map[col])
            self.default_feature_views[col] = FeatureView(self.x,
                                                  self.y + self.header.h + self.prev_fview_height,
                                                  self.w,
                                                  100,
                                                  col,
                                                  self.combined_counts[col],
                                                  font_map=font_map,
                                                  feature_dict=c_dict,
                                                  feature_colors=self.data_colors_map[col])
            self.default_y[col] = (self.feature_views[col].y,
                                   [b.pos[1] for v, b in self.feature_views[col].val_btns.items()])
            self.prev_fview_height += self.feature_views[col].h


        self.scrollable_h = self.h - self.header.h
        fv = list(self.feature_views.values())
        bar_size = 10
        self.scrollable = False
        if len(fv) > 0:
            new_start_y = fv[0].y
            new_end_y = fv[-1].y + fv[-1].h
            net_height = new_end_y - new_start_y
            if net_height > self.scrollable_h:
                bar_size = self.scrollable_h // (net_height / self.scrollable_h)
                self.scrollable = True

        self.scrollbar = ScrollBar((start_x + width - 15,
                                    (self.y + self.header.h)),
                                    (15, self.h - self.header.h),
                                    bar_height=bar_size)
        self.current_y = 0
        self.ddict = data_dictionary

        self.selected: Optional[Tuple[str, any]] = None


    def update(self, scroll: int = 0,
               target_selected_ids: Optional[List[int]] = None,
               deid_selected_ids: Optional[List[int]] = None):
        tsi = target_selected_ids
        dsi = deid_selected_ids
        if tsi is not None and dsi is not None:
            if (len(tsi) or len(dsi)) and scroll == 0:
                ts = self.target_data.loc[tsi, :]
                ds = self.data.loc[dsi, :]
                self.selected = None
                self.reset_features()
                self.combined_counts = compute_combined_counts(ts, ds)
                self.prev_fview_height = 0
                for fname, fview in self.feature_views.items():
                    fview.feature_data = self.combined_counts[fname]
                    fview.y = self.y + self.header.h + self.prev_fview_height
                    fview.feature_data = self.combined_counts[fname]
                    self.prev_fview_height += fview.h
            elif len(tsi) == 0 and len(dsi) == 0:
                self.selected = None
                # self.reset_features()
                # self.combined_counts = compute_combined_counts(self.target_data, self.data)
                # self.prev_fview_height = 0
                # for fname, fview in self.feature_views.items():
                #     fview.feature_data = self.combined_counts[fname]
                #     fview.y = self.y + self.header.h + self.prev_fview_height
                #     fview.feature_data = self.combined_counts[fname]
                #     self.prev_fview_height += fview.h
                self.feature_views = {col: copy.copy(v)
                                      for col, v in self.default_feature_views.items()}
                # print('Feature View: ',scroll)
                for fname, fview in self.feature_views.items():
                    fview.update(self.default_y[fname][0])
                    fview.feature_button.pos = (fview.feature_button.pos[0],
                                                self.default_y[fname][0])
                    for i, (v, b) in enumerate(fview.val_btns.items()):
                        b.pos = (b.pos[0], self.default_y[fname][1][i])
                self.reset_features()
                self.current_y = 0

            fv = list(self.feature_views.values())
            bar_size = 10
            self.scrollable = False
            if len(fv) > 0:
                new_start_y = fv[0].y
                new_end_y = fv[-1].y + fv[-1].h
                net_height = new_end_y - new_start_y
                if net_height > self.scrollable_h:
                    bar_size = self.scrollable_h // (net_height / self.scrollable_h)
                    self.scrollable = True
                    self.scrollbar.bar_height = bar_size
                    self.scrollbar.bar_pos = (self.scrollbar.bar_pos[0],
                                              self.y + self.header.h)
                    self.current_y = 0
                else:
                    self.scrollable = False
        if scroll and len(self.feature_views):
            scroll_speed = 20
            scroll *= scroll_speed
            fv = list(self.feature_views.values())
            new_start_y = fv[0].y + scroll
            new_end_y = fv[-1].y + fv[-1].h + scroll

            if new_start_y > self.y + self.header.h or \
                new_end_y < self.y + self.h - 10:
                return
            self.current_y -= scroll
            if self.current_y > 0:
                scroll_y = self.y + self.header.h  \
                           + self.scrollable_h \
                           // ((new_end_y - new_start_y)/self.current_y)
            else:
                scroll_y = self.y + self.header.h
            for fview in self.feature_views.values():
                fview.update(fview.y + scroll, 0)

            self.scrollbar.update(scroll_y)

    def draw(self, surface, show_update=False):
        update_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        # pygame.draw.rect(surface, 'white', update_rect)

        # for i, t in enumerate(self.texts):
        #     surface.blit(t[0], t[1])
        #     c = t[2]
        #     for b in self.btns[c]:
        #         b.show(surface)
        for col, f_v in self.feature_views.items():
            fv = self.feature_views[col]
            if fv.y + fv.h > 0 and fv.y < self.container_height:
                fv.draw(surface)
        self.header.draw(surface)
        if self.scrollable:
            self.scrollbar.draw(surface)
        if show_update:
            pygame.draw.rect(surface, 'green', update_rect, width=3)
        # pygame.display.update(update_rect)

    def click(self, event):
        updates = set()
        for fname, fview in self.feature_views.items():
            res = fview.click(event)
            if res:
                if fview.selected_value is None:
                    self.selected = (fname, None)
                else:
                    self.selected = (fname, fview.selected_value)
                self.reset_features()
                updates.add(TARGET_PCA_GRID)
                updates.add(DEID_PCA_GRID)
                updates.add(TARGET_PCA_PAIR)
                updates.add(DEID_PCA_PAIR)
                return updates
        return updates

    def reset_features(self):
            for fname, fview in self.feature_views.items():
                if self.selected is None or fname != self.selected[0]:
                    fview.selected_feature = None
                    fview.selected_value = None
                    fview.feature_button.btn.deselect()
                    fview.reset_buttons()

        # for i, t in enumerate(self.texts):
        #     c = t[2]
        #     for j, b in enumerate(self.btns[c]):
        #         hov = b.hover()
        #         res = b.click(event)
        #         if res:
        #             prev_selected = self.selected_btn
        #             if len(prev_selected):
        #                 pc = prev_selected[2]
        #                 pbi = prev_selected[1]
        #                 self.btns[pc][pbi].reset()
        #             self.selected_btn = (i, j, c, b.value)
        #             updates.add(TARGET_PCA_GRID)
        #             updates.add(DEID_PCA_GRID)
        #             updates.add(TARGET_PCA_PAIR)
        #             updates.add(DEID_PCA_PAIR)
        #             break
        #     if res:
        #         break
