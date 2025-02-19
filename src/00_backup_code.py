import sys
import ezdxf
from ezdxf import recover
import ezdxf.addons.geo as geo
from shapely import geometry
import shapely
import copy

import a_config as config # load configuration parameters for the logics
import module.create_geojson as create_geojson # load functions for creating geojson
import module.shapely_functions as shapely_functions # load functions for shapely

# loading dxf file
dxf_name =config.dxf_name

# Umlaut ae, ue, oe doesn't work with ezdxf.readfile()=>use recover module https://ezdxf.mozman.at/docs/drawing/recover.html
try:
    doc, auditor = recover.readfile(dxf_name)
except IOError:
    print(f'Not a DXF file or a generic I/O error.')
    sys.exit(1)
except ezdxf.DXFStructureError:
    print(f'Invalid or corrupted DXF file.')
    sys.exit(2)

# DXF file can still have unrecoverable errors, but this is maybe just
# a problem when saving the recovered DXF file.
if auditor.has_errors:
    auditor.print_error_report()

# get modelspace
msp = doc.modelspace()

min_point = config.min_point # minimum length as a point
wall_width = config.wall_width # wall width
directory_path = config.directory_path # directory path of saving result

# get layout / plan - layout page
# plan = doc.layout('16 - plan 2.OG_1_100')

# initialize empty geojson
origin_geojson = copy.deepcopy(create_geojson.geojson_custom)

# interested layer list
layer_list = config.layer_list

# block_id
block_id = 0
# entity index 
idx = 0

# explode all blocks
for flag_ref in msp.query("INSERT"):
    exploded_e = flag_ref.explode()
    
    # exploded door layer lines(door layer, but not door block, door components)
    for e in exploded_e.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='" + config.door_layer_name + "']"):
        geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)
        each_feature = create_geojson.create_geojson_feature(idx, config.door_layer_name, "door", str(block_id), geo_proxy.__geo_interface__)
        origin_geojson["features"].append(each_feature)
        idx += 1
    block_id += 1


for layer in layer_list:
    for e in msp.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='" + layer + "']"):
        # Convert DXF entity into a GeoProxy object:
        geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)
        
        if "Türen" in layer:
            category = "door"
        else:
            category = "wall"

        each_feature = create_geojson.create_geojson_feature(idx, layer, category, "", geo_proxy.__geo_interface__)
        origin_geojson["features"].append(each_feature)
        idx += 1

# write custom defined CRS geojson
create_geojson.write_geojson(directory_path + 'original_CRS.geojson', origin_geojson)

# # read created geojson / reprojection to EPSG:32632 / write reprojected geojson
# loaded_geojson = geopandas.read_file(directory_path + 'original_CRS.geojson')
# loaded_geojson = loaded_geojson.to_crs(config.target_CRS)
# loaded_geojson.to_file(directory_path + 'converted_CRS.geojson', driver='GeoJSON')

# # load EPSG32632 geojson
# with open(directory_path + 'converted_CRS.geojson') as f:
#     converted_geojson = json.load(f)

converted_geojson = origin_geojson

wall_line_idx = 0

# door multipoints to convex_hull polygon
# + get wall lines(none door layers)
wall_lines_geojson = copy.deepcopy(create_geojson.geojson_custom)

door_dict = {}

for lines in converted_geojson['features']:
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
        door_polygon = geometry.MultiPoint(door_array).convex_hull.simplify(0.1, preserve_topology=True)

        # filter small polygon
        if(door_polygon.area<0.03): continue

        door_polygon_feature = create_geojson.create_geojson_feature(door_polygon_idx, "", "", "", geometry.mapping(door_polygon))
        door_polygon_geojson["features"].append(door_polygon_feature)

        # door_polygon_buffer_list.append(door_polygon.buffer(min_point*1.2, 0))
        door_polygon_buffer_feature = create_geojson.create_geojson_feature(door_polygon_idx, "", "", "", geometry.mapping(door_polygon.buffer(min_point*1.2, 0)))
        door_polygon_buffer_geojson["features"].append(door_polygon_buffer_feature)

        # outer boundery's points of door polygon
        door_points = geometry.MultiPoint(door_polygon.exterior.coords)
        door_points_feature = create_geojson.create_geojson_feature(door_polygon_idx, "", "", "", geometry.mapping(door_points))
        door_points_geojson["features"].append(door_points_feature)

        # outer boundery of door polygon
        door_lines = door_polygon.boundary
        door_lines_feature = create_geojson.create_geojson_feature(door_polygon_idx, "", "", "", geometry.mapping(door_lines))
        door_lines_geojson["features"].append(door_lines_feature)

        door_polygon_idx += 1

create_geojson.write_geojson(directory_path + 'door_polygon.geojson', door_polygon_geojson)
create_geojson.write_geojson(directory_path + 'door_polygon_buffer.geojson', door_polygon_buffer_geojson)
create_geojson.write_geojson(directory_path + 'door_points.geojson', door_points_geojson)
create_geojson.write_geojson(directory_path + 'door_lines.geojson', door_lines_geojson)

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

    door_lines = shapely.ops.split(geometry.LineString(list(door_lines_geojson['features'][door_index]['geometry']["coordinates"])), midle_points)

    using_door_lines = []

    # iteration of 4 lines of a door
    for door_line in door_lines:
        # filter shorter than wall width
        if door_line.length > wall_width: 
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
        rotated_line = shapely.affinity.rotate(door_line, 90, origin=door_point)
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
            if point_to_point_distance < shortest_distance and point_to_point_distance > min_point:
                shortest_distance = point_to_point_distance
                point_in_wall = point

        if point_in_wall.is_empty:
            continue

        # create new_point from door_point, which is located in opossite of point_in_wall - point in room
        new_point = geometry.Point(door_point.coords[0][0]*2-point_in_wall.coords[0][0], door_point.coords[0][1]*2-point_in_wall.coords[0][1])
        geom_feature = create_geojson.create_geojson_feature(door_index, "", "", room_index, geometry.mapping(new_point))
        room_index_geojson["features"].append(geom_feature)

        print("success:index" + room_index)

create_geojson.write_geojson(directory_path + 'room_index.geojson', room_index_geojson)