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
import module.create_geojson as create_geojson


# source file
# dxf_name = "rev_HCU_D_102_Grundriss_1OG_moved"
# dxf_name = "rev_HCU_D_104_Grundriss_2OG_moved"
# dxf_name = "rev_HCU_D_105_Grundriss_3OG_moved"
dxf_name = "rev_HCU_D_106_Grundriss_4OG_moved_V2"

# loading dxf file
doc = ezdxf.readfile("dxf\\"+ dxf_name + ".dxf")

# get modelspace
msp = doc.modelspace()

# minimum length of lines(ignore short lines)
min_length = 0.05

# minimum length as a point
min_point = 1e-3

# get layout / plan - layout page
# plan = doc.layout('16 - plan 2.OG_1_100')

# initialize empty geojson
origin_geojson = copy.deepcopy(create_geojson.geojson_custom)

# interested layer list
layer_list = [
                "AUSBAU - Bezeichnung - Parkplatz" 
                ,"AUSBAU - Darstellungen - Akustik" 
                ,"AUSBAU - Darstellungen - Daemmung" 
                ,"AUSBAU - Darstellungen - Daemmung-brennbar_B1" 
                # ,"AUSBAU - Darstellungen - Doppelbodenschottungen" 
                # ,"AUSBAU - Darstellungen - Fassade" 
                ,"AUSBAU - Darstellungen - Fassade-Bemassung"
                ,"AUSBAU - Darstellungen - Fassade-Bemaßung"
                ,"AUSBAU - Darstellungen - Gelaender" 
                ,"AUSBAU - Darstellungen - Stahlbau" 
                ,"AUSBAU - Darstellungen - Trennwaende"
                ,"AUSBAU - Darstellungen - Trockenbau" 
                ,"AUSBAU - Darstellungen - Waende - Mauerwerk"
                # ,"AUSBAU - Objekte - Aufzuege" 
                # ,"AUSBAU - Objekte - Tueren"
                ,"DARSTELLUNGEN - Aufsichtslinien"
                # ,"DARSTELLUNGEN - Brandwand"
                # ,"ROHBAU - Darstellungen - Unterzug - Deckenversprung - Oeffnung"
                ,"keine" 
                ,"ROHBAU - Darstellungen - Brandwand" 
                # ,"ROHBAU - Darstellungen - Treppen" 
                ,"ROHBAU - Darstellungen - Waende"
                ,"ROHBAU - Darstellungen - Decken" 
                ,"ROHBAU - Darstellungen - Waende - Mauerwerk" 
                # ,"ROHBAU - Darstellungen - Ansichtslinien"
                ,"wall"
]

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
        
        category = ""
        if "waende" in layer or "Waende" in layer or "trockenbau" in layer or "Trockenbau" in layer:
            category = "wall"
        elif "treppen" in layer or "Treppen" in layer:
            category = "stair"
        else:
            category = "etc"

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
create_geojson.write_geojson('option1_walls_individual\\option1.geojson', origin_geojson)

# read created geojson / reprojection to EPSG:32632 / write reprojected geojson
loaded_geojson = geopandas.read_file('option1_walls_individual\\option1.geojson')
loaded_geojson = loaded_geojson.to_crs("EPSG:32632")
loaded_geojson.to_file("option1_walls_individual\\option1_EPSG32632.geojson", driver='GeoJSON')





# load EPSG32632 geojson
with open('option1_walls_individual\\option1_EPSG32632.geojson') as f:
    epsg32632_geojson = json.load(f)


# door multipoints to convex_hull polygon
# + get wall lines(none door layers)
wall_lines_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

wall_line_idx = 0

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

    # polygon의 테두리 points를 뽑는다
    door_points = geometry.MultiPoint(door_polygon.exterior.coords)
    door_points_feature = {
        "type": "Feature",
        "properties": {
            "index": door_polygon_idx
        },
        "geometry": geometry.mapping(door_points)
    }
    door_points_geojson["features"].append(door_points_feature)
    door_polygon_idx += 1

create_geojson.write_geojson('option1_walls_individual\\option1_door_polygon.geojson', door_polygon_geojson)
create_geojson.write_geojson('option1_walls_individual\\option1_door_points.geojson', door_points_geojson)
# create_geojson.write_geojson('option1_walls_individual\\option1_wall_lines.geojson', wall_lines_geojson)

# test용 door 인덱스
sample_door_index = 187
sample_door_point_index = 0

# index 0 door polygon for test
door1_polygon_geojson = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
        "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }
	},
    "features": [{
        "type": "Feature",
        "properties": {
            "index": 1
        },
        "geometry": door_polygon_geojson['features'][sample_door_index]['geometry']
    }]
}

create_geojson.write_geojson('option1_walls_individual\\door1_polygon.geojson', door1_polygon_geojson)



door1_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
door1_idx = 0
# 	1. Start from 1 edge of door polygon (door1_point1)
door1_point1_coord = door_polygon_geojson['features'][sample_door_index]['geometry']["coordinates"][0][sample_door_point_index]
door_point1 = geometry.Point(door1_point1_coord[0], door1_point1_coord[1])
# each_feature = {
#                 "type": "Feature",
#                 "properties": {
#                     "index": door1_idx
#                     ,"name": 'door1_point1'
#                 },
#                 "geometry":geometry.mapping(door_point1)
#             }
# door1_geojson["features"].append(each_feature)
# door1_idx+=1


distance_from_door_point = 10
# 2. Filter all the wall lines which is close from door1_point1
filtered_walls_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
filtered_walls_idx = 0
for line in epsg32632_geojson['features']:
    if line['properties']['category']!='door' and line['geometry']:
        line_shp = geometry.shape(line['geometry'])
        if door_point1.distance(line_shp) < distance_from_door_point:
            each_feature = {
                "type": "Feature",
                "properties": {
                    "index": filtered_walls_idx
                },
                "geometry": geometry.mapping(line_shp)
            }
            filtered_walls_geojson["features"].append(each_feature)
            filtered_walls_idx += 1

temp_filtered_walls_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
# add properties of door juction line to feature of filtered_walls_geojson
for line in filtered_walls_geojson["features"]:
    door_juction_yn = 'N'
    for point in door_points_geojson["features"]:
        # filter door_points which is close to the door_point
        if door_point1.distance(geometry.shape(point['geometry'])) > distance_from_door_point:
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

create_geojson.write_geojson('option1_walls_individual\\filtered_walls.geojson', filtered_walls_geojson)

# 3. get intersection line from the door point1(line1)
line1 = geometry.LineString()
for line in filtered_walls_geojson['features']:
    line_shp = geometry.shape(line['geometry'])
    if line_shp.distance(door_point1) < min_point:
        line1 = line_shp

# 4. Make orthogonal line from line1(rotated_line1)
rotated_line1 = shapely.affinity.rotate(line1, 90, origin=door_point1)
l_coords = list(rotated_line1.coords)
EXTRAPOL_RATIO = 3
p1 = l_coords[-2:][0]
p2 = l_coords[-2:][1]
a = (p1[0]-EXTRAPOL_RATIO*(p2[0]-p1[0]), p1[1]-EXTRAPOL_RATIO*(p2[1]-p1[1]))
b = (p1[0]+EXTRAPOL_RATIO*(p2[0]-p1[0]), p1[1]+EXTRAPOL_RATIO*(p2[1]-p1[1]))
rotated_line1 = geometry.LineString([a,b])

# rotated_line1과 주변 wall lines(door_juction)의 intersections를 찾음
rotated_line1_inters = []
for line in  filtered_walls_geojson['features']:
    if line["properties"]["door_juction"] == "Y":
        line = geometry.shape(line['geometry'])
        if rotated_line1.intersects(line):
            inter = rotated_line1.intersection(line)
            if "Point" == inter.type:
                rotated_line1_inters.append(inter)
            elif "MultiPoint" == inter.type:
                rotated_line1_inters.extend([pt for pt in inter])
            elif "MultiLineString" == inter.type:
                multiLine = [line for line in inter]
                first_coords = multiLine[0].coords[0]
                last_coords = multiLine[len(multiLine)-1].coords[1]
                rotated_line1_inters.append(geometry.Point(first_coords[0], first_coords[1]))
                rotated_line1_inters.append(geometry.Point(last_coords[0], last_coords[1]))
            elif "GeometryCollection" == inter.type:
                for geom in inter:
                    if "Point" == geom.type:
                        rotated_line1_inters.append(geom)
                    elif "MultiPoint" == geom.type:
                        rotated_line1_inters.extend([pt for pt in geom])
                    elif "MultiLineString" == geom.type:
                        multiLine = [line for line in geom]
                        first_coords = multiLine[0].coords[0]
                        last_coords = multiLine[len(multiLine)-1].coords[1]
                        rotated_line1_inters.append(geometry.Point(first_coords[0], first_coords[1]))
                        rotated_line1_inters.append(geometry.Point(last_coords[0], last_coords[1]))

# door1_point1에서 가장 가까운 점을 찾음
shortest_distance = 100
point_in_wall = geometry.Point()
for point in rotated_line1_inters:
    point_to_point_distance = point.distance(door_point1)
    if point_to_point_distance < shortest_distance and point_to_point_distance > min_point:
        shortest_distance = point_to_point_distance
        point_in_wall = point

# door_point1을 기준으로 point_in_wall과 대칭하는 점을 만듦(new_point)
new_point = geometry.Point(door_point1.coords[0][0]*2-point_in_wall.coords[0][0], door_point1.coords[0][1]*2-point_in_wall.coords[0][1])

# door_point1에서 시작하여 new_point 방향으로 뻗어나가는 line을 그려서 rotated_line1를 update
line_coords = [(door_point1.coords[0][0], door_point1.coords[0][1]),(new_point.coords[0][0], new_point.coords[0][1])]
EXTRAPOL_RATIO = 50
line_p1 = line_coords[-2:][0]
line_p2 = line_coords[-2:][1]
line_b = (line_p1[0]+EXTRAPOL_RATIO*(line_p2[0]-line_p1[0]), line_p1[1]+EXTRAPOL_RATIO*(line_p2[1]-line_p1[1]))
rotated_line1 = geometry.LineString([(door_point1.coords[0][0], door_point1.coords[0][1]), line_b])

# rotated_line1_feature = {
#         "type": "Feature",
#         "properties": {
#             "index": door1_idx
#             ,"name": 'rotated_line1'
#         },
#         "geometry": geometry.mapping(rotated_line1)
#     }
# door1_geojson["features"].append(rotated_line1_feature)

# 업데이트된 rotated_line1과 wall lines들이 접하는 points를 업데이트(rotated_line1_inters 업데이트)
rotated_line1_inters = []

for line in  filtered_walls_geojson['features']:
    line = geometry.shape(line['geometry'])
    if rotated_line1.intersects(line):
        inter = rotated_line1.intersection(line)
        if "Point" == inter.type:
            rotated_line1_inters.append(inter)
        elif "MultiPoint" == inter.type:
            rotated_line1_inters.extend([pt for pt in inter])
        elif "GeometryCollection" == inter.type:
            for geom in inter:
                if "Point" == geom.type:
                    rotated_line1_inters.append(geom)
                elif "MultiPoint" == geom.type:
                    rotated_line1_inters.extend([pt for pt in geom])

# door1_point1에서 rotated_line1_inters 에 있는 point 중에 가장 가까운 점을 구함(반대편 벽에 접하는 line2_intersect_point)
shortest_distance = 100
line2_intersect_point = geometry.Point()
for point in rotated_line1_inters:
    point_to_point_distance = point.distance(door_point1)
    if point_to_point_distance < shortest_distance and point_to_point_distance > min_point:
        shortest_distance = point_to_point_distance
        line2_intersect_point = point

# line2_intersect_point와 접하는 wall line을 찾음(line2)
line2 = geometry.LineString()
for line in filtered_walls_geojson['features']:
    line_shp = geometry.shape(line['geometry'])
    if line_shp.distance(line2_intersect_point) < min_point:
        line2 = line_shp

# line1에 접하는 모든 wall line 간의 intersection points(line1_inters)
line1_inters = []
for line in  filtered_walls_geojson['features']:
    line = geometry.shape(line['geometry'])
    if line1.intersects(line):
        inter = line1.intersection(line)
        if "Point" == inter.type:
            line1_inters.append(inter)
        elif "MultiPoint" == inter.type:
            line1_inters.extend([pt for pt in inter])
        elif "GeometryCollection" == inter.type:
            for geom in inter:
                if "Point" == geom.type:
                    line1_inters.append(geom)
                elif "MultiPoint" == geom.type:
                    line1_inters.extend([pt for pt in geom])

# line1_inters중에 door_point1에서 가장 가까운 점(line1_end1)
line1_end1 = geometry.Point()
distance_line1_end1 = 100
for pt in line1_inters:
    if pt.distance(door_point1) < distance_line1_end1:
        line1_end1 = pt
        distance_line1_end1 = pt.distance(door_point1)

# line1_end1 로 line1을 split해서 line1 의 여러 라인을 만듦(line1_lines)
splited_line1 = shapely.ops.split(line1, line1_end1.buffer(min_point))
        
# line1_lines의 라인중 door_point1을 포함하는 line을 추출해서 line1에 덮어 씌움
for line in splited_line1:
    if door_point1.distance(line) < min_point:
        line1 = line

# 업데이트된 line1과 접하는 wall line 간의 intersection points를 다시 구함(updated_line1_inters)
updated_line1_inters = []
for line in  filtered_walls_geojson['features']:
    line = geometry.shape(line['geometry'])
    if line.intersects(line1):
        inter = line.intersection(line1)
        if "Point" == inter.type:
            updated_line1_inters.append(inter)
        elif "MultiPoint" == inter.type:
            updated_line1_inters.extend([pt for pt in inter])
        elif "GeometryCollection" == inter.type:
            for geom in inter:
                if "Point" == geom.type:
                    updated_line1_inters.append(geom)
                elif "MultiPoint" == geom.type:
                    updated_line1_inters.extend([pt for pt in geom])

# line1_end1에서 가장가까운 line1_inters를 구함(line1_end2), 
line1_end2 = geometry.Point()
distance_line1_end2 = 100
for pt in updated_line1_inters:
    # line1_end1과 중복되는 포인트는 무시
    if pt.distance(line1_end1) < min_point:
        continue
    if pt.distance(line1_end1) < distance_line1_end2:
        line1_end2 = pt
        distance_line1_end2 = pt.distance(line1_end1)

# line1을 geojson에 저장
line1_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
line1_feature = {
    "type": "Feature",
    "properties": {
        "name": 'line1'
    },
    "geometry":geometry.mapping(line1)
}
line1_geojson["features"].append(line1_feature)
create_geojson.write_geojson('option1_walls_individual\\line1_test.geojson', line1_geojson)

# line1_end1과 line1_end2로 이루어진 선분으로 line1를 덮어씌움
line1 = geometry.LineString([line1_end1, line1_end2])







# line2에 접하는 모든 wall line 간의 intersection points(line2_inters)
line2_inters = []
for line in  filtered_walls_geojson['features']:
    line = geometry.shape(line['geometry'])
    if line.intersects(line2):
        inter = line.intersection(line2)
        if "Point" == inter.type:
            line2_inters.append(inter)
        elif "MultiPoint" == inter.type:
            line2_inters.extend([pt for pt in inter])
        elif "GeometryCollection" == inter.type:
            for geom in inter:
                if "Point" == geom.type:
                    line2_inters.append(geom)
                elif "MultiPoint" == geom.type:
                    line2_inters.extend([pt for pt in geom])


# line2_inters중에 line2_intersect_point에서 가장 가까운 점(line2_end1)
line2_end1 = geometry.Point()
distance_line2_end1 = 100
for pt in line2_inters:
    if pt.distance(line2_intersect_point) < distance_line2_end1:
        line2_end1 = pt
        distance_line2_end1 = pt.distance(line2_intersect_point)

# line2_end1 로 line2을 split해서 line2 의 여러 라인을 만듦(line2_lines)
splited_line2 = shapely.ops.split(line2, line2_end1.buffer(min_point))
        
# line2_lines의 라인중 line2_intersect_point을 포함하는 line을 추출해서 line2에 덮어 씌움
for line in splited_line2:
    if line2_intersect_point.distance(line) < min_point:
        line2 = line

# line2 gejson test
line2_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
line2_feature = {
    "type": "Feature",
    "properties": {
        "name": 'line2'
    },
    "geometry":geometry.mapping(line2)
}
line2_geojson["features"].append(line2_feature)

# 업데이트된 line2과 접하는 wall line 간의 intersection points를 다시 구함(updated_line2_inters)
updated_line2_inters = []
for line in  filtered_walls_geojson['features']:
    line = geometry.shape(line['geometry'])
    if line2.intersects(line):
        inter = line2.intersection(line)
        if "Point" == inter.type:
            updated_line2_inters.append(inter)
        elif "MultiPoint" == inter.type:
            updated_line2_inters.extend([pt for pt in inter])
        elif "GeometryCollection" == inter.type:
            for geom in inter:
                if "Point" == geom.type:
                    updated_line2_inters.append(geom)
                elif "MultiPoint" == geom.type:
                    updated_line2_inters.extend([pt for pt in geom])

# intersections_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
for pt in updated_line2_inters:
    points_feature = {
        "type": "Feature",
        "properties": {
            "index": i
        },
        "geometry": geometry.mapping(pt)
    }
    line2_geojson["features"].append(points_feature)
create_geojson.write_geojson('option1_walls_individual\\line2_test.geojson', line2_geojson)

# line2_end1에서 가장가까운 line2_inters를 구함(line2_end2), 
line2_end2 = geometry.Point()
distance_line2_end2 = 100
for pt in updated_line2_inters:
    # line2_end1과 중복되는 포인트는 무시
    if pt.distance(line2_end1) < min_point:
        continue
    if pt.distance(line2_end1) < distance_line2_end2:
        line2_end2 = pt
        distance_line2_end2 = pt.distance(line2_end1)

# line2_end1과 line2_end2로 이루어진 선분으로 line2를 덮어씌움
line2 = geometry.LineString([line2_end1, line2_end2])



# 4개의 endpoints에서 접하는 walls로 polygon 만드는 로직
lines_from_4_edges = copy.deepcopy(create_geojson.geojson_EPSG32632)
lines_4 = []
buffer_size=min_point
# line1_end1, line1_end2, line2_end1, line2_end2의 4개의 points에서 접하는 모든 선분을 추출
for line in  filtered_walls_geojson['features']:
    line = geometry.shape(line['geometry'])
    if line1_end1.distance(line) < min_point or line1_end2.distance(line) < min_point or line2_end1.distance(line) < min_point or line2_end2.distance(line) < min_point:
        line_feature = {
            "type": "Feature",
            "properties": {
                "index": door1_idx
                ,"name": 'lines for polygon'
            },
            "geometry":geometry.mapping(line)
        }
        lines_from_4_edges["features"].append(line_feature)

        geom_feature = {
            "type": "Feature",
            "properties": {
                "index": 'room_idx'
            },
            "geometry":geometry.mapping(line)
        }
        door1_geojson["features"].append(geom_feature)

create_geojson.write_geojson('option1_walls_individual\\door1.geojson', door1_geojson)





# # outer wall detection - concave hull, alpha shape
# # initialize empty geojson
# outer_wall_geojson = {
#     "type": "FeatureCollection",
# 	"crs": {
# 	    "type": "name",
#         "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }
# 	},
#     "features": []
# }

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

# wall_alpha_shape = alphashape.alphashape(non_dup_wall_points, 0.3)

# wall_feature = {
#     "type": "Feature",
#     "properties": {
#     },
#     "geometry": geometry.mapping(wall_alpha_shape)
# }
# outer_wall_geojson["features"].append(wall_feature)

# with open('option1_walls_individual\\option1_outer_wall.geojson', 'wt', encoding='utf8') as fp:
#     json.dump(outer_wall_geojson, fp, indent=2)