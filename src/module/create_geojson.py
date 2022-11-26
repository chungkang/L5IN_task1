import json
import a_config as config # load configuration parameters for the logics

# custom coordinate system geojson
geojson_custom = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
		"properties": { "name": config.dxf_CRS }
	},
    "features": []
}

# target CRS geojson
geojson_target = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
        "properties": { "name": "urn:ogc:def:crs:" + config.target_CRS }
	},
    "features": []
}

# write custom defined CRS geojson
def write_geojson(path, input_geojson):
    with open( path, 'wt', encoding='utf8') as fp:
        json.dump(input_geojson, fp, ensure_ascii=False)