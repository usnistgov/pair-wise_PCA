import pygame.font

from pcatool.commonlibs import List, np, math, Dict
import pandas as pd
from pathlib import Path
import json
import os


def load(data_path: Path, schema_path: Path):
    data = pd.read_csv(data_path)
    with open(schema_path, 'r') as f:
        schema = json.load(f)['schema']

    return data, schema


def json_load(path: Path):
    with open(path, 'r') as f:
        return json.load(f)


def create_path(path: Path):
    if not path.exists():
        os.mkdir(path)


def min_max_scaling(series, min_val=None, max_val=None):
    if min_val is None:
        min_val = series.min()
    if max_val is None:
        max_val = series.max()

    return (series - min_val) / (max_val - min_val)


def bin_target_data(data: pd.DataFrame, features: List[str]) -> pd.DataFrame:
    for c in features:
        if c not in data.columns:
            continue
        if c == 'POVPIP':
            na_mask = data[data[c].isin(['N', 501])].index
            nna_mask = data[~data[c].isin(['N', 501])].index
        else:
            na_mask = data[data[c].isin(['N'])].index
            nna_mask = data[~data[c].isin(['N'])].index  # not na mask
        d_temp = pd.DataFrame(pd.to_numeric(data.loc[nna_mask, c]).astype(int), columns=[c])
        data.loc[nna_mask, c + '_bin'] = d_temp[c]\
            .rank(pct=True).apply(lambda x: int(20 * x) if x < 1 else 19)
        data.loc[nna_mask, c + '_bin'] = data.loc[nna_mask, c + '_bin']\
            .astype(int)\
            .astype(str)
        data.loc[na_mask, c + '_bin'] = data.loc[na_mask, c].astype(str)
    return data


def bin_synthetic_data(data: pd.DataFrame,
                       target_data: pd.DataFrame,
                       binned_target_data: pd.DataFrame,
                       features: List[str]) -> pd.DataFrame:
    td = target_data
    btd = binned_target_data

    for c in features:
        bc = c + '_bin'
        if c not in data.columns:
            continue
        if c == 'POVPIP':
            na_mask = data[data[c].isin(['N', 501])].index
            nna_mask = data[~data[c].isin(['N', 501])].index
            btd_nna_mask = btd[~btd[c].isin(['N', 501])].index
        else:
            na_mask = data[data[c].isin(['N'])].index
            nna_mask = data[~data[c].isin(['N'])].index  # not na mask
            btd_nna_mask = btd[~btd[c].isin(['N'])].index  # not na mask

        d_temp = pd.DataFrame(pd.to_numeric(data.loc[nna_mask, c]).astype(int), columns=[c])
        f_data = d_temp.copy()
        f_data[bc] = f_data[c]
        data[bc] = data[c].astype(str)
        max_b = 0
        btd_nna = btd.loc[btd_nna_mask, [bc, c]]\
            .apply(pd.to_numeric, errors='coerce')\
            .astype(int)
        last_bin = btd_nna.sort_values(by=[bc])[bc].values[-1]
        print(f'Bin {c}, Last Bin {last_bin}')
        for b, g in btd_nna.sort_values(by=[bc]).groupby(bc):
            t_bp = pd.DataFrame(pd.to_numeric(td.loc[g.index, c]).astype(int), columns=[c])

            if b == 0:
                max_b = max(t_bp[c])
                max(f_data[(d_temp[c] <= max_b)][c])
                # print(f'-- {b} - {min(t_bp[c])} - {max(t_bp[c])} - {max(f_data[(d_temp[c] <= max_b)][c])} - {0}')
                f_data.loc[(d_temp[c] <= max_b), bc] = str(b)
            elif b != last_bin:
                min_b = max_b
                max_b = max(t_bp[c])
                # print(f'-- {b} - {min(t_bp[c])} - {max(t_bp[c])} - '
                #       f'{max(f_data[(d_temp[c] > min_b) & (d_temp[c] <= max_b)][c])} - {1}')
                f_data.loc[(d_temp[c] > min_b) & (d_temp[c] <= max_b), bc] = str(b)
            else:
                min_b = max_b
                # print(f'-- {b} - {min(t_bp[c])} - {max(t_bp[c])} - {max(f_data[(d_temp[c] > min_b)][c])} - {2}')
                f_data.loc[(d_temp[c] > min_b), bc] = str(b)

        data.loc[nna_mask, bc] = f_data[bc]
        data.loc[na_mask, bc] = data.loc[na_mask, c].astype(str)
        print(f'Finished binning {c}', f'Bins: {len(data[bc].unique())}')
    return data


def subpath(path: Path, level: int = 3):
    p = path
    parts = p.parts
    return Path(*parts[-level:]) \
        if len(p.parts) > level else p


def fix_text_width(text: str,
                   font: pygame.font.Font,
                   max_width: int,
                   trim_from_back: bool = True) -> str:

    if max_width <= 0 or len(text) == 0:
        return text

    trim_fn = lambda txt, size: txt[:-size] if trim_from_back else txt[size:]

    is_fixed = False
    break_count = 0
    break_after = 100
    while not is_fixed and len(text) > 0:
        if break_count > break_after:
            break
        text_surface = font.render(text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(0, 0))
        cut_by = 2
        if text_rect.w > max_width:
            if len(text) > cut_by:
                text = trim_fn(text, cut_by)
            else:
                text = trim_fn(text, 1)
        else:
            is_fixed = True
        break_count += 1
    return text


def bin_density(data: pd.DataFrame, data_dict: Dict, update: bool = True) -> pd.DataFrame:
    """
    data: Data containing density feature
    data_dict: Dictionary containing values range for density feature
    update: if True, update the input data's density feature and return
            else, create two new columns: binned_density and bin_range
            and return the data
    """
    def get_bin_range_log(x):
        for i, v in enumerate(bins):
            if i == x:
                return [round(v, 2), round(bins[i + 1], 2)]
    d = data
    dd = data_dict
    base = 10
    # we remove first 8 bins from this bins list, and prepend
    # two bins. So effective bins are 12. This is done to bottom
    # code density category for the PUMAs with small density.
    n_bins = 20  # number of bins
    # max of range
    n_max = dd['DENSITY']['values']['max'] + 500

    bins = np.logspace(start=math.log(10, base), stop=math.log(n_max, base), num=n_bins+1)
    # remove first 8 bins and prepend two new bins
    bins = [0, 150] + list(bins[8:])
    # print('Bins', bins)
    # print('Densities', d['DENSITY'].unique().tolist())
    n_bins = len(bins)  # update number of bins to effective bins
    labels = [i for i in range(n_bins-1)]

    # top code values to n_max and bottom code values to 0 in the data
    d.loc[d['DENSITY'] < 0, 'DENSITY'] = float(0)
    d.loc[d['DENSITY'] > n_max, 'DENSITY'] = float(n_max) - 100

    if update:
        d['DENSITY'] = pd.cut(d['DENSITY'], bins=bins, labels=labels)
        d['DENSITY'] = d['DENSITY'].apply(lambda x: get_bin_range_log(x)[0])
        return d
    else:
        d['binned_density'] = pd.cut(d['DENSITY'], bins=bins, labels=labels)

        d['bin_range'] = d['binned_density'].apply(lambda x: get_bin_range_log(x)[0])
        return d


def validate(data: pd.DataFrame,
             data_dict: Dict,
             features: List[str]):
    """
    Removes all columns with the out of bound values.
    """

    validation_log = dict()
    sd = data.copy()
    vob_features = []  # value out of bound
    nan_df = sd[sd.isna().any(axis=1)]
    nan_features = []
    if len(nan_df):
        nan_features = sd.columns[sd.isna().any()].tolist()
        validation_log['nans'] = {
            "nan_records": len(nan_df),
            "nan_features": nan_features
        }
        sd = sd.dropna()

    for f in features:
        # check feature has out of bound value
        f_data = data_dict[f]
        has_nan = f in nan_features
        has_N = 'N' in f_data['values'] if f != 'INDP' else True
        f_vals = f_data['values'] if "values" in f_data else []

        if 'min' in f_vals:
            fd = sd[[f]].copy()
            mask = fd[fd[f] != 'N'].index if has_N else fd.index
            fd.loc[mask, f] = pd.to_numeric(fd.loc[mask, f], errors="coerce")
            nans = fd[fd.isna().any(axis=1)]
            if len(nans):
                vob_vals = list(set(data.loc[nans.index, f].values.tolist()))
                vob_features.append((f, vob_vals))
                # console_out(f'Value out of bound for feature {f}, '
                #       f'out of bound values: {vob_vals}. '
                #             f'Dropping feature from evaluation.')

            mask = sd[sd[f] != 'N'].index if has_N else sd.index

            if f in ['PINCP'] and not len(nans):
                sd.loc[mask, f] = pd.to_numeric(sd.loc[mask, f])
                sd.loc[mask, f] = sd.loc[mask, f].astype(float)
            elif not len(nans):
                sd.loc[mask, f] = pd.to_numeric(sd.loc[mask, f])
                sd.loc[mask, f] = sd.loc[mask, f].astype(int)
        elif f == 'PUMA':
            # values intersection
            f_unique = sd['PUMA'].unique().tolist()
            v_intersect = set(f_unique).intersection(set(f_vals))
            if len(v_intersect) < len(f_unique):
                vob_vals = list(set(f_unique).difference(v_intersect))
                vob_features.append((f, vob_vals))
        else:
            u_vals = sd[f].unique().tolist()
            if 'N' not in u_vals:
                sd[f] = sd[f].astype(int)
            fd = sd[[f]].copy()
            mask = fd[fd[f] != 'N'].index if has_N else fd.index
            fd.loc[mask, f] = pd.to_numeric(fd.loc[mask, f], errors="coerce")
            nans = fd[fd.isna().any(axis=1)]
            vob_vals = []
            if len(nans):
                vob_vals.extend(list(set(data.loc[nans.index, f].values.tolist())))
                fd = fd.dropna()

            mask = fd[fd[f] != 'N'].index if has_N else fd.index
            fd.loc[mask, f] = fd.loc[mask, f].astype(int)

            if f != 'INDP':
                real_vals = list(f_vals.keys())
                if 'N' in real_vals:
                    real_vals.remove('N')
                f_unique = set(fd.loc[mask, f].unique().tolist())
                real_vals = [int(v) for v in real_vals]
                v_intersect = set(f_unique).intersection(set(real_vals))
                if len(v_intersect) < len(f_unique):
                    vob_vals.extend(list(set(f_unique).difference(v_intersect)))

            if len(vob_vals):
                vob_features.append((f, vob_vals))
            else:
                mask = sd[sd[f] != 'N'].index if has_N else sd.index
                sd.loc[mask, f] = pd.to_numeric(sd.loc[mask, f])
                sd.loc[mask, f] = sd.loc[mask, f].astype(int)

        if has_N:
            sd[f] = sd[f].astype(object)

        if len(vob_features):
            last_vob_f, vob_vals = vob_features[-1]

            if last_vob_f == f:
                sd = sd.loc[:, sd.columns != f]
                if has_nan:
                    vob_features = (last_vob_f, ['nan'] + vob_vals)

    validation_log['values_out_of_bound'] = dict(vob_features)
    return sd, validation_log
