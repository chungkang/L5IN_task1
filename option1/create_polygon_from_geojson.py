import geopandas as gpd
import geojson
import json
from shapely.geometry import LineString
import shapely
from shapely.geometry import *
from shapely.ops import unary_union
from shapely import geometry
import module.create_geojson as create_geojson
import copy

with open('geojson_result\\22092022\\4OG_7m_60.geojson') as f:
    geojson_result = json.load(f)

#appending all lines from the file to List as shapely objects:
lines_all = []

# line들의 edge points에서 접하는 모든 선분을 추출
for line in  geojson_result['features']:
    line = geometry.shape(line['geometry'])
    lines_all.append(line.buffer(0.01))

# 구해진 모든 wall lines를 통해서 내부 polygon을 구함
Multipolygon = shapely.ops.unary_union(lines_all)

Polygons = list(Multipolygon.geoms)

# initialize empty geojson
polygon_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

for polygon in Polygons:
    all_internal_geoms = [geom for geom in polygon.interiors]

    
    # result polygon from the room detection algorithm
    for geom in all_internal_geoms:
        geom_feature = {
            "type": "Feature",
            "properties": {
                "index": ''
            },
            "geometry":geometry.mapping(geometry.Polygon(geom))
        }
        polygon_geojson["features"].append(geom_feature)

create_geojson.write_geojson('geojson_result\\22092022\\polygon.geojson', polygon_geojson)