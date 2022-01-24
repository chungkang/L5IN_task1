import matplotlib.pyplot as plt
import numpy as np
from copy import deepcopy
import json

with open('testfile_EPSG32632.geojson') as f:
    contact_gj = json.load(f)
    del f
    
contacts = contact_gj['features']

vertices = []

for feat in contacts:
    start = feat["geometry"]["coordinates"][0]
    stop = feat['geometry']['coordinates'][-1]
    
    if start not in vertices:
        vertices.append(start)
    
    if stop not in vertices:
        vertices.append(stop)

for n, v in enumerate(vertices):
    
    for i, feat in enumerate(contacts):
        if v == feat['geometry']['coordinates'][0]:
            feat['properties']['start'] = n
            
        elif v == feat['geometry']['coordinates'][-1]:
            feat['properties']['stop'] = n

contact_adj_dict = {}

for i, c in enumerate(contacts):
    contact_adj_dict[i] = {'start': [],
                           'stop': []}
    
    for j, cc in enumerate(contacts):
        if j != i:
            if c['properties']['start'] in (
                cc['properties']['start'], cc['properties']['stop']):
                contact_adj_dict[i]['start'].append(j)
            elif c['properties']['stop'] in (
                cc['properties']['start'], cc['properties']['stop']):
                contact_adj_dict[i]['stop'].append(j)

# print the first element for demonstration

contact_adj_dict[0]