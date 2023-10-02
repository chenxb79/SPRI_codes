#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR: Shen Ruoque
VERSION: v2021.12.01
多变量 DTW
"""
#%%
import numpy as np
import pandas as pd
import rasterio
import matplotlib.pyplot as plt
import os
import xlrd
import multiprocessing as mp
import ctypes
import os, re, time, ctypes
from datetime import timedelta

#%%读写tif文件
#%%
def gtiffref(file):
    with rasterio.open(file) as ds:
        ref = {
            "width": ds.width,
            "height": ds.height,
            "count": ds.count,
            "dtype": ds.dtypes[0],
            "transform": ds.transform,
            "crs": ds.crs,
        }
    return ref

def readgtiff(file):
    with rasterio.open(file) as ds:
        data = ds.read()
    return data, gtiffref(file)
    
def writegtiff(file, data, ref, compress="DEFLATE", bigtiff=False, nthread=None):
    ref["count"] = data.shape[0]
    ref["dtype"] = data.dtype
    if compress is not None: ref["compress"] = compress; ref["tiled"] = True
    if bigtiff: ref["BIGTIFF"] = "YES"
    if nthread is not None: ref["NUM_THREADS"] = nthread
    with rasterio.open(file, "w", driver="GTiff", **ref) as ds:
        ds.write(data)
    return file

data_max, f0  = readgtiff(f"/mnt/private2/chenxb/India/Meghalaya_01/Meghalaya-2018-S1_VH-001_12_364_day-i-f-vh_max_mask_ndvi.tif")
data_min , f0  = readgtiff(f"/mnt/private2/chenxb/India/Meghalaya_01/Meghalaya-2018-S1_VH-001_12_364_day-i-f-vh_min_mask_ndvi_ndwi.tif")
del f0
# data_max = data[~np.isnan(data_max)]
# data_min = data[~np.isnan(data_min)]
max0 = np.nanquantile(data_max[data_max != 0], 0.9)
min0 = np.nanquantile(data_min[data_min != 0], 0.1) 
print(max0)
print(min0)

# print(np.mean(data_min))
# data = data[~np.isnan(data)]
# length = data.size
# sorted0 = np.sort(data)
# sorted0[int(length * 0.1)]#输出前百分之10的数

# np.savetxt('/mnt/e/chenxb/NM/test/d2.txt',dists,delimiter=' ')

