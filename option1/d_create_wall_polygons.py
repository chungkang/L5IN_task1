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

with open(directory_path + 'outer_wall_manual.geojson') as f:
    outer_wall_geojson = json.load(f)

wall_polygon = geometry.shape(outer_wall_geojson['features'][0]['geometry'])

# load EPSG32632 geojson
with open(directory_path + 'filtered_room_polygon.geojson') as f:
    filtered_room_polygon_geojson = json.load(f)

room_polygon_list = []
for each_room in filtered_room_polygon_geojson['features']:
    room_polygon = geometry.shape(each_room['geometry'])
    room_polygon_list.append(room_polygon)

# polygon substraction
# https://stackoverflow.com/questions/61930060/how-to-use-shapely-for-subtracting-two-polygons
wall_polygon = wall_polygon.difference(geometry.MultiPolygon(room_polygon_list))

# with open(directory_path + 'door_polygon.geojson') as f:
#     door_polygon_geojson = json.load(f)

with open(directory_path + 'door_polygon_buffer.geojson') as f:
    door_polygon_buffer_geojson = json.load(f)

# subtract door from outer wall
door_polygon_list = []
# for each_door in door_polygon_buffer_geojson['features']:
for each_door in door_polygon_buffer_geojson['features']:
    door_polygon = geometry.shape(each_door['geometry'])
    door_polygon_list.append(door_polygon)
    
wall_polygon = wall_polygon.difference(geometry.MultiPolygon(door_polygon_list))


with open(directory_path + 'stair_polygon.geojson') as f:
    stair_polygon_geojson = json.load(f)

# subtract stair from outer wall
stair_polygon_list = []
# for each_door in stair_polygon_geojson['features']:
for each_door in stair_polygon_geojson['features']:
    stair_polygon = geometry.shape(each_door['geometry'])
    stair_polygon_list.append(stair_polygon)

wall_polygon = wall_polygon.difference(geometry.MultiPolygon(stair_polygon_list))

# wall polygon
wall_polygon_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

wall_polygon_feature = {
    "type": "Feature",
    "properties": {
    },
    "geometry": geometry.mapping(wall_polygon)
}
wall_polygon_geojson["features"].append(wall_polygon_feature)

create_geojson.write_geojson(directory_path + 'wall_polygon.geojson', wall_polygon_geojson)
