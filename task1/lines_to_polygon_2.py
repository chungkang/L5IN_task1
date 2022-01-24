import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import json
import geopandas
from shapely.ops import polygonize

with open('testfile_EPSG32632.geojson') as f:
    contact_gj = json.load(f)
    del f
    
# contacts = contact_gj['features']

gdf = geopandas.GeoDataFrame.from_features(f)

polygons = geopandas.GeoSeries(polygonize(gdf.geometry))

polygons.plot()


