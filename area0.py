#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AUTHOR: Shen Ruoque
VERSION: 2020.01.22

对省级识别图进行分割，计算各市/县水稻面积用于验证。
输出 Excel。
"""
#%%
import os
import numpy as np
import pandas as pd
import rasterio
import rasterio.mask
import geopandas as gpd
import multiprocessing as mp
from functools import partial
#%%
def gridarea(lonres, latres, lat):
    return (
        6371008.8 ** 2 * np.deg2rad(lonres) *
        (np.sin(np.deg2rad(lat)) - np.sin(np.deg2rad(lat + latres)))
    )
gridareavec = np.vectorize(gridarea)


def getarea(flag, place_infile, res=None):#res=None
    """
    计算市/县水稻面积

    Parameters
    ----------
    place: GeoDataFrame row, 市/县级矢量边界
    infile: Str, 省级识别结果文件
    flag: List, 水稻标识
    res: Float, 栅格分辨率

    Returns
    -------
    area: Float, 市/县水稻面积列表
    """
    place, infile = place_infile
    geo = [place.geometry.__geo_interface__]
    with rasterio.open(infile) as ds:
        data, transform = rasterio.mask.mask(ds, geo, crop=True)
    data = data[0, :, :]
    height = data.shape[0]
    pixnum = np.zeros(data.shape[0], dtype=np.uint16)
    for iflag in flag:
        pixnum += np.sum(data == iflag, axis=1, dtype=np.uint16)
    del data
    if res is None:
        lonres = transform[0]
        latres = transform[4]
        lats = np.array([transform[5] + i * latres for i in range(height)])
        pixareas = gridareavec(lonres, latres, lats)
        _grid_area = np.sum(pixnum * pixareas)
        if _grid_area != 0:
            area = _grid_area / 10000
        else:
            area = np.nan
        del lats, pixareas
    else:
        _grid_num = np.sum(pixnum)
        if _grid_num != 0:
            area = _grid_num / 10000 * res * res
        else:
            area = np.nan
    del pixnum
    return area
#%%
version = "500m"
croptype = "三季"
prefix = "classified-"
provinces = [
    # "Odisha",
    # "Bihar",
    # "AndhraPradesh",
    # "ArunachalPradesh",
    # "Assam",
    # "Kerala",
    # "Assam",
    # "WestBengal",
    # "TamilNadu",
    # "Punjab",
    # "JammuandKashmir",
    # "Jharkhand",
    # "HimachalPradesh",
    #  "Maharashtra",
    # "Manipur"
    # "Rajasthan",
    # "Gujerat",
    # "Punjab",
    # "MadhyaPradesh",
    # "Chhattisgarh",  
    # "UttarPradesh",  
    # "Karnataka",
    # "Haryana",
    # "Telangana",
    # "Tirpura",
    # "Meghalaya",
    "China",

]
inpath = "/mnt/e/chenxb/India/Odisha/classified" # tif的路径

date_range_str = {
    2017: "20161101_20171031",
    2018: "20171101_20181031",
    2019: "20181101_20191031",
    2020: "20191101_20201231",
}

for province in provinces:
    print(province)
    places = gpd.read_file("/mnt/e/chenxb/India/fromglc10v01/shp/china/china_provinces.shp"
        # f"/mnt/e/India_PaddyRice/{province}/shp/{province}_Shi.shp" # shp路径
    )
    sheet = pd.DataFrame(places[["NAME"]])#NAME_2Dist_Name
    for yr in [2018]:#, 20202017, , 2019
        rstr = date_range_str[yr]
        print(yr)
        file = ("/mnt/e/chenxb/RICE_CH4/chinapaddyRice2020_cropIntensity2020.tif"
            # prefix + f"{province}-S2_swir1-{rstr}_12day-i-f-WGS84-v{croptype}_{version}.tif"
            # f"Dong_{yr}_Identify/{croptype}_NE_{yr}_V1.tif"
        )
        infile = os.path.join(inpath, file)
        with rasterio.open(infile)as ds:
            crs = ds.crs
        places_infile = [
            (place, infile) for _, place in places.to_crs(crs).iterrows()
        ]

        getarea_p = partial(getarea, [4]) # res=20.0

        pools = mp.Pool(processes=20)
        areas = pools.map(getarea_p, places_infile)
        pools.close()
        pools.join()

        sheet[f"DTW_{croptype}_{version}_{rstr}"] = areas
    sheet.to_excel("/mnt/e/chenxb/RICE_CH4/" +
        # "/mnt/e/shenrq/temp/panbh/validation/" + # 结果路径
        f"{province}-{croptype}-{version}-chinapaddyRice2020_cropIntensity2020.xlsx",
        sheet_name=str(yr)#, index=False
    )

# %%
91.99 +90.32 +81.99 +84.87 +87.82 +94.55 +84.25 +92.59 +84.00 +85.54 +87.19 +78.15 +86.78 +85.09 +89.58 +66.67 +81.91 +83.06 +79.43 +63.16 +84.72 +87.00 +96.07 +75.22 +69.05 +86.64 +87.50 +93.60 +83.12+94.35+84.91 +91.43 +86.06 +91.85 +70.81 +74.03 +90.43 +93.58 