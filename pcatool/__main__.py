import os
import datetime
import pandas as pd
import pygame
from pathlib import Path
import argparse
from enum import Enum
import shutil
from pcatool.views import EntryView, pygame_gui

import matplotlib
import pcatool.util as util
from pcatool.pca import FeatureSet
from pcatool.load import download_data, DEFAULT_DATASET, ACS_DATASET
# matplotlib.style.use(["seaborn-deep", "seaborn-notebook"])


class TestDatasetName(Enum):
    NONE = 1
    ma2019 = 2
    tx2019 = 3
    national2019 = 4

target_name_to_state = {
    "ma2019": "massachusetts",
    "tx2019": "texas",
    "national2019": "national"
}

def run():
    bundled_featureset = {
        'all': FeatureSet.all,
        'demographic' :  FeatureSet.demographic,
        'industry': FeatureSet.industry,
        'family': FeatureSet.family
    }
    bundled_datasets = {"MA": TestDatasetName.ma2019,
                        "TX": TestDatasetName.tx2019,
                        "NATIONAL": TestDatasetName.national2019}
    DATA_DIR = Path(DEFAULT_DATASET, ACS_DATASET)
    TAR_DATA_PATH = Path(DATA_DIR, 'national', f'national2019.csv')
    if not DATA_DIR.exists():
        download_data(Path(DEFAULT_DATASET), TAR_DATA_PATH, True)

    pygame.init()
    disp_info = pygame.display.Info()
    w, h = disp_info.current_w - 50, disp_info.current_h - 100

    # entry gui
    egui = EntryView(w, h, bundled_featureset, Path('data'))
    main_prog_exit = False
    while not (egui.exit or main_prog_exit):
        egui.draw()

        state = 'national'
        data_path_str = str(egui.options_view.deid_data_file)
        if len(data_path_str):
            DATA_PATH = Path(egui.options_view.deid_data_file)
            feature_set = FeatureSet[egui.options_view.selected_f_set.lower()]
            # DATA_PATH = Path(args.dataset.name)
            # data_type = DATA_PATH.stem  # target or deidentified
            tar_data_name = bundled_datasets[egui.options_view.select_target_bgrp.selected].name
            state = target_name_to_state[tar_data_name]


            DATA_DICT_PATH = Path(DATA_DIR, 'data_dictionary.json')
            TAR_DATA_PATH = Path(DATA_DIR, state, f'{tar_data_name}.csv')
            SCHEMA_PATH = Path(DATA_DIR, state, f'{tar_data_name}.json')
            # print(TAR_DATA_PATH)
            FILE_DIR = Path(__file__).parent

            RES_PATH = Path(Path.cwd(), 'resource')
            SCREENSHOTS_PATH = Path(Path.cwd(), 'screenshots')
            if not RES_PATH.exists():
                os.mkdir(RES_PATH)
            if not SCREENSHOTS_PATH.exists():
                os.mkdir(SCREENSHOTS_PATH)
            time_now = datetime.datetime.now().strftime('%m-%d-%YT%H.%M.%S')

            DATA_RES_PATH = Path(RES_PATH, '_'.join([DATA_PATH.stem,
                                                     feature_set.name,
                                                     tar_data_name,
                                                     time_now]))

            if not DATA_RES_PATH.exists():
                os.mkdir(DATA_RES_PATH)

            tar_data, schema = util.load(TAR_DATA_PATH, SCHEMA_PATH)

            print(f"Loading {DATA_PATH}...")
            data = pd.read_csv(DATA_PATH)
            unnamed_cols = [c for c in data.columns if 'Unnamed' in c]
            data = data.drop(columns=unnamed_cols)

            data_dict = util.json_load(DATA_DICT_PATH)
            # pygame program
            if egui.stop:
                main_prog_exit = pygame_gui(w, h, DATA_RES_PATH,
                                            tar_data, data, DATA_PATH, TAR_DATA_PATH, schema,
                                            feature_set, data_dict, SCREENSHOTS_PATH,
                                            False)
                if not main_prog_exit:
                    egui.stop = False
                    egui.update()
    pygame.quit()

if __name__ == "__main__":
    run()
