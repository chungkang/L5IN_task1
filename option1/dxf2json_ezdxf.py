import ezdxf
import ezdxf.addons.geo as geo
import json
import geopandas
from shapely import geometry
import alphashape
from descartes import PolygonPatch

import matplotlib.pyplot as plt
import numpy as np


# source file
# dxf_name = "layer_HCU_D_106_Grundriss_4OG_moved_V2"
dxf_name = "rev_vert_HCU_D_106_Grundriss_4OG_moved_V2"

# loading dxf file
doc = ezdxf.readfile("dxf\\"+ dxf_name + ".dxf")

# get modelspace / 모형
msp = doc.modelspace()

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
                # ,"AUSBAU - Objekte - Tueren" 
                ,"DARSTELLUNGEN - Aufsichtslinien" 
                ,"keine" 
                ,"ROHBAU - Darstellungen - Brandwand" 
                # ,"ROHBAU - Darstellungen - Treppen" 
                ,"ROHBAU - Darstellungen - Waende" 
                ,"ROHBAU - Darstellungen - Waende - Mauerwerk" 
]

# door_id
door_block_id = 0
# entity index 
idx = 0

# 1st exploding of blocks(except door blocks)
for flag_ref in msp.query("INSERT[layer!='AUSBAU - Objekte - Tueren']"):
    exploded_e = flag_ref.explode()
    
    # exploded door layer lines(door layer, but not door block, door components)
    for e in exploded_e.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='AUSBAU - Objekte - Tueren']"):
        geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)
        each_feature = {
            "type": "Feature",
            "properties": {
                "index": idx,
                "layer": 'AUSBAU - Objekte - Tueren',
                "category": "door",
                "door_id": door_block_id
            },
            "geometry": geo_proxy.__geo_interface__
        }
        geojson_format["features"].append(each_feature)
        idx += 1

    door_block_id += 1

# explode door block and give door ID
for flag_ref in msp.query("INSERT[layer=='AUSBAU - Objekte - Tueren']"):
    
    exploded_door=flag_ref.explode()

    each_door_line = []

    for e in exploded_door.query("LINE LWPOLYLINE SPLINE POLYLINE"):
        geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)
        
        each_door_line.append(geo_proxy.__geo_interface__['coordinates'])
    multi_door_line = geometry.MultiLineString(each_door_line)

    each_feature = {
                    "type": "Feature",
                    "properties":  {
                                        "index": idx,
                                        "layer": 'AUSBAU - Objekte - Tueren',
                                        "category": "door",
                                        "door_id": door_block_id
                                    },
                    "geometry": geometry.mapping(multi_door_line)
                    }
    geojson_format["features"].append(each_feature)
    
    door_block_id += 1
    idx += 1


# explode all left blocks
for flag_ref in msp.query("INSERT"):
    exploded_e = flag_ref.explode()
    
    # exploded door layer lines(door layer, but not door block, door components)
    for e in exploded_e.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='AUSBAU - Objekte - Tueren']"):
        geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)
        each_feature = {
            "type": "Feature",
            "properties": {
                "index": idx,
                "layer": 'AUSBAU - Objekte - Tueren',
                "category": "door",
                "door_id": door_block_id
            },
            "geometry": geo_proxy.__geo_interface__
        }
        geojson_format["features"].append(each_feature)
        idx += 1

    door_block_id += 1


for layer in layer_list:
    for e in msp.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='" + layer + "']"):
        # Convert DXF entity into a GeoProxy object:
        geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)
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







# door multilinestring to convex_hull polygon
# initialize empty geojson
door_polygon_geojson = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
        "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }
	},
    "features": []
}

# initialize empty geojson
door_point_geojson = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
        "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }
	},
    "features": []
}

door_polygon_geojson_idx = 0
door_point_geojson_idx = 0
# lines 중에서 door_id 있는 것들만 추출
for line in epsg32632_geojson['features']:
    if line['properties']['door_id']!=None and line['geometry']:
        shapely_line = geometry.shape(line['geometry'])
        outer_door_polygon = shapely_line.convex_hull
        if outer_door_polygon.geom_type == 'LineString': continue
        door_points = list(outer_door_polygon.exterior.coords)
        each_feature = {
            "type": "Feature",
            "properties": {
                "index": door_polygon_geojson_idx
            },
            "geometry": geometry.mapping(outer_door_polygon)
        }
        door_polygon_geojson["features"].append(each_feature)
        door_polygon_geojson_idx += 1

        for x in door_points:  
            each_feature = {
                "type": "Feature",
                "properties": {
                    "index": door_point_geojson_idx
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": list(x)
                }
            }
            door_point_geojson["features"].append(each_feature)
            door_point_geojson_idx += 1

# result_door_buff_union["crs"]=({ "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }})

with open('option1\\option1_door_polygon.geojson', 'wt', encoding='utf8') as fp:
    json.dump(door_polygon_geojson, fp, indent=2)

with open('option1\\option1_door_point.geojson', 'wt', encoding='utf8') as fp:
    json.dump(door_point_geojson, fp, indent=2)





# # find intersections between doors and walls
# # initialize empty geojson
# intersections_geojson = {
#     "type": "FeatureCollection",
# 	"crs": {
# 	    "type": "name",
#         "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }
# 	},
#     "features": []
# }

# intersection_idx = 0
# buffer_size = 0.01

# # doors
# for d_line in door_geojson['features']:
#     if d_line['geometry']:
#         door = geometry.shape(d_line['geometry']).buffer(buffer_size)
#         # walls
#         walls_geojson = epsg32632_geojson['features']
#         for w_line in walls_geojson:
#             if w_line['properties']['category']=='wall' and w_line['geometry']:
#                 wall = geometry.shape(w_line['geometry']).buffer(buffer_size)
#                 intersections = door.intersection(wall)
                
#                 intersections_geometry = geometry.mapping(intersections)

#                 if intersections_geometry['coordinates']:
#                     # points.append(intersections)
#                     each_feature = {
#                         "type": "Feature",
#                         "properties": {
#                             "index": intersection_idx
#                         },
#                         "geometry": intersections_geometry
#                     }
#                     intersections_geojson["features"].append(each_feature)
#                     intersection_idx += 1

# with open('option1\\option1_intersections.geojson', 'wt', encoding='utf8') as fp:
#     json.dump(intersections_geojson, fp, indent=2)


from shapely.geometry import Point, LineString

line = LineString([(-9765787.9981184918, 5488940.9749489054), (-9748582.8016368076, 5488402.1275707092)])
point = Point(-9763788.9782693591, 5488878.3678984242)

line.within(point)  # False
line.distance(point)  # 7.765244949417793e-11
line.distance(point) < 1e-8  # True






# outer wall detection - concave hull, alpha shape
# initialize empty geojson
outer_wall_geojson = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
        "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }
	},
    "features": []
}

wall_points = []
for lines in epsg32632_geojson['features']:
    if lines['geometry']:
        shapely_lines = lines['geometry']['coordinates']
        for each_line in shapely_lines:
            if type(each_line[0]) == float:
                wall_points.append(tuple(each_line))
            else:
                for point in each_line:
                    wall_points.append(tuple(point))                

non_dup_wall_points = []
[non_dup_wall_points.append(x) for x in wall_points if x not in non_dup_wall_points]

wall_alpha_shape = alphashape.alphashape(non_dup_wall_points, .18)

wall_feature = {
    "type": "Feature",
    "properties": {
    },
    "geometry": geometry.mapping(wall_alpha_shape)
}
outer_wall_geojson["features"].append(wall_feature)

with open('option1\\option1_outer_wall.geojson', 'wt', encoding='utf8') as fp:
    json.dump(outer_wall_geojson, fp, indent=2)