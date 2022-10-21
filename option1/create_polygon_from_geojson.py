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

with open('geojson_result\\17102022\\4OG_result.geojson') as f:
    geojson_result = json.load(f)

# initialize empty geojson
polygon_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

lines_all = []
# room index에 해당하는 geojson_result의 polygon을 찾기
# line들의 edge points에서 접하는 모든 선분을 추출
for line in  geojson_result['features']:
    line = geometry.shape(line['geometry'])
    lines_all.append(line.buffer(0.01))

# 구해진 모든 wall lines를 통해서 내부 polygon을 구함
buffer_polygon = shapely.ops.unary_union(lines_all)
# Polygon / Multipolygon
if buffer_polygon.geom_type == 'MultiPolygon':
    for polygon in buffer_polygon:
        all_internal_geoms = [geom for geom in polygon.interiors]
        for geom in all_internal_geoms:
            # if geom.contains(geometry_point):
                geom_feature = {
                    "type": "Feature",
                    "properties": {
                        # "id": line['properties']['id']
                    },
                    "geometry":geometry.mapping(geometry.Polygon(geom))
                }
                polygon_geojson["features"].append(geom_feature)
else:
    all_internal_geoms = [geom for geom in buffer_polygon.interiors]
    for geom in all_internal_geoms:
        # if geom.contains(geometry_point):
            geom_feature = {
                "type": "Feature",
                "properties": {
                    # "id": line['properties']['id']
                },
                "geometry":geometry.mapping(geometry.Polygon(geom))
            }
            polygon_geojson["features"].append(geom_feature)

create_geojson.write_geojson('geojson_result\\17102022\\4OG_all_polygon.geojson', polygon_geojson)

with open('geojson_result\\11102022\\room_index.geojson') as f:
    room_index = json.load(f)

# initialize empty geojson
filtered_polygon_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

# room index로 for 문 돌리기
for point in  room_index['features']:
    geometry_point = geometry.Point(point['geometry']['coordinates'])

    for polygon in polygon_geojson['features']:
        geometry_polygon = geometry.shape(polygon['geometry'])
        if geometry_polygon.contains(geometry_point):
            polygon_feature = {
                "type": "Feature",
                "properties": {
                    "id": point['properties']['id']
                },
                "geometry":geometry.mapping(geometry_polygon)
            }
            filtered_polygon_geojson["features"].append(polygon_feature)

create_geojson.write_geojson('geojson_result\\17102022\\4OG_filtered_polygon.geojson', filtered_polygon_geojson)

