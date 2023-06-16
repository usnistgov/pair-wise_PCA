from pcatool.views.entry.title import TitleView
from pcatool.views.entry.options import OptionsView
from pcatool.views.entry.featureset import FeatureSetView
from pcatool.load import DEFAULT_DATASET

# Main View Class
import pandas as pd
import pygame.freetype

from pcatool.commonlibs import Path, pygame, json, Dict
from pcatool.views.components import FileBrowser
from pcatool.fonts import get_font_map

class EntryView:
    def __init__(self, display_w, display_h,
                 feature_sets: Dict, target_data_path: Path):
        self.w = int(display_w // 1.25)
        self.h = int(display_h // 1.25)
        self.feature_sets = feature_sets
        # self.data_path = target_data_path
        font_map = get_font_map()
        data_dict_path = Path(DEFAULT_DATASET, 'data_dictionary.json')
        self.data_dict = dict()
        if data_dict_path.exists():
            with data_dict_path.open('r') as f:
                self.data_dict = json.load(f)
        # self.ft_font_50 = pygame.freetype.SysFont('Sans', 50)
        # self.ft_font_30 = pygame.freetype.SysFont('Sans', 30)

        self.title_view = TitleView(0, 0, self.w, self.h//5, font_map=font_map)
        height_extra = self.h - self.h//5 - self.h//5 * 4
        self.options_view = OptionsView(0, self.h//5,
                                        self.w//2,
                                        self.h//4 * 3, font_map=font_map)

        self.fbrowser_view = FileBrowser(self.w//2, self.h//5,
                                         self.w//2, self.h//5 * 4 + height_extra,
                                         font_map=font_map)
        self.fset_view = FeatureSetView(self.w//2, self.h//5,
                         self.w//2, self.h//5 * 4 + height_extra,
                         feature_set_name=self.options_view.select_f_set_bgrp.selected,
                         data_features=[],
                         data_dictionary=self.data_dict,
                         font_map=font_map)
        self.mouse_pos = (0, 0)
        self.mouse_sel = False
        self.scroll = 0
        self.showfps = True
        self.stop = False
        self.exit = False

        self.data_features = []
        self.update()

    def update(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
        self.surf = pygame.display.set_mode((self.w, self.h), flags)

        self.surf.fill('white')
        self.options_view.started = False
        self.stop = False
        self.exit = False

    def draw(self):

        while not (self.exit or self.stop):
            self.scroll = 0
            for e in pygame.event.get():
                if e.type == pygame.QUIT:
                    self.exit = True
                elif e.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_sel = True
                    self.mouse_pos = e.pos
                elif e.type == pygame.MOUSEBUTTONUP:
                    self.mouse_sel = False
                    self.mouse_pos = e.pos
                elif e.type == pygame.MOUSEMOTION:
                    self.mouse_pos = e.pos
                if e.type == pygame.MOUSEWHEEL:
                    self.scroll = e.y
                self.options_view.click(e)
                self.fbrowser_view.click(e)


            self.title_view.draw(self.surf)
            self.options_view.draw(self.surf)
            if self.options_view.select_file_btn.selected:
                self.fbrowser_view.show = True
                self.fbrowser_view._old_selected = self.fbrowser_view.selected_file
            else:
                self.fbrowser_view.show = False

            if self.options_view.started:
                self.stop = True

            if self.fbrowser_view.show:
                self.fbrowser_view.draw(self.surf)
                self.fbrowser_view.update(self.scroll)
            else:
                self.fset_view.fset_name = self.options_view.selected_f_set
                self.fset_view.draw(self.surf)
                self.fset_view.update(self.scroll)

            if self.fbrowser_view.file_loaded \
                    and not self.fbrowser_view.show:
                self.options_view.deid_data_file = \
                    self.fbrowser_view.selected_file
                if Path(self.options_view.deid_data_file).exists():
                    data = pd.read_csv(Path(self.options_view.deid_data_file))
                    print('loaded data')
                    # drop columns with Unnamed
                    data = data.loc[:, ~data.columns.str.contains('Unnamed')]
                    self.data_features = list(data.columns)
                    self.fset_view.data_features = self.data_features

                self.options_view.select_file_btn.selected = False
                self.fbrowser_view.file_loaded = False

            surface_rect = pygame.Rect(0, 0, self.w, self.h)
            pygame.display.update(surface_rect)
