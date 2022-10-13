import geopandas as gpd
import geojson
import json
from shapely.geometry import LineString
import shapely
from shapely.geometry import *
from shapely.ops import unary_union
from shapely import geometry
import module.create_geojson as create_geojson
import copy

with open('geojson_result\\11102022\\result.geojson') as f:
    geojson_result = json.load(f)

with open('geojson_result\\11102022\\room_index.geojson') as f:
    room_index = json.load(f)

# initialize empty geojson
polygon_geojson = copy.deepcopy(create_geojson.geojson_EPSG32632)

# room index로 for 문 돌리기
for point in  room_index['features']:
    lines_all = []
    # room index에 해당하는 geojson_result의 polygon을 찾기
    # line들의 edge points에서 접하는 모든 선분을 추출
    for line in  geojson_result['features']:
        if line['properties'].get('id',"none") == point['properties']['id']:
            line = geometry.shape(line['geometry'])
            lines_all.append(line.buffer(0.03))

    # 구해진 모든 wall lines를 통해서 내부 polygon을 구함
    Multipolygon = shapely.ops.unary_union(lines_all)
    Polygons = list(Multipolygon.geoms)

    # 만들어진 polygon 내부에 room index의 point가 포함되어 있는 것만 저장
    for polygon in Polygons:
        all_internal_geoms = [geom for geom in polygon.interiors]
        for geom in all_internal_geoms:
            if geom.contains(point):
                geom_feature = {
                    "type": "Feature",
                    "properties": {
                        "id": point['properties']['id']
                    },
                    "geometry":geometry.mapping(geometry.Polygon(geom))
                }
                polygon_geojson["features"].append(geom_feature)

create_geojson.write_geojson('geojson_result\\11102022\\polygon.geojson', polygon_geojson)