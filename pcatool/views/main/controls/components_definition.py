from pcatool.commonlibs import \
    Path, json, pygame, pd, List, Dict, Tuple, Optional
from pcatool.views.components.button import Button

from pcatool.views import BaseView, \
    TARGET_PCA_GRID, DEID_PCA_GRID, \
    TARGET_PCA_PAIR, DEID_PCA_PAIR
from pcatool.views.main.controls import FeatureView
from pcatool.views.components import \
    HeaderView, ButtonGroup, BarChart
import pcatool.util as util

class ComponentDefinitionsView(BaseView):
    def __init__(self, start_x: int, start_y: int,
                 width: int, height: int,
                 container_height: int,
                 definitions_data: pd.DataFrame,
                 font_map: Dict[int, pygame.font.SysFont],
                 title: str = 'PCA Component Definitions'):
        super().__init__(start_x, start_y, width, height)
        self.font_map = font_map
        self.container_height = container_height
        self.definitions = definitions_data.transpose()
        self.definitions = self.definitions.rename(columns={c: f'PC {c}'
                                                            for c in self.definitions.columns})
        self.title = title
        self.selected_ids = []

        self.scroll = 0
        self.header = HeaderView(font_map,
                                 self.x, self.y, self.w, 30,
                                 text=self.title, header_size='2')
        self.comp_names = self.definitions.columns.tolist() # component names
        self.feature_views = dict()
        self.select_comp_bgrp = ButtonGroup(start_x=self.x,
                                               start_y=self.y + self.header.h,
                                               width=self.w, height=40,
                                               button_names=self.comp_names,
                                               font_map=font_map,
                                               selected=self.comp_names[0],
                                               bg='white')

        self.chart = BarChart(self.definitions[[self.comp_names[0]]],
                              (self.x, self.y + self.header.h + self.select_comp_bgrp.h),
                              (self.w, self.h - self.header.h - self.select_comp_bgrp.h),
                              font_map=font_map,
                              bg_color='white', text_color='black',
                              fontsize=18)

        self.selected = self.comp_names[0]

    def update(self, scroll: int = 0):
        pass
        # if scroll and len(self.feature_views):
            # scroll_speed = 20
            # scroll *= scroll_speed
            # fv = list(self.feature_views.values())
            # new_start_y = fv[0].y + scroll
            # new_end_y = fv[-1].y + fv[-1].h + scroll
            #
            # if new_start_y > self.y + self.header.h or \
            #     new_end_y < self.y + self.h - 10:
            #     return
            # for fview in self.feature_views.values():
            #     fview.update(fview.y + scroll, 0)


    def draw(self, surface, show_update=False):
        self.chart.draw(surface)
        self.header.draw(surface)
        self.select_comp_bgrp.draw(surface)


    def click(self, event):
        updates = []
        self.select_comp_bgrp.click(event)
        self.selected = self.select_comp_bgrp.selected
        self.chart = BarChart(self.definitions[[self.selected]],
                              (self.x, self.y + self.header.h + self.select_comp_bgrp.h),
                              (self.w, self.h - self.header.h - self.select_comp_bgrp.h),
                              font_map=self.font_map,
                              bg_color='white', text_color='black',
                              fontsize=25)
        return updates

    # def reset_features(self):
    #     for fname, fview in self.feature_views.items():
    #         if self.selected is None or fname != self.selected[0]:
    #             fview.selected = ''
    #             fview.reset_buttons()
