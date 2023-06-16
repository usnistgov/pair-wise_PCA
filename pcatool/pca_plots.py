from pcatool.commonlibs import time, np, os, product, List
from pathlib import Path
from multiprocessing import Pool

import matplotlib
import matplotlib.pyplot as plt
# matplotlib.use("Agg")
# matplotlib.style.use(["seaborn-deep", "seaborn-notebook"])
import matplotlib.backends.backend_agg as agg

x_min = -0.02
x_max = 1.02
y_min = -0.02
y_max = 1.02


def plot_all_components(data, path, color='b',
                        transparent=False, threaded=True, dpi=10):
    max_avail_threads = max(os.cpu_count() - 2, 1)
    if threaded:
        threads = min(max_avail_threads, 2)
    else:
        threads = 1

    d = data
    s_t = time.time()

    if threads - 1 > 1:  # if more threads than this one
        process_pool = []
        args = []
        all_col_pairs = product(d.columns, d.columns)
        all_col_pairs = [x for x in all_col_pairs if x[0] != x[1]]
        chunks = np.array_split(all_col_pairs, threads-1)
        # divide into threads number of chunks
        for chunk in chunks:
            args.append((data, path, chunk, color, transparent))

        pool = Pool(processes=threads)
        res = pool.starmap(plot_component_pairs, args)

        # split data into chunks
    else:
        for ri, pc_i in enumerate(d.columns):
            for ci, pc_j in enumerate(d.columns):
                # x_min = axis_range.loc['min', pc_j]
                # x_max = axis_range.loc['max', pc_j]
                # y_min = axis_range.loc['min', pc_i]
                # y_max = axis_range.loc['max', pc_i]
                fig = plt.figure(figsize=(10, 10), dpi=dpi)
                ax = fig.add_axes([0, 0, 1, 1])
                ax.scatter(d[pc_j], d[pc_i], color=color)
                ax.set_xlim([x_min, x_max])
                ax.set_ylim([y_min, y_max])
                plt.savefig(Path(path, f'{pc_i}_{pc_j}.png'),
                            pad_inches=0.0, transparent=transparent)
                plt.close(fig)
    print(f'Plotting took {time.time() - s_t:.2f} seconds.')
    return []


def plot_all_colored(data, data_colors, path, color='b',
                    transparent=False, dpi=10):
    d = data
    for ri, pc_i in enumerate(d.columns):
        for ci, pc_j in enumerate(d.columns):
            fig = plt.figure(figsize=(10, 10), dpi=dpi)
            ax = fig.add_axes([0, 0, 1, 1])
            ax.scatter(d[pc_j], d[pc_i], c=data_colors)
            ax.set_xlim([x_min, x_max])
            ax.set_ylim([x_min, x_max])
            plt.savefig(Path(path, f'{pc_i}_{pc_j}.png'),
                        pad_inches=0.0, transparent=transparent)
            plt.close(fig)
    return []


def plot_component_pairs(data, path, column_pairs, color: str = 'r',
                         transparent: bool = True):
    for c1, c2 in column_pairs:
        plot_single_component(data, path, c1, c2, color, transparent, dpi=10)


def plot_single_component(data, path, col1, col2, color: str = 'r',
                          transparent: bool = True, dpi=50):
    d = data
    c1, c2 = col1, col2
    fig = plt.figure(figsize=(10, 10), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.scatter(d[c2], d[c1], color=color)
    ax.set_xlim([x_min, x_max])
    ax.set_ylim([x_min, x_max])
    if path.is_dir():
        im_path = Path(path, f'{c1}_{c2}.png')
    else:
        im_path = path
    parent = im_path.parent
    if not parent.exists():
        parent.mkdir(parents=True)
    ax.tick_params(axis='both', which='major', labelsize=20)
    ax.tick_params(axis='both', which='minor', labelsize=20)
    plt.savefig(im_path, pad_inches=0.0, transparent=transparent)
    plt.close(fig)
    return im_path


def plot_single_colored(data, clr_data, path, col1, col2, color: str = 'r',
                          transparent: bool = True, dpi=50):
    d = data
    c1, c2 = col1, col2
    fig = plt.figure(figsize=(10, 10), dpi=dpi)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.scatter(d[c2], d[c1], c=clr_data, alpha=0.5)
    ax.set_xlim([x_min, x_max])
    ax.set_ylim([x_min, x_max])
    if path.is_dir():
        im_path = Path(path, f'{c1}_{c2}.png')
    else:
        im_path = path
    parent = im_path.parent
    if not parent.exists():
        parent.mkdir(parents=True)
    plt.savefig(im_path,
                pad_inches=0.0, transparent=transparent)
    plt.close(fig)
    return im_path

# def new_plot_single_component(data, path, col1, col2):
#     d = data
#     c1, c2 = col1, col2
#     fig = plt.figure(figsize=(10, 10), dpi=50)
#     ax = fig.add_axes([0, 0, 1, 1])
#
#     ax.scatter(d[c2], d[c1], color='r')
#     ax.set_xlim([-0.02, 1.02])
#     ax.set_ylim([-0.02, 1.02])
#     if path.is_dir():
#         im_path = Path(path, f'{c1}_{c2}.png')
#     else:
#         im_path = path
#     parent = im_path.parent
#     if not parent.exists():
#         parent.mkdir(parents=True)
#     plt.savefig(im_path,
#                 pad_inches=0.0, transparent=True)
#     canvas = agg.FigureCanvasAgg(fig)
#     canvas.draw()
#     renderer = canvas.get_renderer()
#     raw_data = renderer.tostring_argb()
#     size = canvas.get_width_height()
#     plt.close(fig)
#     print('Done', 'Saved to', im_path)
#     return raw_data, size, 'ARGB'