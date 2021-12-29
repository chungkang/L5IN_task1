import ezdxf
import ezdxf.addons.geo as geo
import json
from jsonmerge import merge
# import geopandas

# source file
dxf = "./removed_HCU_D_104_Grundriss_2OG_moved.dxf"

# loading dxf file
doc = ezdxf.readfile(dxf)

# get modelspace
msp = doc.modelspace()

# Get the geo location information from the DXF file:
geo_data = msp.get_geodata()
if geo_data:
    # Get transformation matrix and epsg code:
    m, epsg = geo_data.get_crs_transformation()
else:
    # Identity matrix for DXF files without geo reference data:
    m = ezdxf.math.Matrix44()

# get lines of layer
# lines = msp.query('LINE[layer=="01"]')
# msp.query('LWPOLYLINE')

# counting entities of dxf file  
idx = 0

# initialize empty geojson
geojson_format = {
    "type": "FeatureCollection",
    "features": []
}

# initialize empty list for "features"
features_list = []

# extract each entity
for e in msp.query('LWPOLYLINE') :
    # Convert DXF entity into a GeoProxy object:
    geo_proxy = geo.proxy(e)
    # Transform DXF WCS coordinates into CRS coordinates:
    geo_proxy.wcs_to_crs(m)
    # Transform 2D map projection EPSG:3395 into globe (polar)
    # representation EPSG:4326
    geo_proxy.map_to_globe()
    # Export GeoJSON data:
    name = e.dxf.layer + '_' + str(idx) + '.geojson'

    # with open(TRACK_DATA / name, 'wt', encoding='utf8') as fp:
    # with open( name, 'wt', encoding='utf8') as fp:
    #     json.dump(geo_proxy.__geo_interface__, fp, indent=2)

    # print(geo_proxy.__geo_interface__)
    
    each_feature = {
        "type": "Feature",
        "geometry": geo_proxy.__geo_interface__,
        "properties": {}
    }

    features_list.append(each_feature)
    
    idx = idx + 1

    # if idx ==0:
    #     break

geojson_format["features"] = features_list

print(geojson_format)

with open( 'testfile.geojson', 'wt', encoding='utf8') as fp:
    json.dump(geojson_format, fp, indent=2)
## features 데이터를 geojson 포맷으로 입력 geometry
## {'type': 'Polygon', 'coordinates': [[(32.039104, 47.149722), (32.039094, 47.149752), (32.039104, 47.149722)]]}

## 통합 geojson을 파일로 출력


