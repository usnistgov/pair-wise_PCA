from pcatool.commonlibs import \
    List, \
    Path, pd, \
    product, \
    pygame, Tuple, Optional, BIN_FEATURES, \
    Dict
import shutil
from pcatool.pca_plots import \
    plot_all_components, plot_single_component, \
    plot_single_colored, plot_all_colored
from pcatool.util import min_max_scaling, create_path

from pcatool.views import BaseView, CONTROL
from pcatool.views.components import HeaderView
import pcatool.util as util


class PCAPairView(BaseView):
    def __init__(self, start_x: int, start_y, width: int, height: int,
                 binned_data: pd.DataFrame, pca_data: pd.DataFrame,
                 pca_axis_range: pd.DataFrame,
                 data_colors: pd.DataFrame,
                 plot_color: str,
                 resource_path: Path,
                 font_map: Dict[int, pygame.font.SysFont],
                 label: str = '',
                 title: str = '',
                 header_bg_color: str = 'black',
                 threaded: bool = True):
        super().__init__(start_x, start_y, width, height)
        self.res_path = resource_path
        create_path(self.res_path)
        self.radius = 10
        self.label = label
        self.title = title
        self.title = title + ' : Focus Pair Plot'
        self.threaded = threaded
        self.data = binned_data
        self.data_colors = data_colors
        self.pcd = pca_data
        self.par = pca_axis_range
        self.pcdt = self.pcd.copy()
        self.plot_color = plot_color
        self.selected_pair = []
        self.selected_mouse_pos = (-100, -100)
        self.selected_pair_ids = []
        self.prev_selected_data = ('', '')
        self.selected_plot = None
        self.highlighted_changed = False
        self.selected_ids_changed = False
        self.header = HeaderView(font_map, self.x, self.y, self.w, 30,
                                 text=self.title, header_size='3',
                                 bg=header_bg_color,
                                 align_text='left')

        self.highlight_columns = set()

    def draw(self, surface,
             selected_pair: List[str],
             selected_data,
             data_res_path: Path,
             highlighted_grid,
             mouse_pos: Optional[Tuple[int, int]] = None,
             mouse_sel: bool = False,
             show_update: bool = False):
        self.highlighted_changed = False
        updates = set()
        update_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surface, 'white', update_rect)
        mpos = mouse_pos
        if selected_pair and len(selected_pair):
            if tuple(selected_pair) != tuple(self.selected_pair):
                self.header.text = f'PCA Pair: {selected_pair[1]}' \
                                   f'(x-axis) | {selected_pair[0]}(y-axis)'
                self.selected_pair_ids = []
                self.selected_mouse_pos = (-100, -100)
                self.selected_pair = selected_pair
                self.pcdt = self.pcd[self.selected_pair].copy()
                c1, c2 = self.selected_pair[0], self.selected_pair[1]
                # left, bottom = 0 + self.radius, self.h - self.radius
                new_h = self.h - self.header.h
                w, h = self.w - self.radius * 2, new_h - self.radius * 2

                # self.pcdt[c1] = min_max_scaling(self.pcdt[c1])
                # self.pcdt[c2] = min_max_scaling(self.pcdt[c2])
                self.pcdt[c1] = self.y + self.header.h + (h - (self.pcdt[c1] * h)) + self.radius * 1
                self.pcdt[c2] = self.x + (self.pcdt[c2] * w) + self.radius * 1
                self.selected_ids_changed = True
                self.selected_pair_ids = []
            pc_i, pc_j = selected_pair[0], selected_pair[1]
            im_path = Path(self.res_path, f'{pc_i}_{pc_j}.png')
            if not im_path.exists():
                plot_single_component(self.pcd, im_path, pc_i, pc_j, color=self.plot_color)

            im = pygame.image.load(Path(im_path))
            im = pygame.transform.scale(im, (self.w, self.h - self.header.h))
            surface.blit(im, (self.x, self.y + self.header.h))

        rect_obj = pygame.Rect(self.x, self.y, self.w, self.h)
        pygame.draw.rect(surface, 'black', rect_obj, width=1)
        if mpos:
            mx, my = mpos
            if self.x <= mx <= self.x + self.w and self.y + self.header.h <= my <= self.y + self.h:
                if mouse_sel:
                    self.selected_mouse_pos = mpos
                    self.selected_pair_ids = self.selected_ids()
                    self.selected_ids_changed = True
                    updates.add(CONTROL)
        smx, smy = self.selected_mouse_pos
        if self.x <= smx <= self.x + self.w and self.y + self.header.h <= smy <= self.y + self.h:
            im_path = Path(self.res_path, 'selected_records.png')
            if im_path.exists():
                im = pygame.image.load(im_path)
                im = pygame.transform.scale(im, (self.w, self.h - self.header.h))
                surface.blit(im, (self.x, self.y + self.header.h))

        highlighted_path = Path(data_res_path, 'highlighted')

        if selected_data and len(selected_data):
            create_path(self.res_path)
            c = selected_data[0]
            fv = selected_data[1]
            is_selected_changed = self.selected_changed(selected_data,
                                                        self.prev_selected_data)
            if fv is None:
                sel_fv = self.pcd
            else:
                sel_fv = self.pcd[self.data[c].isin([fv])]

            if self.selected_pair and len(self.selected_pair):
                c1, c2 = self.selected_pair[0], self.selected_pair[1]

                im_path = Path(self.res_path, f'highlighted_{c1}_{c2}.png')

                if not im_path.exists() or is_selected_changed:
                    if fv is None:
                        im_path = plot_single_colored(sel_fv, self.data_colors[c + '_clr'],
                                                      im_path, c1, c2)
                    else:
                        im_path = plot_single_component(sel_fv, im_path, c1, c2)

                im = pygame.image.load(im_path)
                im = pygame.transform.scale(im, (self.w, self.h - self.header.h))
                surface.blit(im, (self.x, self.y + self.header.h))

            highlighted_path = Path(data_res_path, 'highlighted')
            if (not highlighted_path.exists()
                    or is_selected_changed) and highlighted_grid:
                create_path(highlighted_path)
                c, fv = selected_data[0], selected_data[1]
                # print('PCA PAIR', c, fv)
                if c and not fv:
                    plot_all_colored(sel_fv, self.data_colors[c + '_clr'],
                                      highlighted_path,
                                      transparent=True)
                else:
                    plot_all_components(sel_fv, highlighted_path, color='r',
                                        transparent=True,
                                        threaded=self.threaded)
                self.highlighted_changed = True
                updates.add(self.label + ' PCA Grid')
            if is_selected_changed:
                self.prev_selected_data = selected_data
        else:
            if highlighted_path.exists():
                shutil.rmtree(highlighted_path)
                updates.add(self.label + ' PCA Grid')
        if not highlighted_grid and highlighted_path.exists():
            shutil.rmtree(highlighted_path)
            updates.add(self.label + ' PCA Grid')
        if mpos:
            mx, my = mpos
            if self.x <= mx <= self.x + self.w and self.y + self.header.h <= my <= self.y + self.h:
                pygame.draw.circle(surface, '#f8d210',
                                   [mx, my], 30, 5)

        self.header.draw(surface)
        border_rect = pygame.Rect(self.x, self.y + self.header.h, self.w, self.h - self.header.h)
        pygame.draw.rect(surface, 'black', border_rect, width=1)
        if show_update:
            pygame.draw.rect(surface, 'green', update_rect, width=3)
        pygame.display.update(update_rect)

        return updates

    def selected_changed(self, new_selected_data, previous_selected_data):
        nsd = new_selected_data
        psd = previous_selected_data
        return nsd[0] != psd[0] or nsd[1] != psd[1]

    def selected_ids(self) -> List[int]:
        if self.selected_pair and len(self.selected_pair):
            c1, c2 = self.selected_pair[0], self.selected_pair[1]
            smpos = self.selected_mouse_pos
            cp = self.pcdt.copy()
            cp['inside'] = (cp[c1] - smpos[1]) ** 2 + (cp[c2] - smpos[0]) ** 2
            cp = cp[cp['inside'] <= 30 ** 2]

            sel_fv = self.pcd.loc[cp.index, :]
            im_path = Path(self.res_path, f'selected_records.png')
            im_path = plot_single_component(sel_fv, im_path, c1, c2, '#f8d210')

            return cp.index.tolist()
        return []
