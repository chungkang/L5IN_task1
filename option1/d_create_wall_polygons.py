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

directory_path = config.directory_path_result # directory path of saving result

# initialize empty geojson
origin_geojson = copy.deepcopy(create_geojson.geojson_custom)

# interested layer list
layer_list = config.layer_list

# explode all blocks 2 times
for flag_ref in msp.query("INSERT"):
    flag_ref.explode()

for flag_ref in msp.query("INSERT"):
    flag_ref.explode()

idx = 0
# get all layers include fassade
layer_list.append('AUSBAU - Darstellungen - Fassade')
for layer in layer_list:
    for e in msp.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='" + layer + "']"):
        # Convert DXF entity into a GeoProxy object:
        geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)
        
        each_feature = {
            "type": "Feature",
            "properties": {
                "index": idx
            },
            "geometry": geo_proxy.__geo_interface__
        }
        origin_geojson["features"].append(each_feature)
        idx += 1

# write custom defined CRS geojson
create_geojson.write_geojson(directory_path + 'all_walls_original.geojson', origin_geojson)

# read created geojson / reprojection to EPSG:32632 / write reprojected geojson
loaded_geojson = geopandas.read_file(directory_path + 'original.geojson')
loaded_geojson = loaded_geojson.to_crs('EPSG:32632')
loaded_geojson.to_file(directory_path + 'all_walls_original_EPSG32632.geojson', driver='GeoJSON')

# load EPSG32632 geojson
with open(directory_path + 'all_walls_original_EPSG32632.geojson') as f:
    epsg32632_geojson = json.load(f)



# outer wall detection - concave hull, alpha shape
# initialize empty geojson
outer_wall_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

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

wall_alpha_shape = alphashape.alphashape(non_dup_wall_points, 0.112)

wall_feature = {
    "type": "Feature",
    "properties": {
    },
    "geometry": geometry.mapping(wall_alpha_shape)
}
outer_wall_geojson["features"].append(wall_feature)

create_geojson.write_geojson(directory_path + 'outer_wall.geojson', outer_wall_geojson)


# outer_wall.geojson - filtered_room_polygon.geojson
wall_polygon = wall_alpha_shape

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
