from pcatool.commonlibs import pd, random, BIN_FEATURES

target_color = "#06c278"
deid_color = "#068fc2"
target_header_color = "#048754"
deid_header_color = "#046487"


num_colors = 200

custom_colors = ["#d62828", "#3a0ca3", "#f77f00", "#0fa3b1", "#548c2f",
                 "#0353a4", "#3d405b", "#e36414", "#800e13", "#69585f",
                 "#5e503f"]

colors = ["#"+''.join([random.choice('0123456789ABCDEF')
                       for j in range(6)])
           for i in range(num_colors - len(custom_colors))]

colors = custom_colors + colors


def create_data_colors(target: pd.DataFrame, deid: pd.DataFrame):
    target = target.copy()
    deid = deid.copy()
    all_c_map = dict()
    temp_colors = colors.copy()
    for col in target.columns.tolist():
        if col in BIN_FEATURES:
            continue
        if col != 'DENSITY':
            t_u_vals = target[col].unique().tolist()
            d_u_vals = deid[col].unique().tolist()
        else:
            target[col] = target[col].astype(int)
            deid[col] = deid[col].astype(int)
            t_u_vals = target[col].unique().tolist()
            d_u_vals = deid[col].unique().tolist()
        u_vals = list(set(t_u_vals + d_u_vals))
        if 'N' in u_vals:
            u_vals.remove('N')
            u_vals = sorted(u_vals)
            u_vals = ['N'] + u_vals
        if len(u_vals) > num_colors:
            temp_colors = temp_colors + ['#808080'] * ((len(u_vals) - num_colors) + 1)
        # print(col, len(temp_colors), len(u_vals))
        c_map = {v: temp_colors[i+1] if v != 'N' else temp_colors[0]
                 for i, v in enumerate(u_vals)}
        target[col + '_clr'] = target[col].map(c_map)
        deid[col + '_clr'] = deid[col].map(c_map)
        all_c_map[col] = {str(k): v for k, v in c_map.items()}
    t_clr = target[[c for c in target.columns.tolist()
                    if c.endswith('clr')]]
    d_clr = deid[[c for c in deid.columns.tolist()
                    if c.endswith('clr')]]
    return t_clr, d_clr, all_c_map
