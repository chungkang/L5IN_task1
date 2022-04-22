import ezdxf
import ezdxf.addons.geo as geo
import json
import geopandas
from shapely.ops import polygonize

# source file
dxf_name = "layer_HCU_D_106_Grundriss_4OG_moved_V2"

# loading dxf file
doc = ezdxf.readfile("dxf\\"+ dxf_name + ".dxf")

# get modelspace / 모형
msp = doc.modelspace()

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
                ,"keine" 
                ,"ROHBAU - Darstellungen - Brandwand" 
                # ,"ROHBAU - Darstellungen - Treppen" 
                ,"ROHBAU - Darstellungen - Waende" 
                ,"ROHBAU - Darstellungen - Waende - Mauerwerk" 
]

# counting entities of dxf file => index 
idx = 0


# door block start point
point_idx = 0

geojson_door_format = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
		"properties": {
			"name": "+proj=tmerc +lat_0=0 +lon_0=9 +k=1 +x_0=3500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
		}
	},
    "features": []
}

for insert in msp.query("INSERT[layer=='AUSBAU - Objekte - Tueren']"):
    block = insert.dxf.insert
    angle = block.angle
    angle_deg = block.angle_deg
    magnitude = block.magnitude
    magnitude_square = block.magnitude_square
    magnitude_xy = block.magnitude_xy
    x = block.x
    y = block.y

    each_feature = {
        "type": "Feature",
        "properties": {
            "index": point_idx,
            "layer": 'AUSBAU - Objekte - Tueren',
            "category": 'door_point'
        },
        "geometry": {
            "type": "Point",
            "coordinates": [x, y]
        }
    }

    geojson_door_format["features"].append(each_feature)
    point_idx += 1

# write custom defined CRS geojson
with open( 'option2\\option2_door_point.geojson', 'wt', encoding='utf8') as fp:
    json.dump(geojson_door_format, fp, indent=2)

# read created geojson / reprojection to EPSG:32632 / write reprojected geojson
loaded_geojson = geopandas.read_file('option2\\option2_door_point.geojson')
loaded_geojson = loaded_geojson.to_crs("EPSG:32632")
loaded_geojson.to_file("option2\\option2_door_pointEPSG32632.geojson", driver='GeoJSON')

# explode all the blocks
for flag_ref in msp.query("INSERT"):
    flag_ref.explode()

for flag_ref in msp.query("INSERT"):
    flag_ref.explode()

for layer in layer_list:
    for e in msp.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='" + layer + "']"):
        # Convert DXF entity into a GeoProxy object:
        geo_proxy = geo.proxy(e, distance=0.1, force_line_string=True)

        category = ""
        if "waende" in layer or "Waende" in layer or "trockenbau" in layer or "Trockenbau" in layer:
            category = "wall"
        elif "treppen" in layer or "Treppen" in layer:
            category = "stair"
        elif "tueren" in layer or "Tueren" in layer:
            category = "door"
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
with open( 'option2\\option2.geojson', 'wt', encoding='utf8') as fp:
    json.dump(geojson_format, fp, indent=2)

# read created geojson / reprojection to EPSG:32632 / write reprojected geojson
loaded_geojson = geopandas.read_file('option2\\option2.geojson')
loaded_geojson = loaded_geojson.to_crs("EPSG:32632")
loaded_geojson.to_file("option2\\option2_EPSG32632.geojson", driver='GeoJSON')

# lineString to polygon [door]
# linestrings = gdf[gdf.geometry.type == "LineString"]
doors =  loaded_geojson[loaded_geojson.category == "door"]
polygons = geopandas.GeoSeries(polygonize(doors.geometry))
polygons = polygons.set_crs("EPSG:32632")
polygons.to_file("option2\\option2_poligonized_door.geojson", driver='GeoJSON')