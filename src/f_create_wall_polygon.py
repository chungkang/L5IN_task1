# polygon substraction
# https://stackoverflow.com/questions/61930060/how-to-use-shapely-for-subtracting-two-polygons

import json
from shapely import geometry
import copy
import a_config as config # load configuration parameters for the logics
import module.create_geojson as create_geojson # load functions for creating geojson

DIRECTORY_PATH = config.directory_path_result

# open outer wall created manually with QGIS
with open(DIRECTORY_PATH + 'outer_wall_manual.geojson') as f:
    outer_wall_geojson = json.load(f)

# open room polygon
with open(DIRECTORY_PATH + 'final_room_polygon.geojson') as f:
    final_room_polygon = json.load(f)

# open door polygon with buffer
with open(DIRECTORY_PATH + 'door_polygon_buffer.geojson') as f:
    door_polygon_buffer_geojson = json.load(f)


wall_polygon = geometry.shape(outer_wall_geojson['features'][0]['geometry'])

room_polygon_list = []
for each_room in final_room_polygon['features']:
    room_polygon = geometry.shape(each_room['geometry'])
    room_polygon_list.append(room_polygon)
# subtract room from outer wall
wall_polygon = wall_polygon.difference(geometry.MultiPolygon(room_polygon_list))

door_polygon_list = []
# for each_door in door_polygon_buffer_geojson['features']:
for each_door in door_polygon_buffer_geojson['features']:
    door_polygon = geometry.shape(each_door['geometry'])
    door_polygon_list.append(door_polygon)
# subtract door from outer wall
wall_polygon = wall_polygon.difference(geometry.MultiPolygon(door_polygon_list))

# save wall polygon 
wall_polygon_geojson = copy.deepcopy(create_geojson.geojson_custom)
wall_polygon_feature = create_geojson.create_geojson_feature("", "", "", "", geometry.mapping(wall_polygon))
wall_polygon_geojson["features"].append(wall_polygon_feature)

create_geojson.write_geojson(DIRECTORY_PATH + 'wall_polygon.geojson', wall_polygon_geojson)
