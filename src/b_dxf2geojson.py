import sys
import ezdxf
from ezdxf import recover
import ezdxf.addons.geo as geo
import copy
import geopandas
import a_setting as setting
import module.create_geojson as create_geojson # load functions for creating geojson

# loading dxf file
DXF_NAME =setting.dxf_name
DIRECTORY_PATH = setting.directory_path
LAYER_LIST = setting.layer_list
DOOR_LAYER = setting.door_layer_name

# Umlaut ae, ue, oe doesn't work with ezdxf.readfile()=>use recover module https://ezdxf.mozman.at/docs/drawing/recover.html
try:
    doc, auditor = recover.readfile(DXF_NAME)
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

# get layout / plan - layout page
# plan = doc.layout('16 - plan 2.OG_1_100')

# initialize empty geojson
origin_geojson = copy.deepcopy(create_geojson.geojson_custom)

# block_id
block_id = 0
# entity index 
idx = 0

# explode all blocks
for flag_ref in msp.query("INSERT"):
    exploded_e = flag_ref.explode()
    
    # exploded door layer lines(door layer, but not door block, door components)
    for e in exploded_e.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='" + DOOR_LAYER + "']"):
        geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)
        each_feature = create_geojson.create_geojson_feature(idx, DOOR_LAYER, "door", str(block_id), geo_proxy.__geo_interface__)
        origin_geojson["features"].append(each_feature)
        idx += 1
    block_id += 1


for layer in LAYER_LIST:
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
create_geojson.write_geojson(DIRECTORY_PATH + 'original_CRS.geojson', origin_geojson)

# read created geojson / reprojection to EPSG:32632 / write reprojected geojson
# loaded_geojson = geopandas.read_file(DIRECTORY_PATH + 'original_CRS.geojson')
# loaded_geojson = loaded_geojson.to_crs(config.target_CRS)
# loaded_geojson.to_file(DIRECTORY_PATH + 'converted_CRS.geojson', driver='GeoJSON')