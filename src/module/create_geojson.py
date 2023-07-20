import json
import a_setting as setting

# custom coordinate system geojson
geojson_custom = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
		"properties": { "name": setting.dxf_CRS }
	},
    "features": []
}

# target CRS geojson
geojson_target = {
    "type": "FeatureCollection",
	"crs": {
	    "type": "name",
        "properties": { "name": "urn:ogc:def:crs: " + setting.target_CRS }
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
        json.dump(input_geojson, fp, ensure_ascii=False)