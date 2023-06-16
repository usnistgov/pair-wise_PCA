from pcatool.commonlibs import os, pygame, Path, \
    Optional, Tuple, List, Dict
from pcatool.views import BaseView
from pcatool.views.components import \
    HeaderView, TextList
from pcatool.pca import fset_map, FeatureSet

import pcatool.util as util


class FeatureSetView(BaseView):
    def __init__(self, start_x, start_y, width, height,
                 feature_set_name: str,
                 data_features: List[str],
                 data_dictionary: Dict[str, any],
                 font_map: Dict[int, pygame.font.SysFont]):
        super().__init__(start_x, start_y, width, height)
        self._fset_name = feature_set_name
        self._data_features = data_features
        self.data_dict = data_dictionary
        self.feats_in_data = []
        self.feats_not_in_data = []
        self.header = HeaderView(font_map, self.x, self.y, self.w, 40,
                                 f'Feature Set: {self.fset_name}')
        self.in_text_list = TextList(self.x, self.y + self.header.h,
                                     self.w//2, self.h - self.header.h,
                                     text_items=self.feats_in_data,
                                     header_text='Present in DeID Data File',
                                     header_bg_color='#17bf4f',
                                     items_color='#17bf4f',
                                     font_map=font_map)
        self.not_in_text_list = TextList(self.x + self.w // 2, self.y + self.header.h,
                                         self.w // 2, self.h - self.header.h,
                                         text_items=self.feats_not_in_data,
                                         header_text='Missing from DeID Data File',
                                         header_bg_color='#F57777',
                                         items_color='#F57777',
                                         font_map=font_map)
        self.scroll = 0
        self._update()

    def _update(self):
        fset = fset_map[FeatureSet[self.fset_name.lower()]]
        if fset is None:
            fset = list(self.data_dict.keys())
        self.feats_in_data = [feat
                              for feat in fset
                              if feat in self._data_features]
        self.feats_not_in_data = [feat
                                  for feat in fset
                                  if feat not in self._data_features]
        self.in_text_list.text_items = self.feats_in_data
        self.not_in_text_list.text_items = self.feats_not_in_data

    @property
    def data_features(self):
        return self._data_features

    @data_features.setter
    def data_features(self, data_features: List[str]):
        self._data_features = data_features
        self._update()

    @property
    def fset_name(self):
        return self._fset_name

    @fset_name.setter
    def fset_name(self, fset_name: str):
        if fset_name != self.fset_name:
            self._fset_name = fset_name
            self.header.text = f'Feature Set: {self.fset_name}'
            self._update()

    def update(self, scroll: int):
        self.scroll = scroll

    def draw(self, surface,
             show_update=False):
        update_rect = pygame.Rect(self.x, self.y, self.w, self.h)

        self.header.draw(surface)
        self.in_text_list.draw(surface)
        self.in_text_list.update(self.scroll)
        self.not_in_text_list.draw(surface)
        self.not_in_text_list.update(self.scroll)
        pygame.draw.line(surface, 'black',
                         (self.x, self.y),
                         (self.x, self.y + self.h), width=1)
        # pygame.draw.rect(surface, 'black', update_rect, width=1)
        if show_update:
            pygame.draw.rect(surface, 'green', update_rect, width=3)
        # pygame.display.update(update_rect)

    def click(self, event):
        pass

