import json
import a_config as config # load configuration parameters for the logics

# custom coordinate system geojson
geojson_custom = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
		"properties": {
			"name": config.dxf_CRS
		}
	},
    "features": []
}

# EPSG 32632 geojson
geojson_EPSG32632 = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
        "properties": { "name": "urn:ogc:def:crs:EPSG::32632" }
	},
    "features": []
}

def create_geojson_feature(index, layer, category, block_id, geometry):
	each_feature = {
						"type": "Feature",
						"properties": {
							"index": index,
							"layer": layer,
							"category": category,
							"block_id": block_id
						},
						"geometry": geometry
					}
	return each_feature

# write custom defined CRS geojson
def write_geojson(path, input_geojson):
    with open( path, 'wt', encoding='utf8') as fp:
        json.dump(input_geojson, fp, indent=2)