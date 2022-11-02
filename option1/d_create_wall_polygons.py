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

# with open(directory_path + 'original_EPSG32632.geojson') as f:
#     epsg32632_geojson = json.load(f)

# # outer wall detection - concave hull, alpha shape
# # initialize empty geojson
# outer_wall_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

# wall_points = []
# for lines in epsg32632_geojson['features']:
#     if lines['geometry']:
#         shapely_lines = lines['geometry']['coordinates']
#         for each_line in shapely_lines:
#             if type(each_line[0]) == float:
#                 wall_points.append(tuple(each_line))
#             else:
#                 for point in each_line:
#                     wall_points.append(tuple(point))                

# non_dup_wall_points = []
# [non_dup_wall_points.append(x) for x in wall_points if x not in non_dup_wall_points]

# wall_alpha_shape = alphashape.alphashape(non_dup_wall_points, 0.112)

# wall_feature = {
#     "type": "Feature",
#     "properties": {
#     },
#     "geometry": geometry.mapping(wall_alpha_shape)
# }
# outer_wall_geojson["features"].append(wall_feature)

# create_geojson.write_geojson(directory_path + 'outer_wall.geojson', outer_wall_geojson)


# outer_wall.geojson - filtered_room_polygon.geojson
# wall_polygon = wall_alpha_shape



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

wall_polygon_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

wall_polygon_feature = {
    "type": "Feature",
    "properties": {
    },
    "geometry": geometry.mapping(wall_polygon)
}
wall_polygon_geojson["features"].append(wall_polygon_feature)

create_geojson.write_geojson(directory_path + 'wall_polygon.geojson', wall_polygon_geojson)
