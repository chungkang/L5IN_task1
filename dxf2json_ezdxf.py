import ezdxf
import ezdxf.addons.geo as geo
import json
import geopandas
# import pyproj

# source file
# dxf = "./removed_HCU_D_104_Grundriss_2OG_moved.dxf"

# dxf = "./copied_HCU_D_104_Grundriss_2OG_moved.dxf"

dxf = "./layername_HCU_D_105_Grundriss_3OG_moved.dxf"

# loading dxf file
doc = ezdxf.readfile(dxf)

# get modelspace / 모형
msp = doc.modelspace()

# get layout / plan 레이아웃 페이지: 주석 등
# plan = doc.layout('16 - plan 2.OG_1_100')

# explode blocks
for flag_ref in msp.query('INSERT'):
    # print(str(flag_ref))
    flag_ref.explode()

for flag_ref in msp.query('INSERT'):
    # print(str(flag_ref))
    flag_ref.explode()

# Get the geo location information from the DXF file:
geo_data = msp.get_geodata()

if geo_data:
    # Get transformation matrix and epsg code:
    m, epsg = geo_data.get_crs_transformation()
else:
    # Identity matrix for DXF files without geo reference data:
    m = ezdxf.math.Matrix44()

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

layer_list = [
                "AUSBAU - Bezeichnung - Parkplatz" 
                ,"AUSBAU - Darstellungen - Akustik" 
                ,"AUSBAU - Darstellungen - Daemmung" 
                ,"AUSBAU - Darstellungen - Daemmung-brennbar_B1" 
                ,"AUSBAU - Darstellungen - Doppelbodenschottungen" 
                ,"AUSBAU - Darstellungen - Fassade" 
                ,"AUSBAU - Darstellungen - Fassade-Bemassung" 
                ,"AUSBAU - Darstellungen - Gelaender" 
                ,"AUSBAU - Darstellungen - Stahlbau" 
                ,"AUSBAU - Darstellungen - Trockenbau" 
                ,"AUSBAU - Objekte - Aufzuege" 
                ,"AUSBAU - Objekte - Tueren" 
                ,"DARSTELLUNGEN - Aufsichtslinien" 
                ,"keine" 
                ,"ROHBAU - Darstellungen - Brandwand" 
                ,"ROHBAU - Darstellungen - Treppen" 
                ,"ROHBAU - Darstellungen - Waende" 
                ,"ROHBAU - Darstellungen - Waende - Mauerwerk" 
]

# counting entities of dxf file  
idx = 0

# Supported DXF entities are:
# POINT as “Point”
# LINE as “LineString”
# LWPOLYLINE as “LineString” if open and “Polygon” if closed
# POLYLINE as “LineString” if open and “Polygon” if closed, supports only 2D and 3D polylines, POLYMESH and POLYFACE are not supported
# SOLID, TRACE, 3DFACE as “Polygon”
# CIRCLE, ARC, ELLIPSE and SPLINE by approximation as “LineString” if open and “Polygon” if closed
# HATCH as “Polygon”, holes are supported
# # extract each entity
# # CIRCLE ARC ELLIPSE 문의 위치 나중에
for layer in layer_list:
    for e in msp.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='" + layer + "']"):
        # Convert DXF entity into a GeoProxy object:
        geo_proxy = geo.proxy(e)

        # Export GeoJSON data:
        # name = e.dxf.layer + '_' + str(idx) + '.geojson'
        # # with open(TRACK_DATA / name, 'wt', encoding='utf8') as fp:
        # with open( name, 'wt', encoding='utf8') as fp:
        #     json.dump(geo_proxy.__geo_interface__, fp, indent=2)

        each_feature = {
            "type": "Feature",
            "properties": {
                "index": idx,
                "layer": layer 
            },
            "geometry": geo_proxy.__geo_interface__
        }

        geojson_format["features"].append(each_feature)
        
        idx += 1

# write custom defined CRS geojson
with open( 'testfile.geojson', 'wt', encoding='utf8') as fp:
    json.dump(geojson_format, fp, indent=2)

# read created geojson / reprojection to EPSG:32632 / write reprojected geojson
loaded_geojson = geopandas.read_file('testfile.geojson')
loaded_geojson = loaded_geojson.to_crs("EPSG:32632")
loaded_geojson.to_file("testfile_EPSG32632.geojson", driver='GeoJSON')
