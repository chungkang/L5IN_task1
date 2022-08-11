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

# minimum length of lines
min_length = 0.2

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
                ,"AUSBAU - Darstellungen - Fassade" 
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
                ,"ROHBAU - Darstellungen - Waende - Mauerwerk" 
                # ,"ROHBAU - Darstellungen - Ansichtslinien" 
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
create_geojson.write_geojson('option1\\option1.geojson', origin_geojson)

# read created geojson / reprojection to EPSG:32632 / write reprojected geojson
loaded_geojson = geopandas.read_file('option1\\option1.geojson')
loaded_geojson = loaded_geojson.to_crs("EPSG:32632")
loaded_geojson.to_file("option1\\option1_EPSG32632.geojson", driver='GeoJSON')





# load EPSG32632 geojson
with open('option1\\option1_EPSG32632.geojson') as f:
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

door_polygon_geojson_idx = 0

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
            "index": door_polygon_geojson_idx
        },
        "geometry": geometry.mapping(door_polygon)
    }
    door_polygon_geojson["features"].append(door_polygon_feature)
    door_polygon_geojson_idx += 1

    # polygon의 테두리 points를 뽑는다
    door_points = geometry.MultiPoint(door_polygon.exterior.coords)
    door_points_feature = {
        "type": "Feature",
        "properties": {
            "index": door_polygon_geojson_idx
        },
        "geometry": geometry.mapping(door_points)
    }
    door_points_geojson["features"].append(door_points_feature)
    door_polygon_geojson_idx += 1

create_geojson.write_geojson('option1\\option1_door_polygon.geojson', door_polygon_geojson)
# create_geojson.write_geojson('option1\\option1_door_points.geojson', door_points_geojson)
# create_geojson.write_geojson('option1\\option1_wall_lines.geojson', wall_lines_geojson)

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
        "geometry": door_polygon_geojson['features'][1]['geometry']
    }]
}

create_geojson.write_geojson('option1\\door1_polygon.geojson', door1_polygon_geojson)



door1_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
door1_idx = 0
# 	1. Start from 1 edge of door polygon (door1_point1)
door1_point1_coord = door_polygon_geojson['features'][1]['geometry']["coordinates"][0][0]
door_point1 = geometry.Point(door1_point1_coord[0], door1_point1_coord[1])
each_feature = {
                "type": "Feature",
                "properties": {
                    "index": door1_idx
                    ,"name": 'door1_point1'
                },
                "geometry":geometry.mapping(door_point1)
            }
door1_geojson["features"].append(each_feature)
door1_idx+=1

# 2. Filter all the wall lines which is close from door1_point1
door1_filtered_walls_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
door1_filtered_walls_geojson_idx = 0
for line in epsg32632_geojson['features']:
    if line['properties']['category']!='door' and line['geometry']:
        line_shp = geometry.shape(line['geometry'])
        if door_point1.distance(line_shp) < 5:
            each_feature = {
                "type": "Feature",
                "properties": {
                    "index": door_polygon_geojson_idx
                },
                "geometry": geometry.mapping(line_shp)
            }
            door1_filtered_walls_geojson["features"].append(each_feature)
            door1_filtered_walls_geojson_idx += 1

create_geojson.write_geojson('option1\\door1_filtered_walls.geojson', door1_filtered_walls_geojson)

# 3. get intersection line from the door point1(line1)
line1 = geometry.LineString()
for line in door1_filtered_walls_geojson['features']:
    line_shp = geometry.shape(line['geometry'])
    if line_shp.distance(door_point1) < 1e-3:
        each_feature = {
            "type": "Feature",
            "properties": {
                "index": door1_idx
                ,"name": 'line1'
            },
            "geometry":geometry.mapping(line_shp)
        }
        door1_geojson["features"].append(each_feature)
        door1_idx+=1
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

# 5. get another side wall line(line2)
# rotated_line1과 주변 모든 wall line의 intersections를 찾음
all_lines = []
for line in door1_filtered_walls_geojson['features']:
    if line['geometry']:
        all_lines.append(geometry.shape(line['geometry']))

# get all the points from end of lines
# endpts = [(geometry.Point(list(line.coords)[0]), geometry.Point(list(line.coords)[-1])) for line  in all_lines]
# flatten the resulting list to a simple list of points
# endpts= [pt for sublist in endpts  for pt in sublist] 

# find intersections
inters = []
for line in  all_lines:
    if rotated_line1.intersects(line):
        inter = rotated_line1.intersection(line)
        if "Point" == inter.type:
            inters.append(inter)
        elif "MultiPoint" == inter.type:
            inters.extend([pt for pt in inter])
        elif "MultiLineString" == inter.type:
            multiLine = [line for line in inter]
            first_coords = multiLine[0].coords[0]
            last_coords = multiLine[len(multiLine)-1].coords[1]
            inters.append(geometry.Point(first_coords[0], first_coords[1]))
            inters.append(geometry.Point(last_coords[0], last_coords[1]))
        elif "GeometryCollection" == inter.type:
            for geom in inter:
                if "Point" == geom.type:
                    inters.append(geom)
                elif "MultiPoint" == geom.type:
                    inters.extend([pt for pt in geom])
                elif "MultiLineString" == geom.type:
                    multiLine = [line for line in geom]
                    first_coords = multiLine[0].coords[0]
                    last_coords = multiLine[len(multiLine)-1].coords[1]
                    inters.append(geometry.Point(first_coords[0], first_coords[1]))
                    inters.append(geometry.Point(last_coords[0], last_coords[1]))

# # remove duplicate of intersection points
# result = endpts.extend([pt for pt in inters if pt not in endpts])

rotated_line1_intersections_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)
# for i, pt in enumerate(result):
#     points_feature = {
#         "type": "Feature",
#         "properties": {
#             "index": i
#         },
#         "geometry": geometry.mapping(pt)
#     }
#     rotated_line1_intersections_geojson["features"].append(points_feature)

for pt in inters:
    points_feature = {
        "type": "Feature",
        "properties": {
            "index": i
        },
        "geometry": geometry.mapping(pt)
    }
    rotated_line1_intersections_geojson["features"].append(points_feature)

# create_geojson.write_geojson('option1\\rotated_line1_intersections.geojson', rotated_line1_intersections_geojson)

# door1_point1에서 가장 가까운 점을 찾음
shortest_distance = 100
line1_end1 = geometry.Point()
for point in rotated_line1_intersections_geojson['features']:
    point_shp = geometry.shape(point['geometry'])
    point_to_point_distance = point_shp.distance(door_point1)
    if point_to_point_distance < shortest_distance and point_to_point_distance > 1e-3:
        shortest_distance = point_to_point_distance
        line1_end1 = point_shp

point_feature = {
    "type": "Feature",
    "properties": {
        "name": "line2_shortest_intersection" 
    },
    "geometry": geometry.mapping(line1_end1)
}
door1_geojson["features"].append(point_feature)

# shortest_point, door_point1 로 rotated_line1을 split해서 rotated_line1_splited 의 여러 라인을 만듦(rotated_lines)
splited_rotated_line1 = shapely.ops.split(rotated_line1, geometry.MultiPoint([line1_end1, door_point1]).buffer(1e-3))

# 짧은 라인(벽안에 있는 라인)을 무시하고 room을 가로지르는 line을 추출(rotated_line1)
line_length = 0
for line in splited_rotated_line1:
    if line.length > line_length:
        rotated_line1 = line
        line_length = line.length

rotated_line1_feature = {
        "type": "Feature",
        "properties": {
            "index": door1_idx
            ,"name": 'rotated_line1'
        },
        "geometry": geometry.mapping(rotated_line1)
    }
door1_geojson["features"].append(rotated_line1_feature)

# rotated_line1과 wall lines들이 접하는 points를 구함
inters = []
for line in  all_lines:
    if rotated_line1.intersects(line):
        inter = rotated_line1.intersection(line)
        if "Point" == inter.type:
            inters.append(inter)
        elif "MultiPoint" == inter.type:
            inters.extend([pt for pt in inter])
        elif "MultiLineString" == inter.type:
            multiLine = [line for line in inter]
            first_coords = multiLine[0].coords[0]
            last_coords = multiLine[len(multiLine)-1].coords[1]
            inters.append(geometry.Point(first_coords[0], first_coords[1]))
            inters.append(geometry.Point(last_coords[0], last_coords[1]))
        elif "GeometryCollection" == inter.type:
            for geom in inter:
                if "Point" == geom.type:
                    inters.append(geom)
                elif "MultiPoint" == geom.type:
                    inters.extend([pt for pt in geom])
                elif "MultiLineString" == geom.type:
                    multiLine = [line for line in geom]
                    first_coords = multiLine[0].coords[0]
                    last_coords = multiLine[len(multiLine)-1].coords[1]
                    inters.append(geometry.Point(first_coords[0], first_coords[1]))
                    inters.append(geometry.Point(last_coords[0], last_coords[1]))

rotated_line1_intersections_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

for pt in inters:
    points_feature = {
        "type": "Feature",
        "properties": {
            "index": i
        },
        "geometry": geometry.mapping(pt)
    }
    rotated_line1_intersections_geojson["features"].append(points_feature)

create_geojson.write_geojson('option1\\rotated_line1_intersections_new.geojson', rotated_line1_intersections_geojson)

# 문의 시작 point에서 가장 가까운 point를 구함
# door1_point1에서 rotated_line1_intersections_geojson 에 있는 point 중에 가장 가까운 점을 구함
shortest_distance = 100
shortest_point = geometry.Point()
for point in rotated_line1_intersections_geojson['features']:
    point_shp = geometry.shape(point['geometry'])
    point_to_point_distance = point_shp.distance(door_point1)
    if point_to_point_distance < shortest_distance and point_to_point_distance > 1e-3:
        shortest_distance = point_to_point_distance
        shortest_point = point_shp

point_feature = {
    "type": "Feature",
    "properties": {
        "name": "line2_shortest_intersection" 
    },
    "geometry": geometry.mapping(shortest_point)
}
door1_geojson["features"].append(point_feature)

# 해당 shortest_point와 접하는 wall line을 찾음(line2)
line2 = geometry.LineString()
for line in door1_filtered_walls_geojson['features']:
    line_shp = geometry.shape(line['geometry'])
    if line_shp.distance(shortest_point) < 1e-3:
        each_feature = {
            "type": "Feature",
            "properties": {
                "index": door1_idx
                ,"name": 'line2'
            },
            "geometry":geometry.mapping(line_shp)
        }
        door1_geojson["features"].append(each_feature)
        door1_idx+=1
        line2 = line_shp

# line1에 접하는 모든 wall line 간의 intersection points
# door_point에서 가장 가까운 점(line1_end1)
# line1_end1에서 선분을 잘라서 line1를 덮어씌움

# line1_end1에서 가장가까운 intersection point를 구함(line1_end2)
# line1_end1과 line1_end2로 이루어진 선분으로 line1를 덮어씌움


# line2에 접하는 모든 wall line 간의 intersection points를 구함
# shortest_point에서 가장 가까운 점을 구함(line2_end1)
# line2_end1에서 선분을 잘라서 line2를 덮어씌움
# line2_end1에서 가장가까운 intersection point를 구함(line2_end2)
# line2_end1과 line2_end2로 이루어진 선분으로 line2를 덮어씌움

# line1_end1, line1_end2, line2_end1, line2_end2의 4개의 points에서 접하는 모든 선분을 추출
# 해당 line으로 닫히는 polygon을 구함


create_geojson.write_geojson('option1\\door1.geojson', door1_geojson)











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

# with open('option1\\option1_outer_wall.geojson', 'wt', encoding='utf8') as fp:
#     json.dump(outer_wall_geojson, fp, indent=2)