# L5IN_task1: dxf to geojson
 The main aim is converting AutoCAD file(dxf) to geojson file and classify features. The aim is to generate a workflow that needs minimum manipulation of the DXF files. Nevertheless, some pre-adjustments are indispensable because of the complexity of CAD files and the lack of python libraries that can handle DXF files.


![image](https://github.com/chungkang/L5IN_task1/assets/36185863/1efa5a0c-4193-4ebe-8d50-c0e32cd01bb9)

The 2D floor plan generation from CAD plan. Above is the original CAD plan. Below is the zoomed view, from left to right; pre-processed plan, extracted features, and the final product - 2D floor plan

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
This step is for settting requried parameters for main logic.

directory_path: directory path
dxf_name: dxf file name
min_point: minimum length as a point for geometry
wall_width: assumption of wall width
layer_list: interested layers
door_layer: door layer

## Step b. dxf to geojson
This step is for converting dxf to geojson.

- Read dxf file with ezdxf library
- Extract interested layers based on "layer_list"
- Categorized wall and door based on "door_layer_name"
  doors are named with block_id in attribute with each block
- Save geojson

## Step c. door component
This step is for extracting door component.

- Read geojson file from Step b
- Extract door layer based on "door_layer"
- Convert features with Shaepely library for geometric purpose
- Save door component as door_polygon, door_polygon_buffer, door_points, door_lines as geojson
door_polygon: outer most contour
door_polygon_buffer: buffererd door_polygon based with length of "min_point"
door_points: each edge from door_polygon
door_lines: each line from door_polygon

## Step d. Room Index
This step is for extracting "Room Index" to get inner part of wall (room, hallway...).

- Read door_lines geojson created by Step c
- Convert features with Shaepely library for geometric purpose
- Extract lines from door_lines which is longer than "wall_width"
- Get middle point of the longer door line ("Door Point") and draw orthogonal line
- Get the direction of the orthogonal line which have longer length to another intersection point with wall line
- Put "Room Index" inside of the space (not in the wall)
- Save room index as geojson

![image](https://github.com/chungkang/L5IN_task1/assets/36185863/d997d6c8-b9cb-4121-aa7b-108911d1c711)
Door Point and Room Index

## Step e. Room Polygon
This step is for converting closed lines to polygon.

- Read geojson created by Step b
- Convert features with Shaepely library for geometric purpose
- Create polygons with closed lines
- Extract polygons which include Room Index which is extracted by Step d
- Save all closed polygons and extracted polygons as geojson

## Processing with QGIS
This step is for drawing outer most wall of the building with QGIS.

- Read geojson created by Step b with QGIS
- Draw outer most wall with snap function of QGIS

## Step f. Wall Polygon
This step is for extracting wall polygon from outer most wall polygon, door polygon, and room polygon.

- Read geojson from Step c, Step e, and Processing with QGIS. (door_polygon_buffer.geojson, final_room_polygon.geojson, outer_wall_manual.geojson)
- Convert features with Shaepely library for geometric purpose
- Subtract door and room polygon from outer wall polygon
- Save wall as geojson

## Output
Those 3 geojson files are representing door, room, and wall part.
door_polygon_buffer.geojson
final_room_polygon.geojson
wall_polygon.geojson

## Library
ezdxf https://github.com/mozman/ezdxf/tree/stable
Geopandas, Shapely, json, geojson, openCV
