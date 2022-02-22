# -*- coding: utf-8 -*-
"""
Created on Mon Mar 22 12:06:12 2021

@author: DMZ-Admin

source: Hossein-Shoushtari line2poly
"""

import geopandas as gpd
import geojson
import json
from shapely.geometry import LineString
import shapely
from shapely.geometry import *
from shapely.ops import unary_union

#reading the file:
file = "hcu4og_trans.wkt" 
f = open(file)
lines = f.readlines()
f.close()

def file_len(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i 


#appending all lines from the file to List as shapely objects:
lines_list=[]
for l in lines:
    if l[0]=='L':
        #lines_list.append(shapely.wkt.loads(l[0:len(l)]))
        #print(l.split(',')[0][0:-3]+','+l.split(',')[1][0:-5]+')')
        lines_list.append(shapely.wkt.loads(l.split(',')[0][0:-3]+','+l.split(',')[1][0:-5]+')'))
#adding missing connections/lines:

lines_list.append(
LineString([(566595.4845316549, 5932863.945632452),
(566595.4763183513, 5932863.658166827)])
)
lines_list.append(
LineString([(566509.354591591, 5932808.616056689),
(566509.4540725381, 5932808.815018583)])
)
lines_list.append(
LineString([(566595.4786238708, 5932863.952411722),
(566595.4635867841, 5932863.658353137)])
)
lines_list.append(
LineString([(566511.4827338052, 5932813.106675482),
(566511.4400259551, 5932813.0162772)])
)

print(lines_list)
# creating geoseries from the list of lines and plotting it:
gs_lines = gpd.GeoSeries(lines_list)
gs_lines.plot(figsize=(60,40))

"""
#polygon containing the whole HCU:
poly4=Polygon(
    [
    (566500.6298329703, 5932795.542741078), 
    (566650.5161578016, 5932795.542741078), 
    (566650.5161578016, 5932874.987968483), 
    (566500.6298329703, 5932874.987968483), 
    (566500.6298329703, 5932795.542741078)
    ]
)

#creating small buffer around lines and substrect it from the polygon containing the whole building, resulting in "gs_diff" containing all rooms, the outside of hcu and the "inner part" of the thick walls
lines_buffer=gs_lines.buffer(0.025)

gs_lines_buffer_union=gpd.GeoSeries(unary_union(lines_buffer))

gs_diff=gpd.GeoSeries(poly4).difference(gs_lines_buffer_union)


#eliminating the outside of the hcu-building:
hcu_poly_list=[]
for p in gs_diff[0]:
    if p.area<=2000:
        hcu_poly_list.append(p)

#resulting in hcu_poly_list containing all rooms and the interior of some thick walls (thicker than the buffer) as polygons:
gpd.GeoSeries(hcu_poly_list).plot(figsize=(60,40))

#reading a geojson and query by attributes
map_polys = gpd.read_file("Inputdata/map_4.geojson")
all_walls = map_polys.loc[map_polys['type'] == 'wall']
only_rooms = map_polys.loc[map_polys['type'] == 'room']

gs_lines_buffer_union.type

"""