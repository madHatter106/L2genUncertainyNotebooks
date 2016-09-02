# -*- coding: utf-8 -*-
"""
Created on Thu May  5 11:16:51 2016

@author: ekarakoy
"""




def isin_convert(grid=None,coord=None,polygons=False,Nlat=4320):
    """Input must be either a vector of grid numbers ["grd"] or a dataframe
    with column and row identifiers ["coord", e.g. columns in coord$col and
    rows in coord$row]

    When the argument "polygon=FALSE" (Default), the function will output
    a dataframe object containing grid information (gridnumber["output$grd"],
    column["output$col"], row["output$row"], longitude["output$lon"], and
    latitude[output$lat])
    If the argument "polygon=TRUE", then the putput will be a list with
    polygon shapes in a dataframe(longitudinal coordinates of corners
    ["[[i]]$x"], latitudinal coordinates of corners ["[[i]]$y"])"""

    earth_radius = 6378.137 # TODO this was different in globcolour metadata
    Nlat = 4320 # Number of latitudinal bands, globcolour default 4km resolution
    pi = np.pi
    circum = 2*pi*earth_radius # circumference of Earth at equator
    lat_rows = np.arange(1,Nlat+1,1) # nparray of sequence 1 to Nlat
     # circumfrance at equator / lat bin width:
     # delta-radius, varies by how many parallels there are (Nlat)
    dr = (pi*earth_radius)/Nlat
     # angle increment between each parrallel:
     # delta-phi, from equator to pole
    dphi_lat = pi/Nlat
    phi = -(pi/2)+(lat_rows*dphi_lat)-(dphi_lat/2) # nparray of angles
     # calculate latitudal circumference of parallels:
    p = circum*np.cos(phi) # np array of circ in __ (2*Pi*r)*cos(phi)
     # number of lon rows, dimension = lat dimension at equ.
    Nlon = np.rint(p/dr) #round to nearest whole integer
    dlon = p/Nlon # circumfrance / number of meridians
    dphi_lon = (2*pi)/Nlon
    Ntot = sum(Nlon)
    lat = phi*(180/pi) # nparray of angles to radians

    if (grid is not None):
# calculate coordinates