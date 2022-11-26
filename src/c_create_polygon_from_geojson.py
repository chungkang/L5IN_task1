import json
from shapely import geometry, ops
import module.create_geojson as create_geojson
import copy

import a_config as config

directory_path = config.directory_path_result
min_point = config.min_point # minimum length as a point

with open(directory_path + 'converted_CRS.geojson') as f:
    geojson_result = json.load(f)

# initialize empty geojson
polygon_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

lines_all = []
# room index에 해당하는 geojson_result의 polygon을 찾기
# line들의 edge points에서 접하는 모든 선분을 추출
for line in  geojson_result['features']:
    line = geometry.shape(line['geometry'])
    lines_all.append(line.buffer(min_point))

# 구해진 모든 wall lines를 통해서 내부 polygon을 구함
buffer_polygon = ops.unary_union(lines_all)
# Polygon / Multipolygon
if buffer_polygon.geom_type == 'MultiPolygon':
    for polygon in buffer_polygon:
        all_internal_geoms = [geom for geom in polygon.interiors]
        for geom in all_internal_geoms:
            # if geom.contains(geometry_point):
                geom_feature = create_geojson.create_geojson_feature("", "", "", "", geometry.mapping(geometry.Polygon(geom)))
                polygon_geojson["features"].append(geom_feature)
else:
    all_internal_geoms = [geom for geom in buffer_polygon.interiors]
    for geom in all_internal_geoms:
        # if geom.contains(geometry_point):
            geom_feature = create_geojson.create_geojson_feature("", "", "", "", geometry.mapping(geometry.Polygon(geom)))
            polygon_geojson["features"].append(geom_feature)

create_geojson.write_geojson(directory_path + 'all_room_polygon.geojson', polygon_geojson)

with open(directory_path + 'room_index.geojson') as f:
    room_index = json.load(f)

room_polygon_list = []
# room index로 for 문 돌리기
for point in  room_index['features']:
    geometry_point = geometry.Point(point['geometry']['coordinates'])
    for polygon in polygon_geojson['features']:
        geometry_polygon = geometry.shape(polygon['geometry'])
        if geometry_polygon.contains(geometry_point):
            room_polygon_list.append(geometry_polygon)

room_multi_polygon = geometry.MultiPolygon(room_polygon_list)

final_room_multi_polygon = room_multi_polygon.intersection(room_multi_polygon)

# initialize empty geojson
final_room_polygon_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

room_idx = 0
# extract polygons out of multipolygon
for polygon in final_room_multi_polygon:
    geom_feature = create_geojson.create_geojson_feature(room_idx, "", "", "", geometry.mapping(polygon))
    final_room_polygon_geojson["features"].append(geom_feature)
    room_idx += 1

create_geojson.write_geojson(directory_path + 'final_room_polygon.geojson', final_room_polygon_geojson)
