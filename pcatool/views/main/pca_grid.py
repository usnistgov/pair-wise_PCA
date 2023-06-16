from pcatool.commonlibs import \
    Path, pd, pygame, shutil, \
    Tuple, Optional, Dict

from pcatool.views import BaseView, CONTROL
from pcatool.views.components import HeaderView


class PCAGridView(BaseView):
    def __init__(self,
                 start_x: int,
                 start_y: int,
                 width: int,
                 height: int,
                 pca_data: pd.DataFrame,
                 data_result_path: Path,
                 filename: str,
                 font_map: Dict[int, pygame.font.SysFont],
                 label: str = '',
                 title: str = 'PCA Grid',
                 header_bg_color: str = 'black'):
        super().__init__(start_x, start_y, width, height)
        self.n_components = 5  # number of components
        self.r = self.n_components
        self.c = self.n_components
        self.header_height = 30
        self.cw = width // self.c
        self.ch = (height - self.header_height) // self.r
        self.pca_data = pca_data
        self.label = label
        self.title = title
        self.title = title + f' : All Pair Plots ({filename})'
        self.data_result_path = data_result_path
        self.cords = []
        self.selected_pair = []
        self.selected_mouse_pos = (-1, -1)

        self.header = HeaderView(font_map, self.x, self.y, self.w, 30,
                                 text=self.title,
                                 header_size='3',
                                 bg=header_bg_color,
                                 align_text='left')
        self.pc_highlighted_path = Path(data_result_path, 'highlighted')
        if self.pc_highlighted_path.exists():
            shutil.rmtree(self.pc_highlighted_path)
        self._pc_images = dict()
        self._pc_highlighted_images = dict()

        self._setup()

    def _setup(self):
        for ri in range(self.r):
            next_row = []
            for ci in range(self.c):
                left = self.x + ci * self.cw
                top = self.y + self.header.h + ri * self.ch

                next_row.append((left, top))
            self.cords.append(next_row)

    def draw(self,
             surface,
             mouse_pos: Optional[Tuple[int, int]],
             mouse_sel: bool = False,
             highlight_changed: bool = False,
             show_update: bool = False):
        mpos = mouse_pos
        updates = set()
        # print('Update')
        # for col in pcad.columns:
        #     pcad[col] = min_max_scaling(pcad[col])

        font = pygame.font.Font('freesansbold.ttf', 32)
        for ri, pc_i in enumerate(self.pca_data.columns):
            for ci, pc_j in enumerate(self.pca_data.columns):
                left, top = self.cords[ri][ci]
                if ri == ci:
                    text = font.render(pc_i, True, 'black')
                    textRect = text.get_rect()
                    textRect.center = left + self.cw // 2, top + self.ch // 2
                    pygame.draw.rect(surface, 'white', pygame.Rect(left, top, self.cw, self.ch))
                    surface.blit(text, textRect)
                else:
                    comp = f'{pc_i}_{pc_j}'
                    if comp in self._pc_images:
                        im = self._pc_images[comp]
                    else:
                        im_path = Path(self.data_result_path, f'{comp}.png')
                        if not im_path.exists():
                            continue
                        im = pygame.image.load(Path(self.data_result_path, f'{comp}.png'))
                        im = pygame.transform.scale(im, (self.cw, self.ch))
                        self._pc_images[comp] = im

                    surface.blit(im, (left, top))

                    if self.pc_highlighted_path.exists():
                        # if highlight_changed and len(self._pc_highlighted_images) == 20:
                        #     self._pc_highlighted_images = dict()
                        # print('Path exists', self.pc_highlighted_path)
                        # if comp in self._pc_highlighted_images and not highlight_changed:
                        #     im = self._pc_highlighted_images[comp]
                        # else:
                        im_path = Path(self.pc_highlighted_path, f'{comp}.png')
                        if not im_path.exists():
                            continue
                        im = pygame.image.load(Path(self.pc_highlighted_path, f'{comp}.png'))
                        im = pygame.transform.scale(im, (self.cw, self.ch))
                        self._pc_highlighted_images[comp] = im

                        surface.blit(im, (left, top))

                rect_obj = pygame.Rect(left, top, self.cw, self.ch)
                pygame.draw.rect(surface, 'black', rect_obj, width=1)

                if mpos:
                    if left <= mpos[0] < left + self.cw and top <= mpos[1] < top + self.ch and \
                            ri != ci:
                        rect_obj = pygame.Rect(left, top, self.cw, self.ch)
                        pygame.draw.rect(surface, 'red', rect_obj, width=3)
                        if mouse_sel:
                            self.selected_pair = [pc_i, pc_j]
                            self.selected_mouse_pos = mpos

                smpos = self.selected_mouse_pos
                if left <= smpos[0] < left + self.cw and top <= smpos[1] < top + self.ch and \
                        ri != ci:
                    rect_obj = pygame.Rect(left, top, self.cw, self.ch)
                    pygame.draw.rect(surface, '#f8d210', rect_obj, width=3)
                    if mouse_sel:
                        updates.add(self.label + ' PCA Pair')
                        updates.add(CONTROL)

        self.header.draw(surface)
        update_rect = pygame.Rect(self.x, self.y, self.w, self.h)
        if show_update:
            pygame.draw.rect(surface, 'green', update_rect, width=3)
        pygame.display.update(update_rect)

        return updates
