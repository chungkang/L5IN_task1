from tabnanny import check
from venv import create
import ezdxf
import ezdxf.addons.geo as geo
import json
import geopandas
from shapely import geometry
import shapely
from descartes import PolygonPatch
import copy

import a_config as config # load configuration parameters for the logics
import module.create_geojson as create_geojson # load functions for creating geojson
import module.shapely_functions as shapely_functions # load functions for shapely

# loading dxf file
dxf_name =config.dxf_name
doc = ezdxf.readfile("dxf\\"+ dxf_name + ".dxf")

# get modelspace
msp = doc.modelspace()

min_length = config.min_length # minimum length of lines(ignore short lines)
min_point = config.min_point # minimum length as a point
wall_width = config.wall_width # wall width
wall_filtering_distance = config.wall_filtering_distance # wall fintering distance
directory_path = config.directory_path # directory path of saving result

# get layout / plan - layout page
# plan = doc.layout('16 - plan 2.OG_1_100')

# initialize empty geojson
origin_geojson = copy.deepcopy(create_geojson.geojson_custom)

# interested layer list
layer_list = config.layer_list

# door_id
door_block_id = 0
# entity index 
idx = 0

# explode all blocks
for flag_ref in msp.query("INSERT"):
    exploded_e = flag_ref.explode()
    
    # exploded door layer lines(door layer, but not door block, door components)
    for e in exploded_e.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='AUSBAU - Objekte - Tueren']"):
        geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)
        
        # skip short lines
        line = geometry.shape(geo_proxy.__geo_interface__)
        if line.length < min_length:
            continue

        each_feature = {
            "type": "Feature",
            "properties": {
                "index": idx,
                "layer": 'AUSBAU - Objekte - Tueren',
                "category": "door",
                "door_id": str(door_block_id)
            },
            "geometry": geo_proxy.__geo_interface__
        }
        origin_geojson["features"].append(each_feature)
        idx += 1

    door_block_id += 1

for layer in layer_list:
    for e in msp.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='" + layer + "']"):
        # Convert DXF entity into a GeoProxy object:
        geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)
        
        # skip short lines
        line = geometry.shape(geo_proxy.__geo_interface__)
        if line.length < min_length:
            continue
        
        category = "wall"
        if "waende" in layer or "Waende" in layer or "trockenbau" in layer or "Trockenbau" in layer:
            category = "wall"
        # elif "treppen" in layer or "Treppen" in layer:
        #     category = "stair"

        each_feature = {
            "type": "Feature",
            "properties": {
                "index": idx,
                "layer": layer,
                "category": category
            },
            "geometry": geo_proxy.__geo_interface__
        }
        origin_geojson["features"].append(each_feature)
        idx += 1

# write custom defined CRS geojson
create_geojson.write_geojson(directory_path + 'original.geojson', origin_geojson)

# read created geojson / reprojection to EPSG:32632 / write reprojected geojson
loaded_geojson = geopandas.read_file(directory_path + 'original.geojson')
loaded_geojson = loaded_geojson.to_crs('EPSG:32632')
loaded_geojson.to_file(directory_path + 'original_EPSG32632.geojson', driver='GeoJSON')

# load EPSG32632 geojson
with open(directory_path + 'original_EPSG32632.geojson') as f:
    epsg32632_geojson = json.load(f)

wall_line_idx = 0

# door multipoints to convex_hull polygon
# + get wall lines(none door layers)
wall_lines_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

door_dict = {}
for lines in epsg32632_geojson['features']:
    door_points = []
    
    # door lines
    if lines['properties']['category']=='door':
        if lines['properties']['door_id']!=None and lines['geometry']:
            shapely_lines = lines['geometry']['coordinates']
            for each_line in shapely_lines:
                if type(each_line[0]) == float:
                    door_points.append(each_line)
                else:
                    for point in each_line:
                        door_points.append(point)

            if lines['properties']['door_id'] in door_dict:
                door_dict[lines['properties']['door_id']].append(door_points)
            else:
                door_dict[lines['properties']['door_id']] = door_points
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

door_polygon_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
door_points_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
door_lines_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

door_polygon_idx = 0

# door_points dictionary를 key 단위로 돌려줌
for key in door_dict.keys():
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

    door_polygon_feature = {
        "type": "Feature",
        "properties": {
            "index": door_polygon_idx
        },
        "geometry": geometry.mapping(door_polygon)
    }
    door_polygon_geojson["features"].append(door_polygon_feature)

    # door polygon의 테두리 points를 뽑는다
    door_points = geometry.MultiPoint(door_polygon.exterior.coords)
    door_points_feature = {
        "type": "Feature",
        "properties": {
            "index": door_polygon_idx
        },
        "geometry": geometry.mapping(door_points)
    }
    door_points_geojson["features"].append(door_points_feature)

    # door polygon의 테두리 lines를 뽑는다
    door_lines = door_polygon.boundary

    door_lines_feature = {
        "type": "Feature",
        "properties": {
            "index": door_polygon_idx
        },
        "geometry": geometry.mapping(door_lines)
    }
    door_lines_geojson["features"].append(door_lines_feature)

    door_polygon_idx += 1

create_geojson.write_geojson(directory_path + 'door_polygon.geojson', door_polygon_geojson)
# create_geojson.write_geojson(directory_path + 'door_points.geojson', door_points_geojson)
# create_geojson.write_geojson(directory_path + 'door_lines.geojson', door_lines_geojson)

# room index
room_index_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

# to check log
room_index = ''

# door 전체를 돌리는 for문
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
        
        # 2. filter walls which has specipic distance from door point
        distance_from_door_point = wall_filtering_distance
        filtered_walls_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
        filtered_walls_idx = 0

        for line in wall_lines_geojson['features']:
            if line['geometry']:
                line_shp = geometry.shape(line['geometry'])
                if door_point.distance(line_shp) < distance_from_door_point:
                    # split closed polylines - 4 lines
                    if len(line['geometry']["coordinates"]) == 5:
                        wall_line_coords_1 = line['geometry']["coordinates"][1]
                        wall_line_coords_2 = line['geometry']["coordinates"][2]
                        wall_line_coords_3 = line['geometry']["coordinates"][3]
                        middle_points = geometry.MultiPoint([wall_line_coords_1,wall_line_coords_2,wall_line_coords_3])

                        lines = shapely.ops.split(geometry.LineString(list(line['geometry']["coordinates"])), middle_points)
                        for line in lines:
                            each_feature = {
                                "type": "Feature",
                                "properties": {
                                    "index": filtered_walls_idx
                                },
                                "geometry": geometry.mapping(line)
                            }
                            filtered_walls_geojson["features"].append(each_feature)
                            filtered_walls_idx += 1
                    else:
                        each_feature = {
                            "type": "Feature",
                            "properties": {
                                "index": filtered_walls_idx
                            },
                            "geometry": geometry.mapping(line_shp)
                        }
                        filtered_walls_geojson["features"].append(each_feature)
                        filtered_walls_idx += 1

        # add 2 longer lines of door
        each_feature = {
                        "type": "Feature",
                        "properties": {
                            "index": filtered_walls_idx
                        },
                        "geometry": geometry.mapping(using_door_lines[0])
                    }
        filtered_walls_geojson["features"].append(each_feature)
        filtered_walls_idx += 1

        each_feature = {
                        "type": "Feature",
                        "properties": {
                            "index": filtered_walls_idx
                        },
                        "geometry": geometry.mapping(using_door_lines[1])
                    }
        filtered_walls_geojson["features"].append(each_feature)
        filtered_walls_idx += 1    

        temp_filtered_walls_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
        # add properties of door juction line to feature of filtered_walls_geojson
        for line in filtered_walls_geojson["features"]:
            door_juction_yn = 'N'
            for point in door_points_geojson["features"]:
                # filter door_points which is close to the door_point
                if door_point.distance(geometry.shape(point['geometry'])) > distance_from_door_point:
                    continue

                # calculate distance between filtered_walls and door_points
                if geometry.shape(point['geometry']).distance(geometry.shape(line['geometry'])) < min_point:
                    door_juction_yn = 'Y'
                    break
            
            each_feature = {
                "type": "Feature",
                "properties": {
                    "index": line["properties"]["index"]
                    ,"door_juction": door_juction_yn
                },
                "geometry": line["geometry"]
            }
            temp_filtered_walls_geojson["features"].append(each_feature)
        filtered_walls_geojson = temp_filtered_walls_geojson

        create_geojson.write_geojson(directory_path + 'filtered_walls.geojson', filtered_walls_geojson)

        # 3. base lines = door_line

        # 4. Make orthogonal line from line1(rotated_line1)
        # draw extended lineString https://stackoverflow.com/questions/33159833/shapely-extending-line-feature
        orgin_rotated_line1 = shapely.affinity.rotate(door_line, 90, origin=door_point)
        l_coords = list(orgin_rotated_line1.coords)
        EXTRAPOL_RATIO = 50
        p1 = l_coords[-2:][0]
        p2 = l_coords[-2:][1]
        a = (p1[0]-EXTRAPOL_RATIO*(p2[0]-p1[0]), p1[1]-EXTRAPOL_RATIO*(p2[1]-p1[1]))
        b = (p2[0]+EXTRAPOL_RATIO*(p2[0]-p1[0]), p2[1]+EXTRAPOL_RATIO*(p2[1]-p1[1]))
        orgin_rotated_line1 = geometry.LineString([a,b])

        # rotated_line1과 주변 wall lines(door_juction)의 intersections를 찾음
        rotated_line1_inters = shapely_functions.find_intersections_baseline_to_all_door_junction(orgin_rotated_line1,filtered_walls_geojson['features'])

        # door_point에서 가장 가까운 점을 찾음
        shortest_distance = 100
        point_in_wall = geometry.Point()
        for point in rotated_line1_inters:
            point_to_point_distance = point.distance(door_point)
            if point_to_point_distance < shortest_distance and point_to_point_distance > min_point:
                shortest_distance = point_to_point_distance
                point_in_wall = point

        if point_in_wall.is_empty:
            continue

        # door_point을 기준으로 point_in_wall과 대칭하는 점을 만듦(new_point)
        new_point = geometry.Point(door_point.coords[0][0]*2-point_in_wall.coords[0][0], door_point.coords[0][1]*2-point_in_wall.coords[0][1])

        # save room index
        geom_feature = {
            "type": "Feature",
            "properties": {
                "door_index": door_index
                ,"id": room_index
            },
            "geometry":geometry.mapping(new_point)
        }
        room_index_geojson["features"].append(geom_feature)

        print("success:index" + room_index)

create_geojson.write_geojson(directory_path + 'room_index.geojson', room_index_geojson)