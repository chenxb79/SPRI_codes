#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR: Shen Ruoque
VERSION: v2021.12.01
多变量 DTW
"""
#%%
import os, re, time, ctypes, gc
import numpy as np
import rasterio
import multiprocessing as mp
from datetime import timedelta
#%%
def multi_dtw(rk, tk, rl, tl, wk, wl, wd):
    """
    apply multi-variable DTW

    version: 2021.12.01

    Parameters
    ----------
    rk: angles of real/unknown curve (N × nbands)
    tk: angles of typical/standard curve (M × nbands)
    rl: steps of real/unknown curve (N × nbands)
    tl: steps of typical/standard curve (M × nbands)
    wk: weights for angles (nbands)
    wl: weights for steps (nbands)
    wd: weights for distances (nbands)

    Returns
    -------
    distance of 2 multi-band curves
    """
    M, nbands = rk.shape
    N = tk.shape[0]
    d = np.zeros([M, N])
    for iband in range(nbands):
        d += (
            np.abs(rk[:, iband] - tk[:, iband].T) * wk[iband] +
            np.abs(rl[:, iband] - tl[:, iband].T) * wl[iband]
        ) * wd[iband]

    for m in range(1, M):
        d[m, 0] += d[m-1, 0]
    for n in range(1, N):
        d[0, n] += d[0, n-1]
        for m in range(1, M):
            d[m, n] += min(d[m-1, n], d[m-1, n-1], d[m, n-1])

    return d[-1, -1]

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

def writegtiff(file, data, ref, compress="DEFLATE", bigtiff=False, nodata=None, nthread=None):
    ref["count"] = data.shape[0]
    ref["dtype"] = data.dtype
    if compress is not None: ref["compress"] = compress; ref["tiled"] = True
    if bigtiff: ref["BIGTIFF"] = "YES"
    if nodata is not None: ref["nodata"] = nodata
    if nthread is not None: ref["NUM_THREADS"] = nthread
    with rasterio.open(file, "w", driver="GTiff", **ref) as ds:
        ds.write(data)
    return file

def getSPRMI(i):
    v = -11.06
    w = -29.12
    data_r = np.frombuffer(data_shared, dtype=ctypes.c_int16)
    data_r = data_r.reshape(tlen, -1)
    r = data_r[0:7, i].T
    Data_min = np.nanmin(r)
    idx_min = np.where(r == Data_min)[0][0]
    Data_max = np.nanmax(r[int(idx_min):])
    p2 = Data_max/100.0
    p1 = Data_min/100.0
    fD =1 / (1 +np.exp((v - w) / 2 - (p2- p1)))
    fw =1 - max(0,(p1 -w) / (v - w))**2
    fv =1 - max(0,(v - p2) / (v - w))**2
    SPRMI = fD*fw*fv
    return SPRMI

def gridarea(lonres, latres, lat):
    return (
        6371008.8 ** 2 * np.deg2rad(lonres) *
        (np.sin(np.deg2rad(lat)) - np.sin(np.deg2rad(lat + latres)))
    )
gridareavec = np.vectorize(gridarea)

#%%
outpath ="/mnt/e/chenxb/India/结果/2020/01/"
filname = f"sprmi-10-Manipur-2020-S1_VH-152_12_304_day22222-i-f.tif"
# inpath ="/mnt/private2/panbh/India-PaddyRice/westBengal/"
Band_data , f0 = readgtiff("/mnt/private2/chenxb/India/Manipur_01/Manipur-2020-S1_VH-152_12_304_day-i-f.tif")
# Band_data=Band_data[0,:,:]
valid = np.any(Band_data != 0, axis=0)
index = np.nonzero(valid)
validnum = len(index[0])
tlen = Band_data.shape[0]
Band_data = Band_data[ :, index[0], index[1]]
data_shared = Band_data.flatten() 
sprmi = ~valid * np.float32(np.nan)
del Band_data, valid
gc.collect()
pools = mp.Pool(processes=80)
start_time = time.time()
print("start: ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

sprmi_list = pools.map(getSPRMI, range(validnum))
pools.close()
pools.join()

end_time = time.time()
print("end: ", time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
print("total time: ", timedelta(seconds=end_time-start_time))
sprmi[index[0], index[1]] = sprmi_list
del sprmi_list, index
gc.collect()
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
outfile = os.path.join(outpath, filname)
writegtiff(outfile, sprmi[np.newaxis, :, :], f0, nthread=50, bigtiff=True)
print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))





# data_1 = np.zeros_like(data2)
# a1 = np.round((f1["transform"][5] - f2["transform"][5])/f1["transform"][4])
# b1 = np.round((f1["transform"][5] - f2["transform"][5])/f1["transform"][4])+f1["width"]
# a2 = np.round((f1["transform"][2] - f2["transform"][2])/f1["transform"][0])
# b2 = np.round((f1["transform"][2] - f2["transform"][2])/f1["transform"][0])+f1["height"]
# data_1[0,a1:a2,b1:b2]=data1
# outpath ="/mnt/e/chenxb/India/结果/"
# filname = f"sprmi-10-India-2018-S1-VH-WGS-10m.tif"
# data = data1 +data2 +data3+data4 +data5
# outfile = os.path.join(outpath, filname)
# writegtiff(outfile, data, f1)
# gdalwarp -of GTiff -cutline /mnt/e/chenxb/India/fromglc10v01/shp/India/gadm36_IND_0.shp -crop_to_cutline -dstnodata 0 -co COMPRESS=DEFLATE -co PREDICTOR=2 -co ZLEVEL=9 -co NUM_THREADS=20 -co BIGTIFF=YES /mnt/e/chenxb/India/结果/Kar/classified-10-India-2018-S1_VH_Aut_Int8-i-f.tif /mnt/e/chenxb/India/结果/classified-10-India-2018-S1_VH_Aut-i-f.tif
