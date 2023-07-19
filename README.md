# L5IN_task1: dxf to geojson
 The main aim is converting AutoCAD file(dxf) to geojson file and classify features. The aim is to generate a workflow that needs minimum manipulation of the DXF files. Nevertheless, some pre-adjustments are indispensable because of the complexity of CAD files and the lack of python libraries that can handle DXF files.

# The 2D floor plan generation from CAD plan. Above is the original CAD plan. Below is the zoomed view, from left to right; pre-processed plan, extracted features, and the final product - 2D floor plan
![image](https://github.com/chungkang/L5IN_task1/assets/36185863/1efa5a0c-4193-4ebe-8d50-c0e32cd01bb9)

# Workflow
![image](https://github.com/chungkang/L5IN_task1/blob/main/flow_chart.drawio.png)

## Pre processing: modify autoCAD floorplan(dxf)
- Delete uninterested layers with LAYDEL command with AutoCAD
- Delete arcs from the door blocks
- Explode blocks nested in another block feature
- Create door block which is not constructed as a door block
- Delete small objects
  => Assume that all doors are blocks

![image](https://github.com/chungkang/L5IN_task1/assets/36185863/3818d631-f58c-4fcc-a03f-2702cd1899e7)
Original dxf file

![image](https://github.com/chungkang/L5IN_task1/assets/36185863/0e188574-caa7-4a14-8c2e-a9ac26eb0364)
Interested Layers

![image](https://github.com/chungkang/L5IN_task1/assets/36185863/09e4880b-281b-4378-85d7-ebd7ea8ccd86)
Cleaned dxf file

## Step a. setting
directory_path: directory path
dxf_name: dxf file name
min_point: minimum length as a point for geometry
wall_width: assumption of wall width
layer_list: interested layers
door_layer: door layer

## Step b. dxf to geojson
- Read dxf file with ezdxf library
- Extract interested layers based on "layer_list"
- Categorized wall and door based on "door_layer_name"
- Write a geojson file

## Step c. door component


Extract all wall lines and room index
read dxf file as Shapely instant
save all lines as geojson format with CRS
convert CRS to EPSG:32632
extract door polygon, door line, door point from door block
extract inner and outer part of door line
loop with door line - each door line represents room index
assgin room index point to indicate closed room

##### Step c: Create closed polygon for room
input  original_epsg32632.geojson / room_index.geojson
create room polygon with closed lines
filter room polygon with room index point

##### Pre-processing with QGIS
input   original_epsg32632.geojson
draw outer wall line as a single polygon

##### Step d: Extract wall polygon
input  outer_wall_manual.geojson / filtered_room_polygon.geojson / door_polygon.geojson / stair_polygon.geojson
Subtract door, stair from outer wall polygon

## Library
ezdxf https://github.com/mozman/ezdxf/tree/stable
Geopandas, Shapely, json, geojson, openCV
