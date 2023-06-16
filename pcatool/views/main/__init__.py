from pcatool.views.main.controls import ControlView
from pcatool.views.main.pca_grid import PCAGridView
from pcatool.views.main.pca_pair import PCAPairView
from pcatool.views.main.menubar import MenuBarView

# Main View Class
from pcatool.commonlibs import \
    pd, Path, pygame, os, Dict, FPS, time, datetime, \
    BIN_FEATURES

from pcatool.views import \
    TARGET_PCA_GRID, DEID_PCA_GRID, TARGET_PCA_PAIR, \
    DEID_PCA_PAIR, CONTROL, MENUBAR
from pcatool.pca import PCAWrap, FeatureSet, fset_map
from pcatool.pca_plots import plot_all_components
from pcatool.colors import target_color, deid_color, \
    target_header_color, deid_header_color, \
    create_data_colors
from pcatool.views.main.menubar import \
    HIGHLIGHT_ALL_PAIRS, MENU, SCREENSHOT
from pcatool.fonts import get_font_map

import pcatool.util as util


def pygame_gui(width: int,
               height: int,
               output_path: Path,
               tar_data: pd.DataFrame,
               deid_data: pd.DataFrame,
               deid_data_path: Path,
               target_data_path: Path,
               schema: Dict[str, str],
               feature_set: FeatureSet,
               data_dictionary: Dict[str, any],
               screeshots_path: Path,
               threaded: bool = True) -> bool:

    fset = feature_set

    w, h = width, height
    font_map = get_font_map()
    features = fset_map[fset]
    if features is None:
        features = list(tar_data.columns)
    features = set(deid_data.columns).intersection(set(features))
    features = list(set(tar_data.columns).intersection(features))
    tar_data = tar_data[features]
    deid_data = deid_data[features]

    tar_data, _ = util.validate(tar_data, data_dictionary, features)
    deid_data, _ = util.validate(deid_data, data_dictionary, features)

    features = list(set(tar_data.columns).intersection(set(deid_data.columns)))
    features = [f for f in data_dictionary.keys() if f in features]
    tar_data = tar_data.reindex(columns=features)
    deid_data = deid_data.reindex(columns=features)

    t_binned = util.bin_target_data(tar_data.copy(), BIN_FEATURES)
    d_binned = util.bin_synthetic_data(deid_data.copy(),
                                       tar_data.copy(),
                                       t_binned.copy(), BIN_FEATURES)
    # print('TAR:')
    # for c in t_binned.columns:
    #     uv = t_binned[c].unique().tolist()
    #     if len(uv) < 20:
    #         print(c, uv)
    # print()
    # print('DEID:')
    # for c in d_binned.columns:
    #     uv = d_binned[c].unique().tolist()
    #     if len(uv) < 20:
    #         print(c, uv)

    if 'DENSITY' in features:
        t_binned = util.bin_density(t_binned, data_dictionary)
        d_binned = util.bin_density(d_binned, data_dictionary)
    n_components = min(5, len(features))

    # target data pca wrapper
    pca = PCAWrap(deid_data, tar_data, schema, features, n_components, None)
    pca.pca()
    # deid data pca wrapper
    # d_pca = PCAWrap(deid_data, tar_data, schema, features, 'deid', n_components, None)
    # d_pca.pca()

    t_comps_dir = Path(output_path, 'target_comps')
    d_comps_dir = Path(output_path, 'deid_comps')
    for d in [t_comps_dir, d_comps_dir]:
        if not d.exists():
            os.mkdir(d)

    s_time = time.time()

    #
    # print('Plotting all components...')
    for pca_df, d, clr in [(pca.t_pdf, t_comps_dir, target_color), (pca.d_pdf, d_comps_dir, deid_color)]:
        plot_all_components(pca_df, d, color=clr, threaded=threaded, dpi=50)
    # print('Took Time: ', time.time() - s_time)

    s_time = time.time()
    # print('Coloring Each Values')
    if 'INDP' in features:
        tar_data_no_indp = t_binned.drop(columns=['INDP'])
        deid_data_no_indp = d_binned.drop(columns=['INDP'])
    else:
        tar_data_no_indp = t_binned
        deid_data_no_indp = d_binned
    t_clrs, d_clrs, clr_map = create_data_colors(tar_data_no_indp, deid_data_no_indp)
    # print('Coloring Took Time: ', time.time() - s_time)

    # menu bar view position and size
    mb_h = 40
    e_h = h - mb_h # effective height for other views
    m_view_info = (0, 0, w, mb_h, deid_data_path, font_map)

    # target pca grid position and size
    t_pca_g_info = (0, mb_h, w//3 + 3, e_h//2, pca.t_pdf, t_comps_dir,
                    target_data_path.stem,
                    font_map,
                    'Target', 'TARGET DATA', target_header_color)
    # deid pca grid position and size
    d_pca_g_info = (0, mb_h + e_h//2, w//3 + 3, e_h//2, pca.d_pdf, d_comps_dir,
                    deid_data_path.stem,
                    font_map,
                    'Deidentified', 'DEIDENTIFIED DATA', deid_header_color)

    # target pca pair view position and size
    t_pca_view_info = (w//3, mb_h, w//3, e_h//2,
                       t_binned, pca.t_pdf.copy(),
                       pca.axis_range,
                       t_clrs,
                       target_color,
                       Path(output_path, 'target_temp'),
                       font_map,
                       'Target', 'TARGET', target_header_color)
    # deid pca pair view position and size
    d_pca_view_info = (w//3, mb_h + e_h//2, w//3, e_h//2,
                       d_binned, pca.d_pdf.copy(),
                       pca.axis_range,
                       d_clrs,
                       deid_color,
                       Path(output_path, 'deid_temp'), font_map, 'Deidentified',
                       'DEIDENTIFIED', deid_header_color)

    # control view position and size
    c_view_info = (w//3 * 2, mb_h, w//3, e_h,
                   tar_data_no_indp,
                   deid_data_no_indp,
                   clr_map,
                   data_dictionary,
                   pca.comp_df,
                   fset.value,
                   font_map)

    # menu bar view
    m_view = MenuBarView(*m_view_info)

    # target pca grid
    t_pca_g = PCAGridView(*t_pca_g_info)
    # deid pca grid
    d_pca_g = PCAGridView(*d_pca_g_info)

    # target pca pair view
    t_pca_view = PCAPairView(*t_pca_view_info)
    # deid pca pair view
    d_pca_view = PCAPairView(*d_pca_view_info)

    # feature control view
    c_view = ControlView(*c_view_info)
    # print('Hello')
    # pygame.display.set_caption(f'PCA-{DATA_PATH.stem.upper()}-{data_type}-{feature_type}')
    clock = pygame.time.Clock()
    flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    surface = pygame.display.set_mode((w, h), flags)
    exit_program = False
    stop_program = False
    mouse_pos = (0, 0)
    mouse_sel = False
    showfps = True
    default_highlighted_grid = m_view.btns[HIGHLIGHT_ALL_PAIRS].selected
    surface.fill('white')
    surface_rect = pygame.Rect(0, 0, w, h)
    t_pca_g.draw(surface, mouse_pos, mouse_sel,
                                 t_pca_view.highlighted_changed)
    new_mouse_pos = (mouse_pos[0], mouse_pos[1] - e_h // 2)
    d_pca_g.draw(surface, new_mouse_pos, mouse_sel,
                                 d_pca_view.highlighted_changed)
    t_pca_view.draw(surface, t_pca_g.selected_pair,
                    c_view.f_control.selected, t_comps_dir,
                    default_highlighted_grid, mouse_pos,
                    mouse_sel)
    d_pca_view.draw(surface, d_pca_g.selected_pair,
                    c_view.f_control.selected, d_comps_dir,
                    default_highlighted_grid, new_mouse_pos,
                    mouse_sel)
    c_view.draw(surface)
    m_view.draw(surface)
    pygame.display.update(surface_rect)
    view_names = {t_pca_g: TARGET_PCA_GRID,
                  t_pca_view: TARGET_PCA_PAIR,
                  d_pca_g: DEID_PCA_GRID,
                  d_pca_view: DEID_PCA_PAIR,
                  c_view: CONTROL,
                  m_view: MENUBAR}

    name_to_views = {v: k for k, v in view_names.items()}
    views = [t_pca_g, t_pca_view, d_pca_g, d_pca_view, c_view, m_view]
    updates_history = dict()
    counter = 0

    while not (exit_program or stop_program):
        updates = set()
        scroll = 0
        time_delta = clock.tick(FPS) / 1000.0
        # surface.fill('white')
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                exit_program = True
            if e.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
                updates = updates.union({k for k, v in name_to_views.items()
                               if v.point_in_view(mouse_pos)})
            if e.type == pygame.MOUSEBUTTONDOWN:
                mouse_sel = True
                updates = updates.union({k for k, v in name_to_views.items()
                               if v.point_in_view(mouse_pos)})
            if e.type == pygame.MOUSEBUTTONUP:
                mouse_sel = False
            if e.type == pygame.MOUSEWHEEL:
                scroll = e.y
                updates.add(CONTROL)

            new_updates = c_view.click(e)
            new_updates = set(new_updates).union(set(m_view.click(e)))
            if len(new_updates) > 0:
                updates = updates.union(new_updates)

        # with mouse_selection
        k = len(updates)
        i = 0
        updates = list(updates)

        # print(f'--BEFORE {updates}')
        while i < k:
            # print(updates)
            u = updates[i]
            updates_history[u] = 3
            new_updates = set()

            if u == TARGET_PCA_PAIR:
                new_updates_1 = t_pca_view.draw(surface, t_pca_g.selected_pair,
                                              c_view.f_control.selected, t_comps_dir,
                                              m_view.btns[HIGHLIGHT_ALL_PAIRS].selected,
                                              mouse_pos,
                                              mouse_sel)
                new_mouse_pos = (mouse_pos[0], mouse_pos[1] + e_h//2)
                new_updates_2 = d_pca_view.draw(surface, d_pca_g.selected_pair,
                                                c_view.f_control.selected, d_comps_dir,
                                                m_view.btns[HIGHLIGHT_ALL_PAIRS].selected,
                                                new_mouse_pos,
                                                mouse_sel)
                new_updates = new_updates_1.union(new_updates_2)
                # print('Target PCA PAIR', new_updates)
            elif u == DEID_PCA_PAIR:
                new_updates_1 = d_pca_view.draw(surface, d_pca_g.selected_pair,
                                              c_view.f_control.selected, d_comps_dir,
                                                m_view.btns[HIGHLIGHT_ALL_PAIRS].selected,
                                              mouse_pos,
                                              mouse_sel)
                new_mouse_pos = (mouse_pos[0], mouse_pos[1] - e_h//2)
                new_updates_2 = t_pca_view.draw(surface, t_pca_g.selected_pair,
                                                c_view.f_control.selected, t_comps_dir,
                                                m_view.btns[HIGHLIGHT_ALL_PAIRS].selected,
                                                new_mouse_pos,
                                                mouse_sel)
                new_updates = new_updates_1.union(new_updates_2)
                # print('DEID PCA PAIR', new_updates)
            elif u == TARGET_PCA_GRID:
                new_updates_1 = t_pca_g.draw(surface, mouse_pos, mouse_sel,
                                             t_pca_view.highlighted_changed)
                new_mouse_pos = (mouse_pos[0], mouse_pos[1] + e_h // 2)
                new_updates_2 = d_pca_g.draw(surface, new_mouse_pos, mouse_sel,
                                             d_pca_view.highlighted_changed)
                new_updates = new_updates_1.union(new_updates_2)
            elif u == DEID_PCA_GRID:
                new_updates_1 = d_pca_g.draw(surface, mouse_pos, mouse_sel,
                                             d_pca_view.highlighted_changed)
                new_mouse_pos = (mouse_pos[0], mouse_pos[1] - e_h // 2)
                new_updates_2 = t_pca_g.draw(surface, new_mouse_pos, mouse_sel,
                                             t_pca_view.highlighted_changed)
                new_updates = new_updates_1.union(new_updates_2)
            elif u == CONTROL:
                t_ids = None
                d_ids = None
                if t_pca_view.selected_ids_changed:
                    t_ids = t_pca_view.selected_pair_ids
                    t_pca_view.selected_ids_changed = False
                if d_pca_view.selected_ids_changed:
                    d_ids = d_pca_view.selected_pair_ids
                    d_pca_view.selected_ids_changed = False
                if t_ids is not None and d_ids is None:
                    d_ids = []
                if d_ids is not None and t_ids is None:
                    t_ids = []

                c_view.update(scroll,
                                  t_ids,
                                  d_ids)
                c_view.draw(surface)
            elif u == MENUBAR:
                m_view.draw(surface)

            updates = updates + list(new_updates)
            # print('Final updates: ', updates)
            k = len(updates)
            i += 1
        # last update before after mouse leaves
        if counter % 5 == 0:
            for k in list(updates_history.keys()):
                u = k
                updates_history[u] -= 1
                if updates_history[u] == 0:
                    del updates_history[u]
                nu = set()
                if u == TARGET_PCA_PAIR:
                    nu_1 = t_pca_view.draw(surface, t_pca_g.selected_pair,
                                    c_view.f_control.selected, t_comps_dir,
                                    m_view.btns[HIGHLIGHT_ALL_PAIRS].selected,
                                    mouse_pos,
                                    mouse_sel, False)
                    new_mouse_pos = (mouse_pos[0], mouse_pos[1] + e_h//2)
                    nu_2 = d_pca_view.draw(surface, d_pca_g.selected_pair,
                                    c_view.f_control.selected, d_comps_dir,
                                    m_view.btns[HIGHLIGHT_ALL_PAIRS].selected,
                                    new_mouse_pos,
                                    mouse_sel, False)
                    nu = nu_1.union(nu_2)
                elif u == DEID_PCA_PAIR:
                    nu_1 = d_pca_view.draw(surface, d_pca_g.selected_pair,
                                    c_view.f_control.selected, d_comps_dir,
                                    m_view.btns[HIGHLIGHT_ALL_PAIRS].selected,
                                    mouse_pos,
                                    mouse_sel, False)
                    new_mouse_pos = (mouse_pos[0], mouse_pos[1] - e_h//2)
                    nu_2 = t_pca_view.draw(surface, t_pca_g.selected_pair,
                                    c_view.f_control.selected, t_comps_dir,
                                    m_view.btns[HIGHLIGHT_ALL_PAIRS].selected,
                                    new_mouse_pos,
                                    mouse_sel, False)
                    nu = nu_1.union(nu_2)
                elif u == TARGET_PCA_GRID:
                    nu_1 = t_pca_g.draw(surface, mouse_pos, mouse_sel, False, False)
                    new_mouse_pos = (mouse_pos[0], mouse_pos[1] + e_h // 2)
                    nu_2 = d_pca_g.draw(surface, new_mouse_pos, mouse_sel, False, False)
                    nu = nu_1.union(nu_2)
                elif u == DEID_PCA_GRID:
                    nu_1 = d_pca_g.draw(surface, mouse_pos, mouse_sel, False, False)
                    new_mouse_pos = (mouse_pos[0], mouse_pos[1] - e_h // 2)
                    nu_2 = t_pca_g.draw(surface, new_mouse_pos, mouse_sel, False, False)
                    nu = nu_1.union(nu_2)
                elif u == CONTROL:
                    t_ids = None
                    d_ids = None
                    if t_pca_view.selected_ids_changed:
                        t_ids = t_pca_view.selected_pair_ids
                        t_pca_view.selected_ids_changed = False
                    if d_pca_view.selected_ids_changed:
                        d_ids = d_pca_view.selected_pair_ids
                        d_pca_view.selected_ids_changed = False
                    if t_ids is not None and d_ids is None:
                        d_ids = []
                    if d_ids is not None and t_ids is None:
                        t_ids = []

                    c_view.update(scroll,
                                  t_ids,
                                  d_ids)
                    c_view.draw(surface, False)
                elif u == MENUBAR:
                    m_view.draw(surface, False)

                for u in nu:
                    if u not in updates_history:
                        updates_history[u] = 3
                    else:
                        updates_history[u] += 3

        if m_view.btns[MENU].selected:
            stop_program = True
        if m_view.btns[SCREENSHOT].selected:
            now_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            im_path = Path(screeshots_path, f'ss_{now_time}.jpg')
            pygame.image.save(surface, im_path)
            m_view.btns[SCREENSHOT].selected = False
        # fc_view.update(pca_view.selected_pair_ids, scroll)
        # fc_view.draw(surface)
        # pca_g.draw(surface, pca.t_pdf, mouse_pos, mouse_sel)
        # selected_pca_pair = pca_g.selected_pair
        # pca_view.draw(surface, selected_pca_pair,
        #               fc_view.selected_btn, output_path, mouse_pos,
        #               mouse_sel)
        # if showfps:
        #     font = pygame.font.SysFont("comicsansms", 15)
        #     text = font.render(f"FPS: {clock.get_fps():.2f}",
        #                        True, 'black')
        #     text_rect = text.get_rect()
        #     text_rect.topleft = (w - text_rect.w, 0)
        #     pygame.draw.rect(surface, 'white', text_rect)
        #     surface.blit(text, (w - text_rect.w, 0))
        #     pygame.display.update(text_rect)
        clock.tick(FPS)
        counter += 1
        counter %= (FPS * 2)

    return exit_program