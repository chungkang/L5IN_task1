import geopandas
from shapely.ops import polygonize

# gdf = geopandas.GeoDataFrame.from_features(f)
gdf = geopandas.read_file('testfile_EPSG32632.geojson')
linestrings = gdf[gdf.geometry.type == "LineString"]

polygons = geopandas.GeoSeries(polygonize(linestrings.geometry))

# polygons.plot()

polygons = polygons.set_crs("EPSG:32632")
polygons.to_file("poligonized_test.geojson", driver='GeoJSON')
