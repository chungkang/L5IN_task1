import json
from shapely import geometry, ops
import module.create_geojson as create_geojson
import copy

import a_config as config

directory_path = config.directory_path_result
min_point = config.min_point # minimum length as a point

with open(directory_path + 'original_CRS.geojson') as f:
    geojson_result = json.load(f)

# initialize empty geojson
polygon_geojson = copy.deepcopy(create_geojson.geojson_custom)

lines_all = []
# find polygoond fromo geojson_result with room index
# extract all lines which has intersection with edge points
for line in  geojson_result['features']:
    line = geometry.shape(line['geometry'])
    lines_all.append(line.buffer(min_point))

# get all inner polygon(room) from wall lines
buffer_polygon = ops.unary_union(lines_all)
# Multipolygon, Polygon 
if buffer_polygon.geom_type == 'MultiPolygon':
    for polygon in buffer_polygon.geoms:
        all_internal_geoms = [geom for geom in polygon.interiors]
        for geom in all_internal_geoms:
            geom_feature = create_geojson.create_geojson_feature("", "", "", "", geometry.mapping(geometry.Polygon(geom)))
            polygon_geojson["features"].append(geom_feature)
else:
    all_internal_geoms = [geom for geom in buffer_polygon.interiors]
    for geom in all_internal_geoms:
        geom_feature = create_geojson.create_geojson_feature("", "", "", "", geometry.mapping(geometry.Polygon(geom)))
        polygon_geojson["features"].append(geom_feature)

create_geojson.write_geojson(directory_path + 'all_room_polygon.geojson', polygon_geojson)

with open(directory_path + 'room_index.geojson') as f:
    room_index = json.load(f)

room_polygon_list = []
# iterate with room index
for point in  room_index['features']:
    geometry_point = geometry.Point(point['geometry']['coordinates'])
    for polygon in polygon_geojson['features']:
        geometry_polygon = geometry.shape(polygon['geometry'])
        if geometry_polygon.contains(geometry_point):
            room_polygon_list.append(geometry_polygon)

room_multi_polygon = geometry.MultiPolygon(room_polygon_list)

# polygon with room index => room polygon
final_room_multi_polygon = room_multi_polygon.intersection(room_multi_polygon)

# initialize empty geojson
final_room_polygon_geojson = copy.deepcopy(create_geojson.geojson_custom)

room_idx = 0
# extract polygons out of multipolygon
# Multipolygon, Polygon 
if final_room_multi_polygon.geom_type == 'MultiPolygon':
    for polygon in final_room_multi_polygon.geoms:
        geom_feature = create_geojson.create_geojson_feature(room_idx, "", "", "", geometry.mapping(final_room_multi_polygon))
        final_room_polygon_geojson["features"].append(geom_feature)
        room_idx += 1
else:
    geom_feature = create_geojson.create_geojson_feature(room_idx, "", "", "", geometry.mapping(final_room_multi_polygon))
    final_room_polygon_geojson["features"].append(geom_feature)
    room_idx += 1

create_geojson.write_geojson(directory_path + 'final_room_polygon.geojson', final_room_polygon_geojson)
