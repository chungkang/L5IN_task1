from tabnanny import check
from venv import create
import ezdxf
import ezdxf.addons.geo as geo
import json
import geopandas
from shapely import geometry
import shapely
import alphashape
from descartes import PolygonPatch
import numpy as np
import itertools
import matplotlib.pyplot as plt
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

# room detection algorithm by door polygon's edge points
result_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

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

    # interation of 4 lines of a door
    for door_line in door_lines:
        # filter shorter than wall width
        if door_line.length > wall_width: 
            using_door_lines.append(door_line)

    door_line_index = 0
    # interate 2 longer lines of a door
    for door_line in using_door_lines:
        # try:
            room_index = str(door_index) + '-' + str(door_line_index)
            door_line_index += 1

            # 1. start from door_point
            # add door_point as a midle point of the door_line
            x, y = (door_line.bounds[0]+door_line.bounds[2])/2.0, (door_line.bounds[1]+door_line.bounds[3])/2.0
            door_point = geometry.Point(x, y)

            # door point에서 접하고 평행인 wall line을 찾는다 - wall line은 1개인 경우와 2개인 경우
            # 해당 door line을 90도 회전시켜서 수직선으로 사용
            
            # 2. filtered walls distance from door point
            distance_from_door_point = wall_filtering_distance
            filtered_walls_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
            filtered_walls_idx = 0

            for line in wall_lines_geojson['features']:
                # if line['properties']['category']!='door' and line['geometry']:
                if line['geometry']:
                    line_shp = geometry.shape(line['geometry'])
                    if door_point.distance(line_shp) < distance_from_door_point:
                        # split rounded polylines - 4 lines
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

            # add up door 2 longer lines
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

            # door_point1에서 시작하여 new_point 방향으로 뻗어나가는 line을 그려서 rotated_line1를 update
            line_coords = [(door_point.coords[0][0], door_point.coords[0][1]),(new_point.coords[0][0], new_point.coords[0][1])]
            EXTRAPOL_RATIO = 50
            line_p1 = line_coords[-2:][0]
            line_p2 = line_coords[-2:][1]
            line_point_b = (line_p1[0]+EXTRAPOL_RATIO*(line_p2[0]-line_p1[0]), line_p1[1]+EXTRAPOL_RATIO*(line_p2[1]-line_p1[1]))
            rotated_line1 = geometry.LineString([(door_point.coords[0][0], door_point.coords[0][1]), line_point_b])

            # 업데이트된 rotated_line1과 wall lines들이 접하는 points를 업데이트(rotated_line1_inters 업데이트)
            rotated_line1_inters = shapely_functions.find_intersections_baseline_to_all(rotated_line1,filtered_walls_geojson['features'])

            # door_point1에서 rotated_line1_inters 에 있는 point 중에 가장 가까운 점을 구함(반대편 벽에 접하는 line2_intersect_point)
            shortest_distance = 100
            line2_intersect_point = geometry.Point()
            for point in rotated_line1_inters:
                point_to_point_distance = point.distance(door_point)
                if point_to_point_distance < shortest_distance and point_to_point_distance > min_point:
                    shortest_distance = point_to_point_distance
                    line2_intersect_point = point

            # line2_intersect_point와 접하는 wall line을 찾음(line2)
            line2 = geometry.LineString()
            for line in filtered_walls_geojson['features']:
                line_shp = geometry.shape(line['geometry'])
                if line_shp.distance(line2_intersect_point) < min_point:
                    line2 = line_shp

            # door 쪽의 벽을 감지하는 로직
            door_end1_x, door_end1_y = door_line.bounds[0], door_line.bounds[1]
            door_end2_x, door_end2_y = door_line.bounds[2], door_line.bounds[3]

            door_x1, door_y1 = door_end1_x, door_end1_y
            door_x2, door_y2 = door_end2_x, door_end2_y

            if door_end1_x > door_end2_x:
                door_x1, door_y1 = door_end2_x, door_end2_y
                door_x2, door_y2 = door_end1_x, door_end1_y
            
            door_gap_x, door_gap_y = door_x2 - door_x1, door_y2 - door_y1
            door_a = door_y1 - door_gap_y / door_gap_x * door_x1

            for line in  filtered_walls_geojson['features']:
                line = geometry.shape(line['geometry'])
                line_end1_x, line_end1_y = line.bounds[0], line.bounds[1]
                line_end2_x, line_end2_y = line.bounds[2], line.bounds[3]

                line_x1, line_y1 = line_end1_x, line_end1_y
                line_x2, line_y2 = line_end2_x, line_end2_y

                if line_end1_x > line_end2_x:
                    line_x1, line_y1 = line_end2_x, line_end2_y
                    line_x2, line_y2 = line_end1_x, line_end1_y
                
                start_edge_check1 = 0.0001 > abs(abs(line_y1) - abs(door_gap_y / door_gap_x * line_x1 + door_a))
                start_edge_check2 = 0.0001 > abs(abs(line_y2) - abs(door_gap_y / door_gap_x * line_x2 + door_a))

                # filtering 된 wall lines 중에 door_line 함수에 있는 wall lines 들을 저장
                if start_edge_check1 and start_edge_check2:
                    line_feature = {
                        "type": "Feature",
                        "properties": {
                            "door_index": door_index
                            ,"id": room_index
                        },
                        "geometry":geometry.mapping(line)
                    }
                    result_geojson["features"].append(line_feature)
            
            # line과 해당 라인에 포함된 point와 filtered_walls_geojson으로 접하는 walls를 감지하는 로직 => return [result_yn, result_lines]
            line2_intersects_lines = shapely_functions.get_lines_from_point_and_line(line2, line2_intersect_point, filtered_walls_geojson['features'])

            if line2_intersects_lines[0]:
                # line2_intersects_lines[1] 에는 line2와 접하는 wall lines 들이 들어있음
                for line in line2_intersects_lines[1]:
                    line_feature = {
                        "type": "Feature",
                        "properties": {
                            "door_index": door_index
                            ,"id": room_index
                        },
                        "geometry":geometry.mapping(line)
                    }
                    result_geojson["features"].append(line_feature)

            # 결과가 없으면 스킵
            else:
                continue
            
            # add door_line
            geom_feature = {
                "type": "Feature",
                "properties": {
                    "door_index": door_index
                    ,"id": room_index
                },
                "geometry":geometry.mapping(door_line)
            }
            result_geojson["features"].append(geom_feature)

            if not line2_intersect_point:
                continue

            # door_point와 line2_intersect_point의 중간점을 기준으로 90도 직교, 45, 135 3개의 선분에서 접하는 벽을 더 추가
            x, y = (door_point.bounds[0]+line2_intersect_point.bounds[0])/2.0, (door_point.bounds[1]+line2_intersect_point.bounds[1])/2.0
            middle_room_point = geometry.Point(x, y)

            # save room index
            geom_feature = {
                "type": "Feature",
                "properties": {
                    "door_index": door_index
                    ,"id": room_index
                },
                "geometry":geometry.mapping(middle_room_point)
            }
            room_index_geojson["features"].append(geom_feature)

            # 중간점을 기준으로 선을 그린다 - 90도 직교
            rotated_line1_90 = shapely.affinity.rotate(orgin_rotated_line1, 90, origin=middle_room_point)
            rotated_line1_135 = shapely.affinity.rotate(orgin_rotated_line1, 135, origin=middle_room_point)
            rotated_line1_225 = shapely.affinity.rotate(orgin_rotated_line1, 225, origin=middle_room_point)








            # 90도 직교선에서 탐지되는 2개의 walls를 찾는 로직
            # line과 해당 라인에 포함된 point와 filtered_walls_geojson으로 접하는 walls를 감지하는 로직 => return [result_yn, result_lines]
            # line2_intersects_lines = shapely_functions.get_lines_from_point_and_line(rotated_line1_90, middle_room_point, filtered_walls_geojson['features'])

            # 해당 선과 교차하는 points를 찾는다
            rotated_line1_90_inters = shapely_functions.find_intersections_baseline_to_all(rotated_line1_90,filtered_walls_geojson['features'])

            # 중간점에서 가장가까운 point와 반대편 endpoint를 잇는 선으로 업데이트 한다
            shortest_distance = 100
            intersect_point_90_1 = geometry.Point()
            for point in rotated_line1_90_inters:
                if point.distance(middle_room_point) < shortest_distance:
                    shortest_distance = point_to_point_distance
                    intersect_point_90_1 = point

            # -----------intersect_point_90_1-----
            splited_rotated_line1_90 = shapely.ops.split(rotated_line1_90, intersect_point_90_1.buffer(min_point))
                    
            # 중간점을 포함하는 선분을 잘라서 선분 update
            for line in splited_rotated_line1_90:
                if middle_room_point.distance(line) < min_point:
                    rotated_line1_90 = line

            # 해당 선과 교차하는 points를 다시 구함
            rotated_line1_90_inters = shapely_functions.find_intersections_baseline_to_all(rotated_line1_90,filtered_walls_geojson['features'])

            # 첫번째 교차 point 이외에 중간점에서 가장 가까운 point를 찾는다
            intersect_point_90_2 = geometry.Point()
            distance_90_1 = 100
            for pt in rotated_line1_90_inters:
                # line2_end1과 중복되는 포인트는 무시
                if pt.distance(intersect_point_90_1) < min_point:
                    continue
                if pt.distance(intersect_point_90_1) < distance_90_1:
                    intersect_point_90_2 = pt
                    distance_90_1 = pt.distance(intersect_point_90_1)

            if not intersect_point_90_2:
                continue

            # 덮어씌우기
            splited_rotated_line1_90 = geometry.LineString([intersect_point_90_1, intersect_point_90_2])

            # line1_90에 접하는 2개의 wall line을 구함
            buffer_size=min_point
            for line in  filtered_walls_geojson['features']:
                line = geometry.shape(line['geometry'])
                if intersect_point_90_1.distance(line) < min_point:
                    # line과 해당 라인에 포함된 point와 filtered_walls_geojson으로 접하는 walls를 감지하는 로직 => return [result_yn, result_lines]
                    rotated_line_90_1_intersects_lines = shapely_functions.get_lines_from_point_and_line(line, intersect_point_90_1, filtered_walls_geojson['features'])

                    if rotated_line_90_1_intersects_lines[0]:
                        # rotated_line_90_1_intersects_lines[1] 에는 line와 접하는 wall lines 들이 들어있음
                        for line in rotated_line_90_1_intersects_lines[1]:
                            line_feature = {
                                "type": "Feature",
                                "properties": {
                                    "door_index": door_index
                                    ,"id": room_index
                                },
                                "geometry":geometry.mapping(line)
                            }
                            result_geojson["features"].append(line_feature)

                    # 결과가 없으면 스킵
                    else:
                        continue

                elif intersect_point_90_2.distance(line) < min_point:
                    # line과 해당 라인에 포함된 point와 filtered_walls_geojson으로 접하는 walls를 감지하는 로직 => return [result_yn, result_lines]
                    rotated_line_90_2_intersects_lines = shapely_functions.get_lines_from_point_and_line(line, intersect_point_90_2, filtered_walls_geojson['features'])

                    if rotated_line_90_2_intersects_lines[0]:
                        # rotated_line_90_2_intersects_lines[1] 에는 line와 접하는 wall lines 들이 들어있음
                        for line in rotated_line_90_2_intersects_lines[1]:
                            line_feature = {
                                "type": "Feature",
                                "properties": {
                                    "door_index": door_index
                                    ,"id": room_index
                                },
                                "geometry":geometry.mapping(line)
                            }
                            result_geojson["features"].append(line_feature)

                    # 결과가 없으면 스킵
                    else:
                        continue












            # 135도 직교선에서 탐지되는 2개의 walls를 찾는 로직
            # 해당 선과 교차하는 points를 찾는다
            rotated_line1_135_inters = shapely_functions.find_intersections_baseline_to_all(rotated_line1_135,filtered_walls_geojson['features'])

            # 중간점에서 가장가까운 point와 반대편 endpoint를 잇는 선으로 업데이트 한다
            shortest_distance = 100
            intersect_point_135_1 = geometry.Point()
            for point in rotated_line1_135_inters:
                if point.distance(middle_room_point) < shortest_distance:
                    shortest_distance = point_to_point_distance
                    intersect_point_135_1 = point

            # -----------intersect_point_135_1-----
            splited_rotated_line1_135 = shapely.ops.split(rotated_line1_135, intersect_point_135_1.buffer(min_point))
                    
            # 중간점을 포함하는 선분을 잘라서 선분 update
            for line in splited_rotated_line1_135:
                if middle_room_point.distance(line) < min_point:
                    rotated_line1_135 = line

            # 해당 선과 교차하는 points를 다시 구함
            rotated_line1_135_inters = shapely_functions.find_intersections_baseline_to_all(rotated_line1_135,filtered_walls_geojson['features'])

            # 첫번째 교차 point 이외에 중간점에서 가장 가까운 point를 찾는다
            intersect_point_135_2 = geometry.Point()
            distance_135_1 = 100
            for pt in rotated_line1_135_inters:
                # line2_end1과 중복되는 포인트는 무시
                if pt.distance(intersect_point_135_1) < min_point:
                    continue
                if pt.distance(intersect_point_135_1) < distance_135_1:
                    intersect_point_135_2 = pt
                    distance_135_1 = pt.distance(intersect_point_135_1)

            if not intersect_point_135_2:
                continue

            # 덮어씌우기
            splited_rotated_line1_135 = geometry.LineString([intersect_point_135_1, intersect_point_135_2])

            # line1_135에 접하는 2개의 wall line을 구함
            buffer_size=min_point
            for line in  filtered_walls_geojson['features']:
                line = geometry.shape(line['geometry'])
                if intersect_point_135_1.distance(line) < min_point:
                    # line과 해당 라인에 포함된 point와 filtered_walls_geojson으로 접하는 walls를 감지하는 로직 => return [result_yn, result_lines]
                    rotated_line_135_1_intersects_lines = shapely_functions.get_lines_from_point_and_line(line, intersect_point_135_1, filtered_walls_geojson['features'])

                    if rotated_line_135_1_intersects_lines[0]:
                        # rotated_line_135_1_intersects_lines[1] 에는 line와 접하는 wall lines 들이 들어있음
                        for line in rotated_line_135_1_intersects_lines[1]:
                            line_feature = {
                                "type": "Feature",
                                "properties": {
                                    "door_index": door_index
                                    ,"id": room_index
                                },
                                "geometry":geometry.mapping(line)
                            }
                            result_geojson["features"].append(line_feature)

                    # 결과가 없으면 스킵
                    else:
                        continue

                elif intersect_point_135_2.distance(line) < min_point:
                    # line과 해당 라인에 포함된 point와 filtered_walls_geojson으로 접하는 walls를 감지하는 로직 => return [result_yn, result_lines]
                    rotated_line_135_2_intersects_lines = shapely_functions.get_lines_from_point_and_line(line, intersect_point_135_2, filtered_walls_geojson['features'])

                    if rotated_line_135_2_intersects_lines[0]:
                        # rotated_line_135_2_intersects_lines[1] 에는 line와 접하는 wall lines 들이 들어있음
                        for line in rotated_line_135_2_intersects_lines[1]:
                            line_feature = {
                                "type": "Feature",
                                "properties": {
                                    "door_index": door_index
                                    ,"id": room_index
                                },
                                "geometry":geometry.mapping(line)
                            }
                            result_geojson["features"].append(line_feature)

                    # 결과가 없으면 스킵
                    else:
                        continue














            # 225도 직교선에서 탐지되는 2개의 walls를 찾는 로직
            # 해당 선과 교차하는 points를 찾는다
            rotated_line1_225_inters = shapely_functions.find_intersections_baseline_to_all(rotated_line1_225,filtered_walls_geojson['features'])

            # 중간점에서 가장가까운 point와 반대편 endpoint를 잇는 선으로 업데이트 한다
            shortest_distance = 100
            intersect_point_225_1 = geometry.Point()
            for point in rotated_line1_225_inters:
                if point.distance(middle_room_point) < shortest_distance:
                    shortest_distance = point_to_point_distance
                    intersect_point_225_1 = point

            # -----------intersect_point_225_1-----
            splited_rotated_line1_225 = shapely.ops.split(rotated_line1_225, intersect_point_225_1.buffer(min_point))
                    
            # 중간점을 포함하는 선분을 잘라서 선분 update
            for line in splited_rotated_line1_225:
                if middle_room_point.distance(line) < min_point:
                    rotated_line1_225 = line

            # 해당 선과 교차하는 points를 다시 구함
            rotated_line1_225_inters = shapely_functions.find_intersections_baseline_to_all(rotated_line1_225,filtered_walls_geojson['features'])

            # 첫번째 교차 point 이외에 중간점에서 가장 가까운 point를 찾는다
            intersect_point_225_2 = geometry.Point()
            distance_225_1 = 100
            for pt in rotated_line1_225_inters:
                # line2_end1과 중복되는 포인트는 무시
                if pt.distance(intersect_point_225_1) < min_point:
                    continue
                if pt.distance(intersect_point_225_1) < distance_225_1:
                    intersect_point_225_2 = pt
                    distance_225_1 = pt.distance(intersect_point_225_1)

            if not intersect_point_225_2:
                continue

            # 덮어씌우기
            splited_rotated_line1_225 = geometry.LineString([intersect_point_225_1, intersect_point_225_2])

            # line1_225에 접하는 2개의 wall line을 구함
            buffer_size=min_point
            for line in  filtered_walls_geojson['features']:
                line = geometry.shape(line['geometry'])
                if intersect_point_225_1.distance(line) < min_point:
                    # line과 해당 라인에 포함된 point와 filtered_walls_geojson으로 접하는 walls를 감지하는 로직 => return [result_yn, result_lines]
                    rotated_line_225_1_intersects_lines = shapely_functions.get_lines_from_point_and_line(line, intersect_point_225_1, filtered_walls_geojson['features'])

                    if rotated_line_225_1_intersects_lines[0]:
                        # rotated_line_225_1_intersects_lines[1] 에는 line와 접하는 wall lines 들이 들어있음
                        for line in rotated_line_225_1_intersects_lines[1]:
                            line_feature = {
                                "type": "Feature",
                                "properties": {
                                    "door_index": door_index
                                    ,"id": room_index
                                },
                                "geometry":geometry.mapping(line)
                            }
                            result_geojson["features"].append(line_feature)

                    # 결과가 없으면 스킵
                    else:
                        continue

                elif intersect_point_225_2.distance(line) < min_point:
                    # line과 해당 라인에 포함된 point와 filtered_walls_geojson으로 접하는 walls를 감지하는 로직 => return [result_yn, result_lines]
                    rotated_line_225_2_intersects_lines = shapely_functions.get_lines_from_point_and_line(line, intersect_point_225_2, filtered_walls_geojson['features'])

                    if rotated_line_225_2_intersects_lines[0]:
                        # rotated_line_135_2_intersects_lines[1] 에는 line와 접하는 wall lines 들이 들어있음
                        for line in rotated_line_225_2_intersects_lines[1]:
                            line_feature = {
                                "type": "Feature",
                                "properties": {
                                    "door_index": door_index
                                    ,"id": room_index
                                },
                                "geometry":geometry.mapping(line)
                            }
                            result_geojson["features"].append(line_feature)

                    # 결과가 없으면 스킵
                    else:
                        continue





            print("success:index" + room_index)

        # except Exception as error:
        #     print("failed:index" + room_index + " message:" + str(error))

create_geojson.write_geojson(directory_path + 'result.geojson', result_geojson)
create_geojson.write_geojson(directory_path + 'room_index.geojson', room_index_geojson)
