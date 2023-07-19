from shapely import geometry
import copy
import geopandas
import json
import a_setting as setting
import module.create_geojson as create_geojson # load functions for creating geojson

MIN_POINT = setting.min_point
DIRECTORY_PATH = setting.directory_path

# read created geojson
with open(DIRECTORY_PATH + 'original_CRS.geojson', "r") as file:
    # Read the contents of the file
    loaded_geojson = json.load(file)

wall_line_idx = 0

# door multipoints to convex_hull polygon
# + get wall lines(none door layers)
wall_lines_geojson = copy.deepcopy(create_geojson.geojson_custom)

door_dict = {}

for lines in loaded_geojson['features']:
    door_points = []

    # door lines
    if lines['properties']['category']=='door':
        if lines['properties']['block_id']!=None and lines['geometry']:
            shapely_lines = lines['geometry']['coordinates']
            for each_line in shapely_lines:
                if type(each_line[0]) == float:
                    door_points.append(each_line)
                else:
                    for point in each_line:
                        door_points.append(point)

            if lines['properties']['block_id'] in door_dict:
                door_dict[lines['properties']['block_id']].append(door_points)
            else:
                door_dict[lines['properties']['block_id']] = door_points

    # wall lines
    else:
        if lines['geometry']:
            wall_line_feature = {
                "type": "Feature",
                "properties": lines['properties'],
                "geometry": lines['geometry']
            }
            wall_lines_geojson["features"].append(wall_line_feature)
            wall_line_idx+=1

door_polygon_geojson = copy.deepcopy(create_geojson.geojson_custom)
door_polygon_buffer_geojson = copy.deepcopy(create_geojson.geojson_custom)
door_points_geojson = copy.deepcopy(create_geojson.geojson_custom)
door_lines_geojson = copy.deepcopy(create_geojson.geojson_custom)

# door_polygon_buffer_list = []

door_polygon_idx = 0
# iterate door_points dictionary with key
for key in door_dict.keys():
    # exclude doors have no block
    if key != '':
        door_array = []
        for i in door_dict[key]:
            if type(i[0]) == float:
                    door_array.append(tuple(i))
            else:
                for point in i:
                    door_array.append(tuple(point))
        door_polygon = geometry.MultiPoint(door_array).convex_hull

        # filter small polygon
        if door_polygon.is_empty or door_polygon.area < 0.03:
            continue

        simplified_polygon = door_polygon
        if door_polygon.area > 0:
            simplified_polygon = door_polygon.simplify(0.1, preserve_topology=True)

        door_polygon_feature = create_geojson.create_geojson_feature(door_polygon_idx, "", "", "", geometry.mapping(simplified_polygon))
        door_polygon_geojson["features"].append(door_polygon_feature)

        # door_polygon_buffer_list.append(door_polygon.buffer(min_point*1.2, 0))
        door_polygon_buffer_feature = create_geojson.create_geojson_feature(door_polygon_idx, "", "", "", geometry.mapping(door_polygon.buffer(MIN_POINT*1.2, 0)))
        door_polygon_buffer_geojson["features"].append(door_polygon_buffer_feature)

        # outer boundery's points of door polygon
        door_points = geometry.MultiPoint(simplified_polygon.exterior.coords)
        door_points_feature = create_geojson.create_geojson_feature(door_polygon_idx, "", "", "", geometry.mapping(door_points))
        door_points_geojson["features"].append(door_points_feature)

        # outer boundery of door polygon
        door_lines = simplified_polygon.boundary
        door_lines_feature = create_geojson.create_geojson_feature(door_polygon_idx, "", "", "", geometry.mapping(door_lines))
        door_lines_geojson["features"].append(door_lines_feature)

        door_polygon_idx += 1

create_geojson.write_geojson(DIRECTORY_PATH + 'door_polygon.geojson', door_polygon_geojson)
create_geojson.write_geojson(DIRECTORY_PATH + 'door_polygon_buffer.geojson', door_polygon_buffer_geojson)
create_geojson.write_geojson(DIRECTORY_PATH + 'door_points.geojson', door_points_geojson)
create_geojson.write_geojson(DIRECTORY_PATH + 'door_lines.geojson', door_lines_geojson)