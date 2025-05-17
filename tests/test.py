import os
import numpy as np
import warnings
import tifffile
import cv2

warnings.filterwarnings("ignore")

import matplotlib.pyplot as plt
import scipy
import tqdm
import matplotlib
import joblib

import torch


import kornia
import seaborn

import sarpy
import rasterio
from osgeo import gdal

# print import versions
print("Python version:", os.sys.version)
print("Numpy version:", np.__version__)
print("Tifffile version:", tifffile.__version__)
print("OpenCV version:", cv2.__version__)
print("Kornia version:", kornia.__version__)
print("Seaborn version:", seaborn.__version__)
print("Rasterio version:", rasterio.__version__)
print("Joblib version:", joblib.__version__)
print("Matplotlib version:", matplotlib.__version__)
print("Torch version:", torch.__version__)
print("GDAL version:", gdal.__version__)
