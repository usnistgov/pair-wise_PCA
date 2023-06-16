from pcatool.commonlibs import os, pygame, Path, \
    Optional, Tuple, Dict
from pcatool.views import BaseView
from pcatool.views.components import \
    HeaderView, NewButton, ButtonGroup, \
    BoxedButton
from pcatool.pca import fset_map, FeatureSet

import pcatool.util as util


class OptionsView(BaseView):
    def __init__(self, start_x, start_y, width, height,
                 font_map: Dict[int, pygame.font.SysFont]):
        super().__init__(start_x, start_y, width, height)
        self.header = HeaderView(font_map, self.x, self.y, self.w, 40, 'Options')
        self.select_file_h = HeaderView(font_map,
                                        self.x, self.y + self.header.h,
                                        self.w, 30,
                                        'Select Deidentified CSV Data File',
                                        bg='#1A5CC2',
                                        header_size='2')
        self.select_file_btn = NewButton(text='Select File',
                                         pos=(self.x + 20,
                                             self.select_file_h.y + self.select_file_h.h + 10),
                                         size=(140, 30),
                                         font_map=font_map,
                                         fontsize=25)
        self.selected_file_h = HeaderView(font_map,
                                          self.x,
                                          self.select_file_btn.pos[1] +
                                          self.select_file_btn.size[1] + 10,
                                          self.w, 20,
                                          'Selected File',
                                          bg='#9FC5E8',
                                          text_color='black',
                                          header_size='3',
                                          align_text='left')
        self.select_target_h = HeaderView(font_map,
                                          self.x,
                                          self.selected_file_h.y +
                                          self.selected_file_h.h + 10,
                                          self.w, 30,
                                          'Select Target Data Name',
                                          bg='#1A5CC2',
                                          header_size='2')
        self.select_target_bgrp = ButtonGroup(start_x=self.x + 20,
                                              start_y=self.select_target_h.y +
                                              self.select_target_h.h + 10,
                                              width=self.w - 40, height=30,
                                              button_names=['MA',
                                                            'TX',
                                                            'NATIONAL'],
                                              selected='NATIONAL',
                                              font_map=font_map)
        self.selected_target_file_h = HeaderView(font_map,
                                                 self.x,
                                          self.select_target_bgrp.y +
                                          self.select_target_bgrp.h + 10,
                                          self.w, 20,
                                          f'Selected Target Data: '
                                          f'{self.select_target_bgrp.selected}',
                                          bg='#9FC5E8',
                                          text_color='black',
                                          header_size='3',
                                          align_text='left')
        self.select_f_set_h = HeaderView(font_map,
                                         self.x,
                                          self.selected_target_file_h.y +
                                          self.selected_target_file_h.h + 10,
                                          self.w, 30,
                                          'Select Feature Set to Explore',
                                          bg='#1A5CC2',
                                          header_size='2')
        self.select_f_set_bgrp = ButtonGroup(start_x=self.x + 20,
                                             start_y=self.select_f_set_h.y +
                                             self.select_f_set_h.h + 10,
                                             width=self.w - 40, height=30,
                                             button_names=list([f.value.capitalize()
                                                                for f in fset_map.keys()]),
                                             selected=FeatureSet.demographic.value.capitalize(),
                                             font_map=font_map)
        self.selected_f_set_h = HeaderView(font_map,
                                           self.x,
                                           self.select_f_set_bgrp.y +
                                           self.select_f_set_bgrp.h + 10,
                                           self.w, 20,
                                           f'Selected Feature Set: '
                                           f'{self.select_f_set_bgrp.selected}',
                                           bg='#9FC5E8',
                                           text_color='black',
                                           header_size='3',
                                           align_text='left')
        # self.select_cpu_threads_h = HeaderView(self.x,
        #                                  self.selected_f_set_h.y +
        #                                  self.selected_f_set_h.h + 10,
        #                                  self.w, 30,
        #                                  'Use Multi-Threading',
        #                                  bg='#1A5CC2',
        #                                  header_size='2')
        # self.select_threads_btn = BoxedButton(self.x,
        #                                       self.select_cpu_threads_h.y +
        #                                       self.select_cpu_threads_h.h,
        #                                       self.w,
        #                                       50,
        #                                       button_align='center',
        #                                       text='Multi-Threading: Off',
        #                                       bg='white',
        #                                       tight=True)
        # self.select_threads_btn.btn.selected = \
        #     True if os.cpu_count() - 2 > 1 else False
        # if not self.select_threads_btn.btn.selected:
        #     self.select_threads_btn.btn.text = 'Multi-Threading: ON'
        # else:
        #     self.select_threads_btn.btn.text = 'Multi-Threading: OFF'
        self.start_button = BoxedButton(self.x,
                                        self.y + self.h - 50,
                                        self.w,
                                        50,
                                        font_map=font_map,
                                        button_align='center',
                                        text='START',
                                        bg='white')

        self.deid_data_file = ''
        self.selected_f_set = FeatureSet.demographic.name
        self.started = False

    def draw(self, surface,
             show_update=False):
        self.header.draw(surface)
        self.select_file_h.draw(surface)
        self.select_file_btn.draw(surface)
        self.select_file_btn.hover()

        if len(str(self.deid_data_file)) \
                and Path(self.deid_data_file).exists():
            t_path = str(util.subpath(Path(self.deid_data_file), 3))
            self.selected_file_h.text = f'Selected File: {t_path}'
            self.selected_file_h.draw(surface)

        self.select_target_h.draw(surface)
        self.select_target_bgrp.draw(surface)
        self.selected_target_file_h.text = \
            f'Selected Target Data: {self.select_target_bgrp.selected}'
        self.selected_target_file_h.draw(surface)

        self.select_f_set_h.draw(surface)
        self.select_f_set_bgrp.draw(surface)
        self.selected_f_set_h.text = \
            f'Selected Feature Set: {self.select_f_set_bgrp.selected}'
        self.selected_f_set_h.draw(surface)
        self.selected_f_set = self.select_f_set_bgrp.selected

        # self.select_cpu_threads_h.draw(surface)
        # self.select_threads_btn.draw(surface)
        #
        # if self.select_threads_btn.btn.selected:
        #     self.select_threads_btn.btn.text = 'Multi-Threading: ON'
        # else:
        #     self.select_threads_btn.btn.text = 'Multi-Threading: OFF'
        self.start_button.draw(surface)
        # h1_rect = self.ft_font_30.get_rect('Options')
        # h1_rect.center = (self.w // 2, self.y + 40)
        # self.ft_font_30.render_to(surface,
        #                           h1_rect.topleft,
        #                           'Options', (100, 200, 255))

        update_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        if show_update:
            pygame.draw.rect(surface, 'green', update_rect, width=3)
        # pygame.display.update(update_rect)

    def click(self, event):
        self.select_file_btn.click(event)
        self.select_target_bgrp.click(event)
        self.select_f_set_bgrp.click(event)
        # res = self.select_threads_btn.click(event)

        res = self.start_button.click(event)
        if res and len(str(self.deid_data_file)) \
                and Path(self.deid_data_file).exists():
            self.started = True
        else:
            self.start_button.btn.selected \
                = False
