#!/usr/bin/env julia -p 4
# -*- coding: utf-8 -*-
# AUTHOR: Shen Ruoque
#=
并行地将被 GEE 切分过的遥感文件拼起来，多年同时进行。
=#
using Distributed
addprocs(1)
@everywhere rsindex = "VH"
@everywhere satellite = "S1"
@everywhere composite = "2021121_12_2022243_day"
@everywhere include("/mnt/e/shenrq/Agri/TWDTW/mergelist.jl")
@everywhere cd("/mnt/private2/chenxb/India/Odisha_01")
@everywhere function isfname(place, yr, rsindex, fname)
    isfile(fname) &&
    occursin("$place-$yr-$(satellite)_$rsindex-$composite-i-f", fname)
end

@sync @distributed for yr = 2022:2022
    place = "Odisha"
    path = "./"
    flist = [i for i = readdir(path) if isfname(place, yr, rsindex, joinpath(spath, i))]
    outfile = "$place-$yr-$(satellite)_$rsindex-$composite-i-f.tif"
    println(flist)
    mergelist(path, flist, joinpath(path, outfile))
    [rm(joinpath(path, file)) for file = flist if file ≠ outfile]
end

rmprocs(workers())

# IOError: unlink("./WestBengal-2022-S1_VH-182_12_304_day-i-f-0000000000-0000000000.tif"): no such file or directory (ENOENT)
