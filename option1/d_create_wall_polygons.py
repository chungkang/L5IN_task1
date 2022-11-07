from tabnanny import check
from venv import create
import json
from shapely import geometry
import alphashape
from descartes import PolygonPatch
import copy
import a_config as config # load configuration parameters for the logics
import module.create_geojson as create_geojson # load functions for creating geojson

directory_path = config.directory_path_result
min_point = config.min_point # minimum length as a point

with open(directory_path + 'outer_wall_manual2.geojson') as f:
    outer_wall_geojson = json.load(f)

wall_polygon = geometry.shape(outer_wall_geojson['features'][0]['geometry'])

# load EPSG32632 geojson
with open(directory_path + 'filtered_room_polygon.geojson') as f:
    filtered_room_polygon_geojson = json.load(f)

for each_room in filtered_room_polygon_geojson['features']:
    room_polygon = geometry.shape(each_room['geometry'])

    # polygon substraction
    # https://stackoverflow.com/questions/61930060/how-to-use-shapely-for-subtracting-two-polygons
    wall_polygon = wall_polygon.difference(room_polygon)


with open(directory_path + 'door_polygon.geojson') as f:
    door_polygon_geojson = json.load(f)

door_polygon_list = []
for each_door in door_polygon_geojson['features']:
    door_polygon = geometry.shape(each_door['geometry'])
    door_buffer = door_polygon.buffer(min_point*1.1)
    door_polygon_list.append(door_buffer)
    
door_multi_polygon = geometry.MultiPolygon(door_polygon_list)

wall_polygon = wall_polygon.difference(door_multi_polygon)

# 계단 polygon 빼기

wall_polygon_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

wall_polygon_feature = {
    "type": "Feature",
    "properties": {
    },
    "geometry": geometry.mapping(wall_polygon)
}
wall_polygon_geojson["features"].append(wall_polygon_feature)

create_geojson.write_geojson(directory_path + 'wall_polygon.geojson', wall_polygon_geojson)
