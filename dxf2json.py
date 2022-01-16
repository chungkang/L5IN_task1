import ezdxf
import ezdxf.addons.geo as geo
import json
from jsonmerge import merge
# import geopandas

# source file
# dxf = "./removed_HCU_D_104_Grundriss_2OG_moved.dxf"

dxf = "./copied_HCU_D_104_Grundriss_2OG_moved.dxf"

# loading dxf file
doc = ezdxf.readfile(dxf)

# get modelspace / 모형
msp = doc.modelspace()

# get layout / plan 레이아웃 페이지: 주석 등
plan = doc.layout('16 - plan 2.OG_1_100')

# get blocks
blk = doc.blocks
# my_block = doc.blocks.new('MyBlock')

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
    "features": []
}

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

# extract each entity
# 전체 *, 블로참조 ATTRIB, 치수 DIMENSION, ARC_DIMENSION, HATCH,INSERT, LEADER, MESH, MTEXT, POINT, 정점 VERTEX, 보조선 RAY, SHAPE, SOLID, SURFACE, TEXT, TRACE, VIEWPORT, XLINE

# ARC CIRCLE ELLIPSE 
for e in msp.query('LWPOLYLINE MLINE POLYLINE SPLINE') :
# for e in msp.query('LWPOLYLINE') :
    # Convert DXF entity into a GeoProxy object:
    geo_proxy = geo.proxy(e)
    # Transform DXF WCS coordinates into CRS coordinates:
    geo_proxy.wcs_to_crs(m)
    # Transform 2D map projection EPSG:3395 into globe (polar)
    # representation EPSG:4326
    geo_proxy.map_to_globe()
    # Export GeoJSON data:
    # name = e.dxf.layer + '_' + str(idx) + '.geojson'

    # # with open(TRACK_DATA / name, 'wt', encoding='utf8') as fp:
    # with open( name, 'wt', encoding='utf8') as fp:
    #     json.dump(geo_proxy.__geo_interface__, fp, indent=2)
    
    each_feature = {
        "type": "Feature",
        "properties": {},
        "geometry": geo_proxy.__geo_interface__
    }

    geojson_format["features"].append(each_feature)
    
    idx += 1

with open( 'testfile.geojson', 'wt', encoding='utf8') as fp:
    json.dump(geojson_format, fp, indent=2)



