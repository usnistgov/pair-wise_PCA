from typing import Dict, List, Optional, Tuple
from pathlib import Path
from itertools import product
import pandas as pd
import numpy as np
import pygame
import pygame.freetype
import json
import os
import time
import shutil
from datetime import datetime
import zipfile
import sys
import urllib.request
from tqdm import tqdm
import random
import math

FPS = 60
BIN_FEATURES = ['AGEP', 'PWGTP', 'WGTP', 'PINCP', 'POVPIP']

# my_font_30 = pygame.font.SysFont(None, 30)
