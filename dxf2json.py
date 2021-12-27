import ezdxf
import ezdxf.addons.geo as geo
import json

dxf = "./removed_HCU_D_104_Grundriss_2OG_moved.dxf"

# loading dxf file
doc = ezdxf.readfile(dxf)

# get modelspace
msp = doc.modelspace()

# get lines of layer
# lines = msp.query('LINE[layer=="01"]')

# Get the geo location information from the DXF file:
geo_data = msp.get_geodata()
if geo_data:
    # Get transformation matrix and epsg code:
    m, epsg = geo_data.get_crs_transformation()
else:
    # Identity matrix for DXF files without geo reference data:
    m = ezdxf.math.Matrix44()

# for track in msp.query('LWPOLYLINE'):

def export_geojson(entity, m, index):
    # Convert DXF entity into a GeoProxy object:
    geo_proxy = geo.proxy(entity)
    # Transform DXF WCS coordinates into CRS coordinates:
    geo_proxy.wcs_to_crs(m)
    # Transform 2D map projection EPSG:3395 into globe (polar)
    # representation EPSG:4326
    geo_proxy.map_to_globe()
    # Export GeoJSON data:
    name = entity.dxf.layer + '_' + str(index) + '.geojson'
    # with open(TRACK_DATA / name, 'wt', encoding='utf8') as fp:
    with open(name, 'wt', encoding='utf8') as fp:
        json.dump(geo_proxy.__geo_interface__, fp, indent=2)

idx = 0

for e in msp.query('LWPOLYLINE'):
    export_geojson(e, m, idx)
    idx = idx + 1
