#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
画验证图，所有县级市，3 年。
"""
#%%
import os
import re
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats as stats
from matplotlib import rcParams
import seaborn as sns
#%%
rcParams["font.family"] = "Times New Roman"
plt.rcParams["xtick.direction"] = "in"
plt.rcParams["ytick.direction"] = "in"
# os.chdir("D:/Agri/rice/validation")
#%%
def varify(x0, y0, rng, xtick=True, ytick=True):
    x = []; y = []
    for i in range(len(x0)):
        if np.isnan(x0[i]) or np.isnan(y0[i]): continue
        x.append(x0[i])
        y.append(y0[i])
    sns.regplot(
        x=x, y=y, marker=".", color="k", 
        scatter_kws={"s": 30, "lw": 0},
        line_kws={"ls": (0,(5,10)), "lw": 0.85}
    )
    k, b = np.linalg.lstsq(np.vstack([x, np.ones(len(x))]).T, y, rcond=-1)[0]
    r, _ = stats.pearsonr(x, y)
    dtm = r ** 2
    # rmse = np.sqrt(np.mean((np.array(x) - np.array(y)) ** 2))
    mae = np.mean(np.abs(np.array(x) - np.array(y)))
    rmae = mae / np.mean(np.array(x))
    # mrae = np.mean(np.abs(np.array(x) - np.array(y)) / np.array(x))
    plt.plot([0, rng], [0, rng], color="k", lw=0.85)
    plt.xlim(0, rng); plt.ylim(0, rng)
    if xtick:
        plt.xticks(size="x-large")
    else:
        plt.xticks(size=0)
    if ytick:
        plt.yticks(size="x-large")
    else:
        plt.yticks(size=0)
    est_equ = "$y = %1.2f x " % k + ("+ %.2f$\n" % b if b > 0 else "−%5.2f$\n" % -b)
    plt.text(
        rng - rng / 32, rng / 32,
        est_equ +
        "$R^2$ = %1.3f\n"%dtm +
        # "MAE = %.2f\n"%mae +
        "RMAE = %.2f"%rmae,# +
        # "MRAE = %.2f"%mrae,
        horizontalalignment='right',
        verticalalignment='bottom',
        size="x-large"
    )
    ax = plt.gca()
    ax.set_aspect(1)
    # plt.grid()
    return rng
#%%
provinces = [
    # "Odisha",
    # "Bihar",
    # "Assam",
    # "Kerala",
    # "WestBengal",
    # "TamilNadu",
    # "Karnataka",
    # "Telangana",
    # "AndhraPradesh",
    "ArunachalPradesh",
    "Punjab",
    "JammuandKashmir",
    "Jharkhand",
    "HimachalPradesh",
    "Maharashtra",
    "Manipur",
    "Rajasthan",
    "Gujerat",
    "Punjab",
    "MadhyaPradesh",
    "Chhattisgarh",  
    # "UttarPradesh",  
    "Haryana",
    # "Tirpura",
    # "Meghalaya",
]
#%%
# # level = "city"; accuracy = 1e2
# level = "county"; accuracy = 1e1
# xlsx = pd.DataFrame()
# for place in versions.keys():
#     for version in [versions[place]]:
#         xlsx0 = pd.read_excel(f"{place}-{level}-area.xlsx")
#         xlsx0.rename(columns={
#             f"DTW_{version}_2017": "DTW_2017",
#             f"DTW_{version}_2018": "DTW_2018",
#             f"DTW_{version}_2019": "DTW_2019",
#         }, inplace=True)
#         xlsx = xlsx.append(xlsx0)
#%%
xlsx = pd.read_excel(f"/mnt/e/chenxb/India/train/1.xlsx")
fig = plt.figure(figsize=(15*0.8, 12*0.8), dpi=300, facecolor="white")
# fig, axs = plt.subplots(nrows=2, ncols=3, figsize=(12, 8))
# for yr in range(2017, 2019+1):
for i, province in enumerate(provinces):
    # if province not in xlsx.keys(): continue
    #ix = (yr-2017) % 3
    ix = i % 4
    iy = i // 4
    ax = plt.axes([0.080+0.295*ix, 0.890-0.295/12*15*iy, 0.270, 0.270/12*15])
    x = xlsx[f"{province}(ha)"].to_numpy() / 1000
    y = xlsx[f"SPRMI_{province}"].to_numpy() / 1000
    max_axis = 185
    varify(x, y, max_axis,
        xtick = iy == 2,
        ytick = ix == 0
    )
    plt.text(
        0.05 * max_axis, 0.90 * max_axis,
        "(" + chr(ord("a")+i) + ")",
        size="xx-large"
    )
    plt.title(province, fontdict={'fontsize': 16, 'fontweight': 'bold'})
fig.text(
    0.65, 0.08, "Statistical area (×10$^3$ ha)",
    size="xx-large", ha="center", va="center"
)
fig.text(
    0.04, 0.65, "Identified area (×10$^3$ ha)",
    size="xx-large", ha="center", va="center", rotation=90
)
# plt.savefig(f"India-Kharif_rice-county-SPRMI-all.png")
# # # plt.tight_layout()
# plt.close()

# %%
