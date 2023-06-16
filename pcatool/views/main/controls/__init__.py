from pcatool.views.main.controls.feature import FeatureView
from pcatool.views.main.controls.all_features import AllFeaturesControlView
from pcatool.views.main.controls.components_definition import \
    ComponentDefinitionsView

# control view class

from pcatool.commonlibs import \
    Path, json, pygame, pd, List, Dict, Optional, \
    BIN_FEATURES
from pcatool.views.components.button import Button

from pcatool.views import BaseView, \
    TARGET_PCA_GRID, DEID_PCA_GRID, \
    TARGET_PCA_PAIR, DEID_PCA_PAIR
from pcatool.views.components import \
    HeaderView, ButtonGroup
import pcatool.util as util
from pcatool.load import DEFAULT_DATASET


class ControlView(BaseView):
    def __init__(self, start_x: int, start_y: int,
                 width: int, height: int,
                 target_data: pd.DataFrame,
                 deid_data: pd.DataFrame,
                 data_colors_map: Dict[str, any],
                 data_dictionary: Dict[str, any],
                 component_definitions: pd.DataFrame,
                 feature_set_name: str,
                 font_map: Dict[int, pygame.font.SysFont]):
        super().__init__(start_x, start_y, width, height)
        self.data = deid_data
        self.target_data = target_data
        self.selected_ids = []
        self.texts = []
        self.btns = dict()
        self.selected_btn = tuple()
        self.scroll = 0
        self.controls_name = ['Select Feature', 'Component Definitions']
        self.select_control_bgrp = ButtonGroup(start_x=self.x,
                                               start_y=self.y,
                                               width=self.w, height=40,
                                               font_map=font_map,
                                               button_names=self.controls_name,
                                               selected=self.controls_name[0],
                                               bg='#e1e3e8')

        self.f_control = AllFeaturesControlView(self.x, self.y + self.select_control_bgrp.h,
                                                self.w, self.h - self.select_control_bgrp.h,
                                                self.h,
                                                self.target_data, self.data,
                                                data_colors_map,
                                                data_dictionary,
                                                font_map,
                                                feature_set_name)

        self.cd_control = ComponentDefinitionsView(self.x, self.y + self.select_control_bgrp.h,
                                                   self.w, self.h - self.select_control_bgrp.h,
                                                   self.h,
                                                   component_definitions,
                                                   font_map)

        DATA_DICT_PATH = Path(f'{DEFAULT_DATASET}/data_dictionary.json')
        with open(DATA_DICT_PATH) as f:
            self.ddict = json.load(f)

    def update(self, scroll: int = 0,
               target_selected_ids: Optional[List[int]] = None,
               deid_selected_ids: Optional[List[int]] = None):
        if self.select_control_bgrp.selected == self.controls_name[0]:
            self.f_control.update(scroll,
                                  target_selected_ids,
                                  deid_selected_ids)

    def draw(self, surface, show_update=False):
        update_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surface, 'white', update_rect)
        if self.select_control_bgrp.selected == self.controls_name[0]:
            self.f_control.draw(surface)
        elif self.select_control_bgrp.selected == self.controls_name[1]:
            self.cd_control.draw(surface)
        self.select_control_bgrp.draw(surface)
        if show_update:
            pygame.draw.rect(surface, 'green', update_rect, width=3)
        pygame.display.update(update_rect)

    def click(self, event):
        updates = []
        self.select_control_bgrp.click(event)
        if self.select_control_bgrp.selected == self.controls_name[0]:
            updates = self.f_control.click(event)
        elif self.select_control_bgrp.selected == self.controls_name[1]:
            updates = self.cd_control.click(event)
        return updates
