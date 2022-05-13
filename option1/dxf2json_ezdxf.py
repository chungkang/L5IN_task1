import ezdxf
import ezdxf.addons.geo as geo
import json
import geopandas
from shapely import geometry, ops, wkt
import matplotlib.pyplot as plt

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

# counting entities of dxf file => index 
idx = 0

# 1st exploding of blocks(except door blocks)
for flag_ref in msp.query("INSERT[layer!='AUSBAU - Objekte - Tueren']"):
    exploded_e = flag_ref.explode()

    # exploded door layer lines(no actual door)
    for e in exploded_e.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='AUSBAU - Objekte - Tueren']"):
        geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)
        each_feature = {
            "type": "Feature",
            "properties": {
                "index": idx,
                "layer": 'AUSBAU - Objekte - Tueren',
                "category": "door"
            },
            "geometry": geo_proxy.__geo_interface__
        }
        geojson_format["features"].append(each_feature)
        idx += 1

# for flag_ref in msp.query("INSERT[layer!='AUSBAU - Objekte - Tueren']"):
#     exploded_e = flag_ref.explode()

# explode door block and give door ID
door_block_id = 0
for flag_ref in msp.query("INSERT[layer=='AUSBAU - Objekte - Tueren']"):
    
    exploded_door=flag_ref.explode()
    for e in exploded_door.query("LINE LWPOLYLINE SPLINE POLYLINE"):
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



with open('option1\\option1_EPSG32632.geojson') as f:
    gj = json.load(f)
polygon_lines_geojson = gj['features']

buffer_size = 0.001

doors = []
for each in polygon_lines_geojson:
    if each['properties']['category']=='door':
        linestring =  str(each['geometry']['coordinates']).replace('], [', ',').replace(', ',' ').replace('[','').replace(']','')
        doors.append(wkt.loads('LINESTRING ('+linestring+')').buffer(buffer_size))

# If the command above fails, try union first and then buffer:
# buff_union = shapely.ops.unary_union([b1,b2,t1,t2]).buffer(buffer_size)

door_buff_union = ops.unary_union(doors)

result_door_buff_union = geopandas.GeoSeries(door_buff_union).__geo_interface__
result_door_buff_union["crs"]=({ "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }})

with open('option1\\option1_result_door_union.geojson', 'wt', encoding='utf8') as fp:
    json.dump(result_door_buff_union, fp, indent=2)



# # Extracting all the interior geometries
# # Idea taken from here: https://stackoverflow.com/a/21922058/8667016
# all_internal_geoms = [geom for geom in door_buff_union.interiors]

# # Fishing out the interior geometry we really need
# internal_geom = all_internal_geoms[0]

# # Plotting results
# # Code taken from here: https://stackoverflow.com/a/56140178/8667016
# plt.plot(*internal_geom.xy)












# divede lines with category / merge lines which have intersection each other
# with open('option1\\option1_EPSG32632.geojson') as f:
#     gj = json.load(f)
# lines_geojson = gj['features']

# doors = []
# walls = []
# for each in lines_geojson:
#     if each['properties']['category']=='door':
#         doors.append(each['geometry']['coordinates'])
#     else:
#         walls.append(each['geometry']['coordinates'])

# # merge lines with shapely.ops.linemerge
# merged_doors = ops.linemerge(doors)
# merged_walls = ops.linemerge(walls)

# # change shapely geometry to geojson format
# result_doors = geopandas.GeoSeries(merged_doors).__geo_interface__
# result_walls = geopandas.GeoSeries(merged_walls).__geo_interface__
# result_doors["crs"].append('{ "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }}')
# result_walls["crs"].append('{ "type": "name", "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }}')

# # write custom geojson
# with open( 'option1\\option1_merged_doors.geojson', 'wt', encoding='utf8') as fp:
#     json.dump(result_doors, fp, indent=2)

# with open( 'option1\\option1_merged_walls.geojson', 'wt', encoding='utf8') as fp:
#     json.dump(result_walls, fp, indent=2)