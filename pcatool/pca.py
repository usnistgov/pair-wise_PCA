from pcatool.commonlibs import List, Dict
import pandas as pd
import numpy as np
from enum import Enum
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import multiprocessing as mp
from pcatool.util import min_max_scaling


def transform(data: pd.DataFrame, schema):
    # replace categories with codes
    # replace N: NA with -1 for categoricals
    # replace N: NA with mean for numericals
    data = data.copy()
    for c in data.columns.tolist():
        desc = schema[c]
        if "values" in desc:
            if "has_null" in desc:
                null_val = desc["null_value"]
                data[c] = data[c].replace(null_val, -1)
        elif "min" in desc:
            if "has_null" in desc:
                null_val = desc["null_value"]
                nna_mask = data[~data[c].isin(['N'])].index  # not na mask
                if c == 'PINCP':
                    data[c] = data[c].replace(null_val, 9999999)
                elif c == 'POVPIP':
                    data[c] = data[c].replace(null_val, 999)
        if c == 'PUMA':
            data[c] = data[c].astype(pd.CategoricalDtype(desc["values"])).cat.codes
            if "N" in desc['values']:
                data[c] = data[c].replace(0, -1)
        else:
            data[c] = pd.to_numeric(data[c])
    return data


class FeatureSet(Enum):
    all = 'all'
    demographic = 'demographic'
    industry = 'industry'
    family = 'family'

# rev_fset = {v: k for k, v in FeatureSet.__dict__.items() if not k.startswith('__')}


Demographic_focused = ["SEX", "MSP", "RAC1P", "OWN_RENT", "PINCP_DECILE", "EDU",
                       "AGEP", "HOUSING_TYPE", "DVET", "DEYE"]

Industry_focused = ["SEX", "MSP", "RAC1P", "OWN_RENT", "PINCP_DECILE",
                    "EDU", "HISP", "PUMA", "INDP_CAT"]

Family_focused = ["SEX", "MSP", "RAC1P", "OWN_RENT", "PINCP_DECILE",
                  "HISP", "PUMA", "AGEP", "NOC", "NPF", "POVPIP"]

fset_map = {
    FeatureSet.all: None,
    FeatureSet.demographic: Demographic_focused,
    FeatureSet.industry: Industry_focused,
    FeatureSet.family: Family_focused
}


def get_index(merge_df, target_chunk) -> List[int]:
    idx = []
    for i, t_r in target_chunk.iterrows():
        for j, m_r in merge_df.iterrows():
            if t_r.equals(m_r):
                idx.append(i)
                break
    return idx


class PCAWrap:
    RACE_SPLIT = ['AGEP', 'RAC1P', 'MSP', 'SEX', 'HOUSING_TYPE', 'OWN_RENT', 'DVET', 'DEYE']
    RACE_SPLIT_EDU_PINCP = ['AGEP', 'RAC1P', 'MSP', 'SEX', 'HOUSING_TYPE', 'OWN_RENT',
                            'DVET', 'PINCP_DECILE', 'EDU']

    def __init__(self,
                 data: pd.DataFrame,
                 target_data: pd.DataFrame,
                 schema: Dict,
                 features: List[str],
                 components: int = 5, comps_df=None):
        self.feature_set = features
        self.deid_d = data[self.feature_set]
        self.tar_d = target_data[self.feature_set]
        self.deid_d = transform(self.deid_d, schema)  # transformed data
        self.tar_d = transform(self.tar_d, schema)
        t_dd = self.tar_d.drop_duplicates()
        d_dd = self.deid_d.drop_duplicates()

        # keep deid point that are not in target data

        m_d = d_dd.merge(t_dd,
                        how='left',
                        on=self.tar_d.columns.tolist(),
                        indicator=True)
        m_d.set_index(d_dd.index, inplace=True)

        m_t = t_dd.merge(d_dd,
                         how='left',
                         on=self.tar_d.columns.tolist(),
                         indicator=True)

        m_t.set_index(t_dd.index, inplace=True)

        self.d_idx = []
        self.t_idx = []
        m_d = m_d[m_d['_merge'] == 'both'].drop(columns=['_merge'])
        m_t = m_t[m_t['_merge'] == 'both'].drop(columns=['_merge'])
        self.d_idx = m_d.index.tolist()
        self.t_idx = m_t.index.tolist()

        # p_size = 8
        # t_c = np.array_split(t_dd, p_size)
        # d_c = np.array_split(d_dd, p_size)
        #
        # pool = mp.Pool(p_size)
        # t_data = [(m_t, c) for c in t_c]
        # d_data = [(m_d, c) for c in d_c]
        # print('EQUALITY CHECK TARGET')
        # res = pool.starmap(get_index, t_data)
        # self.t_idx = [item for sublist in res for item in sublist]
        # print('EQUALITY CHECK DEID')
        # res = pool.starmap(get_index, d_data)
        # self.d_idx = [item for sublist in res for item in sublist]

        # print('EQUALITY CHECK DONE')
        # print('Target MERGE Shape: ', m_t.shape, len(self.t_idx))
        # print('Deid MERGE Shape: ', m_d.shape, len(self.d_idx))
        # # print(m)
        # # print(m['_merge'].value_counts())
        #
        # for c in self.tar_d.columns.tolist():
        #     u_tar = self.tar_d[c].unique().tolist()
        #     u_deid = self.deid_d[c].unique().tolist()
        #     u_tar_types = [type(v) for v in u_tar]
        #     u_deid_types = [type(v) for v in u_deid]
        #     print(c, ' unique target: ', u_tar)
        #     print(c, ' unique deid: ', u_deid)
        #     print(c, ' unique target types: ', u_tar_types)
        #     print(c, ' unique deid types: ', u_deid_types)

        self.cc = components
        self.t_pca = PCA(n_components=self.cc)
        self.comp_df = comps_df
        self.t_pdf = None  # target pca transformed data
        self.d_pdf = None  # deid pca transformed data
        self.axis_range = None  # min and max value of each PCA

    def pca(self):
        self.tar_d = self.tar_d.reindex(sorted(self.tar_d.columns), axis=1)
        self.deid_d = self.deid_d.reindex(sorted(self.tar_d.columns), axis=1)
        df_v = self.deid_d.values
        tdf_v = self.tar_d.values
        # Standardize features by removing the mean and scaling to unit variance.
        scaler = StandardScaler().fit(tdf_v)
        df_v = scaler.transform(df_v)
        tdf_v = scaler.transform(tdf_v)
        # tdf_v = StandardScaler().fit_transform(self.tar_d.values)

        # transform target data to pca space
        t_pc = self.t_pca.fit_transform(tdf_v)

        self.comp_df = pd.DataFrame(self.t_pca.components_,
                                    columns=self.tar_d.columns,
                                    index=[i for i in range(self.cc)])

        # transform deid data to pca space using target pca basis
        t_pc = np.matmul(tdf_v, np.array(self.comp_df.T.values))
        d_pc = np.matmul(df_v, np.array(self.comp_df.T.values))

        comps_c = self.comp_df.columns.tolist()
        for c in comps_c:
            if c not in self.feature_set:
                self.comp_df = self.comp_df.drop(columns=[c])

        # print('Features: ', self.tdf.columns.tolist())
        # print()
        # print('PCA Basis (From original data):')
        #
        # for i, comp in enumerate(self.comp_df.values):
        #     qc = [[n, round(v, 2)] for n, v in zip(self.tdf.columns.tolist(), comp)]
        #     qc = sorted(qc, key=lambda x: x[1], reverse=True)
        #     qc = [f'{v[0]} ({v[1]})' for v in qc]
        #     print(f'PC: {i}: ',','.join(qc[:9]))
        # print()
        # self.comp_df.to_csv('resource/national_comps.csv')
        self.t_pdf = pd.DataFrame(data=t_pc,
                                  columns=[f'PC-{i}'
                                           for i in range(self.cc)],
                                  index=self.tar_d.index)


        self.d_pdf = pd.DataFrame(data=d_pc,
                                  columns=[f'PC-{i}'
                                           for i in range(self.cc)],
                                  index=self.deid_d.index)

        mins = []
        maxs = []
        for pc in self.t_pdf.columns:
            pc_min = self.t_pdf[pc].min()
            pc_max = self.t_pdf[pc].max()
            mins.append(pc_min)
            maxs.append(pc_max)
        self.axis_range = pd.DataFrame(data=[mins, maxs],
                                       columns=self.t_pdf.columns,
                                       index=['min', 'max'])
        # print('PCA Basis AFTER:')
        # for c in self.d_pdf.columns:
        #     print(c, self.d_pdf[c].min(), self.d_pdf[c].max())
        # print()
        for c in self.d_pdf.columns:
            self.d_pdf[c] = min_max_scaling(self.d_pdf[c],
                                            self.t_pdf[c].min(),
                                            self.t_pdf[c].max())
        for c in self.t_pdf.columns:
            self.t_pdf[c] = min_max_scaling(self.t_pdf[c])

        # self.t_pdf = self.t_pdf.iloc[self.t_idx]
        # self.d_pdf = self.d_pdf.iloc[self.d_idx]
        # print('Final target size : ', self.t_pdf.shape)
        # print('Final deid size : ', self.d_pdf.shape)
        # print('PCA Basis AFTER:')
        # for c in self.d_pdf.columns:
        #     print(c, self.d_pdf[c].min(), self.d_pdf[c].max())
        # print()


