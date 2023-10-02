#!/usr/bin/env julia
# -*- coding: utf-8 -*-
#=
识别水稻种植区
=#

using Distributed
addprocs(5)
@everywhere include(joinpath("/mnt/e/shenrq/Agri/rice/script/gtiffio.jl"))
@everywhere include(joinpath("/mnt/e/shenrq/Agri/rice/script/recognize_core.jl"))

@everywhere maize_areas = Dict(
    "Jilin" => Dict(
        2019 =>305079.1786  , # ha 210595
    )
)
yrmax = maize_areas["Jilin"] |> keys |> maximum

prefix0 = "sprmi-10-"
prefix = "classified-10-"

fname = ARGS[1]
yr = parse(Int, ARGS[2])
# path = "/mnt/e/chenxb/JL/jilin_TWDTW/new/10day/distance/"
path = "/mnt/e/chenxb/India/结果/2020/022/"
infile = joinpath(path, prefix0 * fname)
println(infile)
dist, ref = readgtiff(infile)
dist = dropdims(dist; dims=3)
maize_area = maize_areas["Jilin"][min(yr, yrmax)]
threshold, classified = recognize(dist, ref, 10000maize_area; proj="WGS84", rev=true)  #rev=false是从小到大WGS84 ALBERS
println(threshold)
outpath = joinpath(path, prefix * fname)
writegtiff(outpath, UInt8.(classified), ref)


rmprocs(workers())
