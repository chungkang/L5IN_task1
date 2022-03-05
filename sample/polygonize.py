# -*- coding: utf-8 -*-
"""
Created on Tue Mar 16 11:05:04 2021
@author: Cigdem
edited by Hossein's line2poly code
"""

import json
import fiona
import geopandas as gpd
import geojson
import json
from shapely.geometry import LineString
import shapely
from shapely.geometry import *
from shapely.ops import unary_union
from pathlib import Path


#data_folder = Path("Y:\Projekt\L5IN\1_Scan\QGIS_Map_Routing\DXF2GeoJSON")
#plan = data_folder / ("1OG_DXF2Plan_28062021.geojson")
#boundary = data_folder / ("1OG_Boundary_28062021.geojson")


# import plan as geopandas data frame from geojson
plan_df = gpd.read_file("EG_DXF2Plan_28062021.geojson")



# import the polygon covering HCU building
hcu_boundary = gpd.GeoSeries.from_file("EG_boundingbox.geojson")

print(hcu_boundary)

# create a buffer
plan_buffer = plan_df.buffer(0.0009)

# combine buffer and the plan and set CRS
plan_buffer_union=gpd.GeoSeries(unary_union(plan_buffer)).set_crs(epsg=32632)
#plan_buffer_union=plan_buffer_union.set_crs(epsg=32632)

# polygonizing of the plan. Plan&buffer combination is subtracted from the hcu_polygon
diff=gpd.GeoSeries(hcu_boundary).difference(plan_buffer_union)

# areas outside the building is omitted
plan_poly=[]
for p in diff[0]:
    if p.area<=2000:
        plan_poly.append(p)
        
# create a geoseries from the plan polygons and write to Geojson
plan_final = gpd.GeoSeries(plan_poly)
plan_final = plan_final.set_crs(epsg=32632).to_file("EG_POLYPLAN_28062021_deneme.geojson", driver='GeoJSON')

# the polygonized plan is written to geojson
#plan_final.to_file("plan4OG_polygonv2.geojson", driver='GeoJSON')