import ezdxf
import ezdxf.addons.geo as geo
import json
import geopandas
from shapely.ops import polygonize
import shapely

# source file
# dxf_name = "layername_HCU_D_105_Grundriss_3OG_moved"
dxf_name = "layer_HCU_D_106_Grundriss_4OG_moved_V2"

# loading dxf file
doc = ezdxf.readfile("option1\\"+ dxf_name + ".dxf")

# get modelspace / 모형
msp = doc.modelspace()

# get layout / plan - layout page
# plan = doc.layout('16 - plan 2.OG_1_100')

# myText = open(r'my_text_file.txt','w')
# myText.write(str(msp.query('INSERT')))
# myText.close()

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

# counting entities of dxf file  
idx = 0

for block in msp.query("INSERT[layer=='AUSBAU - Objekte - Tueren']"):
    name = block.dxf.name
    insert = block.dxf.insert
    x = insert.x
    y = insert.y
    # angle = block.dxf.insert.angle             # radian
    angle_deg = insert.angle_deg     # degrees
    magnitude = insert.magnitude
    
    gap = 0.1
    point_1 = [x,y]
    point_2 = [x+gap,y]
    point_3 = [x+gap,y-gap]
    point_4 = [x,y-gap]

    each_feature = {
            "type": "Feature",
            "properties": {
                "index": idx,
                "layer": 'door',
                "category": 'door_start'
            },
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    point_1,
                    point_2,
                    point_3,
                    point_4,
                    point_1
                ]
            }
        }
    geojson_format["features"].append(each_feature)
    idx += 1


# explode blocks
# for flag_ref in msp.query("INSERT[layer!='AUSBAU - Objekte - Tueren']"):
#     # print(str(flag_ref))
#     flag_ref.explode()

for flag_ref in msp.query("INSERT[layer!='AUSBAU - Objekte - Tueren']"):
    flag_ref.explode()

for flag_ref in msp.query("INSERT"):
    flag_ref.explode()

for layer in layer_list:
    for e in msp.query("LINE LWPOLYLINE SPLINE POLYLINE[layer=='" + layer + "']"):
        # Convert DXF entity into a GeoProxy object:
        geo_proxy = geo.proxy(e)

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

# Polyline으로 된 door 제거

# write custom defined CRS geojson
with open( 'testfile.geojson', 'wt', encoding='utf8') as fp:
    json.dump(geojson_format, fp, indent=2)

# read created geojson / reprojection to EPSG:32632 / write reprojected geojson
loaded_geojson = geopandas.read_file('testfile.geojson')
loaded_geojson = loaded_geojson.to_crs("EPSG:32632")
loaded_geojson.to_file("testfile_EPSG32632.geojson", driver='GeoJSON')


# shapely merge test
gdf = geopandas.GeoDataFrame.from_features(geojson_format)
polygons = geopandas.GeoSeries(polygonize(gdf.geometry))

geojson_polygons = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
		"properties": {
			"name": "+proj=tmerc +lat_0=0 +lon_0=9 +k=1 +x_0=3500000 +y_0=0 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
		}
	},
    "features": []
}

for polygon in polygons:
    g1 = shapely.wkt.loads(polygon.wkt)
    g2 = shapely.geometry.mapping(g1)

    each_feature = {
        "type": "Feature",
        "properties": {
            "index": idx,
            "layer": 'layer',
            "category": 'category'
        },
        "geometry": g2
    }

    geojson_polygons["features"].append(each_feature)
    
    idx += 1

with open( 'shapely_test.geojson', 'wt', encoding='utf8') as fp:
    json.dump(geojson_polygons, fp, indent=2)