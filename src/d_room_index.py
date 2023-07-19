import json
from shapely import geometry
from shapely.ops import split
from shapely.affinity import rotate
import copy
import a_setting as setting
import module.create_geojson as create_geojson
import module.shapely_functions as shapely_functions

MIN_POINT = setting.min_point
WALL_WIDTH = setting.wall_width
DIRECTORY_PATH = setting.directory_path

# read created geojson
with open(DIRECTORY_PATH + 'door_lines.geojson', "r") as file:
    # Read the contents of the file
    door_lines_geojson = json.load(file)

# room index
room_index_geojson = copy.deepcopy(create_geojson.geojson_custom)

# to check log
room_index = ''

# iterate door
for door_index in range(len(door_lines_geojson["features"])):

    # draw each lines of door - 4 lines
    line_coords_1 = door_lines_geojson['features'][door_index]['geometry']["coordinates"][1]
    line_coords_2 = door_lines_geojson['features'][door_index]['geometry']["coordinates"][2]
    line_coords_3 = door_lines_geojson['features'][door_index]['geometry']["coordinates"][3]
    midle_points = geometry.MultiPoint([line_coords_1,line_coords_2,line_coords_3])

    door_lines = split(geometry.LineString(list(door_lines_geojson['features'][door_index]['geometry']["coordinates"])), midle_points)

    using_door_lines = []

    # iteration of 4 lines of a door
    for door_line in door_lines.geoms:
        # filter shorter than wall width
        if door_line.length > WALL_WIDTH: 
            using_door_lines.append(door_line)

    door_line_index = 0
    # interate 2 longer lines of a door
    for door_line in using_door_lines:
        room_index = str(door_index) + '-' + str(door_line_index)
        door_line_index += 1

        # 1. start from door_point
        # add door_point as a midle point of the door_line
        x, y = (door_line.bounds[0]+door_line.bounds[2])/2.0, (door_line.bounds[1]+door_line.bounds[3])/2.0
        door_point = geometry.Point(x, y)
        
        # 2. Make orthogonal line from line1(rotated_line1)
        # draw extended lineString https://stackoverflow.com/questions/33159833/shapely-extending-line-feature
        rotated_line = rotate(door_line, 90, origin=door_point)
        l_coords = list(rotated_line.coords)
        EXTRAPOL_RATIO = 50
        p1 = l_coords[-2:][0]
        p2 = l_coords[-2:][1]
        a = (p1[0]-EXTRAPOL_RATIO*(p2[0]-p1[0]), p1[1]-EXTRAPOL_RATIO*(p2[1]-p1[1]))
        b = (p2[0]+EXTRAPOL_RATIO*(p2[0]-p1[0]), p2[1]+EXTRAPOL_RATIO*(p2[1]-p1[1]))
        rotated_line = geometry.LineString([a,b])

        # find intersections of rotated_line and 2 longer lines of door
        rotated_line_inters = shapely_functions.find_intersections_baseline_to_all(rotated_line, door_lines_geojson['features'])

        # find the closest point from door_point
        shortest_distance = 100
        point_in_wall = geometry.Point()
        for point in rotated_line_inters:
            point_to_point_distance = point.distance(door_point)
            if point_to_point_distance < shortest_distance and point_to_point_distance > MIN_POINT:
                shortest_distance = point_to_point_distance
                point_in_wall = point

        if point_in_wall.is_empty:
            continue

        # create new_point from door_point, which is located in opossite of point_in_wall - point in room
        new_point = geometry.Point(door_point.coords[0][0]*2-point_in_wall.coords[0][0], door_point.coords[0][1]*2-point_in_wall.coords[0][1])
        geom_feature = create_geojson.create_geojson_feature(door_index, "", "", room_index, geometry.mapping(new_point))
        room_index_geojson["features"].append(geom_feature)

        print("success:index" + room_index)

create_geojson.write_geojson(DIRECTORY_PATH + 'room_index.geojson', room_index_geojson)