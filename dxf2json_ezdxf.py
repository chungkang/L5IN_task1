import ezdxf
import ezdxf.addons.geo as geo
import json
# import geopandas

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

# for flag_ref in msp.query('INSERT'):
#     # print(str(flag_ref))
#     flag_ref.explode()

# Get the geo location information from the DXF file:
geo_data = msp.get_geodata()

if geo_data:
    # Get transformation matrix and epsg code:
    m, epsg = geo_data.get_crs_transformation()
else:
    # Identity matrix for DXF files without geo reference data:
    m = ezdxf.math.Matrix44()

# counting entities of dxf file  
idx = 0

# initialize empty geojson
geojson_format = {
    "type": "FeatureCollection",
    "crs":
    {
        "type": "name",
        "properties":
        {
        }
    },
    "features": []
}
# geojson_format = {
#     "type": "FeatureCollection",
#     "crs":
#     {
#         "type": "name",
#         "properties":
#         {
#             "name": "EPSG: 8395"
#         }
#     },
#     "features": []
# }


# get lines of layer
# lines = msp.query('LINE[layer=="01"]')
# lines = msp.query('LINE[layer=="MyLayer"]')
# all_lines_by_color = msp.query('LINE').groupby('color')
# lines_with_color_1 = all_lines_by_color.get(1, [])

# delete entities
# line = msp.add_line((0, 0), (1, 0))
# msp.delete_entity(line)
# line.destroy()

# get attribute value
# linetype = entity.dxf.linetype
# entity.dxf.layer = "MyLayer"

# Supported DXF entities are:
# POINT as “Point”
# LINE as “LineString”
# LWPOLYLINE as “LineString” if open and “Polygon” if closed
# POLYLINE as “LineString” if open and “Polygon” if closed, supports only 2D and 3D polylines, POLYMESH and POLYFACE are not supported
# SOLID, TRACE, 3DFACE as “Polygon”
# CIRCLE, ARC, ELLIPSE and SPLINE by approximation as “LineString” if open and “Polygon” if closed
# HATCH as “Polygon”, holes are supported

# extract each entity
# CIRCLE ARC ELLIPSE 문의 위치 나중에  
for e in msp.query("""LINE LWPOLYLINE SPLINE POLYLINE[
                                                    layer=="AUSBAU - Bezeichnung - Parkplatz" 
                                                    |layer=="AUSBAU - Darstellungen - Akustik" 
                                                    |layer=="AUSBAU - Darstellungen - Daemmung" 
                                                    |layer=="AUSBAU - Darstellungen - Daemmung-brennbar_B1" 
                                                    |layer=="AUSBAU - Darstellungen - Doppelbodenschottungen" 
                                                    |layer=="AUSBAU - Darstellungen - Fassade" 
                                                    |layer=="AUSBAU - Darstellungen - Fassade-Bemassung" 
                                                    |layer=="AUSBAU - Darstellungen - Gelaender" 
                                                    |layer=="AUSBAU - Darstellungen - Stahlbau" 
                                                    |layer=="AUSBAU - Darstellungen - Trockenbau" 
                                                    |layer=="AUSBAU - Objekte - Aufzuege" 
                                                    |layer=="AUSBAU - Objekte - Tueren" 
                                                    |layer=="DARSTELLUNGEN - Aufsichtslinien" 
                                                    |layer=="keine" 
                                                    |layer=="ROHBAU - Darstellungen - Brandwand" 
                                                    |layer=="ROHBAU - Darstellungen - Treppen" 
                                                    |layer=="ROHBAU - Darstellungen - Waende" 
                                                    |layer=="ROHBAU - Darstellungen - Waende - Mauerwerk" 
                                                ]
                    """) :

    # print(e)
    
    # Convert DXF entity into a GeoProxy object:
    geo_proxy = geo.proxy(e)
    # Transform DXF WCS coordinates into CRS coordinates:
    # geo_proxy.wcs_to_crs(m)
    # Transform 2D map projection EPSG:3395 into globe (polar)
    # representation EPSG:4326
    # geo_proxy.map_to_globe()

    # Export GeoJSON data:
    # name = e.dxf.layer + '_' + str(idx) + '.geojson'
    # # with open(TRACK_DATA / name, 'wt', encoding='utf8') as fp:
    # with open( name, 'wt', encoding='utf8') as fp:
    #     json.dump(geo_proxy.__geo_interface__, fp, indent=2)

    each_feature = {
        "type": "Feature",
        "properties": {

        },
        "geometry": geo_proxy.__geo_interface__
    }

    geojson_format["features"].append(each_feature)
    
    idx += 1

with open( 'testfile.geojson', 'wt', encoding='utf8') as fp:
    json.dump(geojson_format, fp, indent=2)



