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

# Get the geo location information from the DXF file:
# geo_data = msp.get_geodata()

# if geo_data:
#     # Get transformation matrix and epsg code:
#     m, epsg = geo_data.get_crs_transformation()
# else:
#     # Identity matrix for DXF files without geo reference data:
#     m = ezdxf.math.Matrix44()

# initialize empty geojson
geojson_format = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
		"properties": {
			"name": "+proj=tmerc +lat_0=0 +lon_0=9 +k=1 +x_0=3500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
		}
	},
    "features": []
}

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
                ,"AUSBAU - Objekte - Tueren"
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
        geojson_format["features"].append(each_feature)
        idx += 1

    door_block_id += 1

# # 1st exploding of blocks(except door blocks)
# for flag_ref in msp.query("INSERT[layer!='AUSBAU - Objekte - Tueren']"):
#     exploded_e = flag_ref.explode()
    
#     # exploded door layer lines(door layer, but not door block, door components)
#     for e in exploded_e.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='AUSBAU - Objekte - Tueren']"):
#         geo_proxy = geo.proxy(e, distance=0, force_line_string=True)
        
#         # skip short lines
#         line = geometry.shape(geo_proxy.__geo_interface__)
#         if line.length < min_length:
#             continue

#         each_feature = {
#             "type": "Feature",
#             "properties": {
#                 "index": idx,
#                 "layer": 'AUSBAU - Objekte - Tueren',
#                 "category": "door",
#                 "door_id": door_block_id
#             },
#             "geometry": geo_proxy.__geo_interface__
#         }
#         geojson_format["features"].append(each_feature)
#         idx += 1

#     door_block_id += 1

# # explode door block and give door ID
# for flag_ref in msp.query("INSERT[layer=='AUSBAU - Objekte - Tueren']"):
#     exploded_door=flag_ref.explode()
#     each_door_line = []

#     for e in exploded_door.query("LINE LWPOLYLINE SPLINE POLYLINE"):
#         geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)

#         # skip short lines
#         line = geometry.shape(geo_proxy.__geo_interface__)
#         if line.length < min_length:
#             continue

#         each_door_line.append(geo_proxy.__geo_interface__['coordinates'])

#     multi_door_line = geometry.MultiLineString(each_door_line)

#     each_feature = {
#                     "type": "Feature",
#                     "properties":  {
#                                         "index": idx,
#                                         "layer": 'AUSBAU - Objekte - Tueren',
#                                         "category": "door",
#                                         "door_id": door_block_id
#                                     },
#                     "geometry": geometry.mapping(multi_door_line)
#                     }
#     geojson_format["features"].append(each_feature)
    
#     door_block_id += 1
#     idx += 1


# # explode all left blocks
# for flag_ref in msp.query("INSERT"):
#     exploded_e = flag_ref.explode()
    
#     # exploded door layer lines(door layer, but not door block, door components)
#     for e in exploded_e.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='AUSBAU - Objekte - Tueren']"):
#         geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)
        
#         # skip short lines
#         line = geometry.shape(geo_proxy.__geo_interface__)
#         if line.length < min_length:
#             continue

#         each_feature = {
#             "type": "Feature",
#             "properties": {
#                 "index": idx,
#                 "layer": 'AUSBAU - Objekte - Tueren',
#                 "category": "door",
#                 "door_id": str(door_block_id)
#             },
#             "geometry": geo_proxy.__geo_interface__
#         }
#         geojson_format["features"].append(each_feature)
#         idx += 1

#     door_block_id += 1


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
        geojson_format["features"].append(each_feature)
        idx += 1

# write custom defined CRS geojson
with open( 'option1\\option1.geojson', 'wt', encoding='utf8') as fp:
    json.dump(geojson_format, fp, indent=2)

# read created geojson / reprojection to EPSG:32632 / write reprojected geojson
loaded_geojson = geopandas.read_file('option1\\option1.geojson')
loaded_geojson = loaded_geojson.to_crs("EPSG:32632")
loaded_geojson.to_file("option1\\option1_EPSG32632.geojson", driver='GeoJSON')





# load EPSG32632 geojson
with open('option1\\option1_EPSG32632.geojson') as f:
    epsg32632_geojson = json.load(f)






# door multipoints to convex_hull polygon
door_dict = {}
for lines in epsg32632_geojson['features']:
    door_points = []
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

door_polygon_geojson = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
        "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }
	},
    "features": []
}
door_points_geojson = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
        "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }
	},
    "features": []
}

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


with open('option1\\option1_door_polygon.geojson', 'wt', encoding='utf8') as fp:
    json.dump(door_polygon_geojson, fp, indent=2)
with open('option1\\option1_door_points.geojson', 'wt', encoding='utf8') as fp:
    json.dump(door_points_geojson, fp, indent=2)



# index 0 door polygon for test
index0_polygon_geojson = {
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

with open('option1\\index0_door_polygon.geojson', 'wt', encoding='utf8') as fp:
    json.dump(index0_polygon_geojson, fp, indent=2)


# # find intersections + split lines with intersections
# # get all lines from geojson
# all_lines = []
# for lines in epsg32632_geojson['features']:
#     if lines['properties']['door_id']==None and lines['geometry']:
#         all_lines.append(geometry.shape(lines['geometry']))

# # get all the points from end of lines
# endpts = [(geometry.Point(list(line.coords)[0]), geometry.Point(list(line.coords)[-1])) for line  in all_lines]
# # flatten the resulting list to a simple list of points
# endpts= [pt for sublist in endpts  for pt in sublist] 

# # find intersections
# inters = []
# for line1,line2 in  itertools.combinations(all_lines, 2):
#   if  line1.intersects(line2):
#     inter = line1.intersection(line2)
#     if "Point" == inter.type:
#         inters.append(inter)
#     elif "MultiPoint" == inter.type:
#         inters.extend([pt for pt in inter])
#     elif "MultiLineString" == inter.type:
#         multiLine = [line for line in inter]
#         first_coords = multiLine[0].coords[0]
#         last_coords = multiLine[len(multiLine)-1].coords[1]
#         inters.append(geometry.Point(first_coords[0], first_coords[1]))
#         inters.append(geometry.Point(last_coords[0], last_coords[1]))
#     elif "GeometryCollection" == inter.type:
#         for geom in inter:
#             if "Point" == geom.type:
#                 inters.append(geom)
#             elif "MultiPoint" == geom.type:
#                 inters.extend([pt for pt in geom])
#             elif "MultiLineString" == geom.type:
#                 multiLine = [line for line in geom]
#                 first_coords = multiLine[0].coords[0]
#                 last_coords = multiLine[len(multiLine)-1].coords[1]
#                 inters.append(geometry.Point(first_coords[0], first_coords[1]))
#                 inters.append(geometry.Point(last_coords[0], last_coords[1]))

# # remove duplicate of intersection points
# result = endpts.extend([pt for pt in inters  if pt not in endpts])

# intersections_geojson = {
#     "type": "FeatureCollection",
# 	"crs": {
# 	    "type": "name",
#         "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }
# 	},
#     "features": []
# }
# for i, pt in enumerate(result):
#     points_feature = {
#         "type": "Feature",
#         "properties": {
#             "index": i
#         },
#         "geometry": geometry.mapping(pt)
#     }
#     intersections_geojson["features"].append(points_feature)

# with open('option1\\option1_intersections.geojson', 'wt', encoding='utf8') as fp:
#     json.dump(intersections_geojson, fp, indent=2)























"""


# find lines with door points
# initialize empty geojson
intersections_geojson = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
        "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }
	},
    "features": []
}

intersection_idx = 0
# door buffer point랑 교점이 있으면 다 저장
for line in epsg32632_geojson['features']:
    if line['geometry']:
        # 라인 1줄-door point 전부와 비교
        line_shp = geometry.shape(line['geometry'])
        
        intersect_YN = 'N'
        # door line단위 for문 - multiPoints
        for door in door_points_geojson["features"]:
            # point 단위 for문
            door_shp = geometry.shape(door['geometry'])
            if line_shp.distance(door_shp.buffer(0.01)) < 1e-8:
                intersect_YN = 'Y'
                continue
    
        if intersect_YN == 'N':
            continue

        each_feature = {
            "type": "Feature",
            "properties": {
                "index": intersection_idx
            },
            "geometry":geometry.mapping(line_shp)
        }
        intersections_geojson["features"].append(each_feature)
        intersection_idx += 1

with open('option1\\option1_intersections.geojson', 'wt', encoding='utf8') as fp:
    json.dump(intersections_geojson, fp, indent=2)



"""




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