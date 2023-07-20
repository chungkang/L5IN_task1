# L5IN_task1: DXF to GeoJSON

The main aim of this project is to convert AutoCAD files (DXF) to GeoJSON format and classify features. The goal is to create a workflow that requires minimal manipulation of the DXF files. However, some pre-adjustments are indispensable due to the complexity of CAD files and the limited availability of Python libraries that can handle DXF files.

![Original CAD plan](https://github.com/chungkang/L5IN_task1/assets/36185863/1efa5a0c-4193-4ebe-8d50-c0e32cd01bb9)

## Workflow
![Flowchart](https://github.com/chungkang/L5IN_task1/blob/main/flow_chart.drawio.png)

## Preprocessing: Modifying AutoCAD Floorplan (DXF)
- Use the LAYDEL command in AutoCAD to delete unneeded layers.
- Remove arcs from the door blocks.
- Explode blocks nested within another block feature.
- Create door blocks that are not constructed as door blocks.
- Delete small objects.
  => It is assumed that all doors are represented as blocks.

|![Original DXF file](https://github.com/chungkang/L5IN_task1/assets/36185863/3818d631-f58c-4fcc-a03f-2702cd1899e7)|![Interested Layers](https://github.com/chungkang/L5IN_task1/assets/36185863/0e188574-caa7-4a14-8c2e-a9ac26eb0364)|![Cleaned DXF file](https://github.com/chungkang/L5IN_task1/assets/36185863/09e4880b-281b-4378-85d7-ebd7ea8ccd86)|
|-|-|-|
|Original DXF file|Interested Layers|Cleaned DXF file|

## Step a: Setting
This step is for setting required parameters for the main logic.

- directory_path: directory path
- dxf_name: DXF file name
- min_point: minimum length as a point for geometry
- wall_width: assumption of wall width
- layer_list: interested layers
- door_layer: door layer

## Step b: DXF to GeoJSON
This step is for converting DXF to GeoJSON.

- Read the DXF file using the ezdxf library.
- Extract the layers of interest based on the "layer_list."
- Categorize walls and doors based on the "door_layer_name."
  Doors are identified by the block_id attribute within each block.
- Save the GeoJSON file.

## Step c: Door Component
This step is for extracting door components.

- Read the GeoJSON file from Step b.
- Extract the door layer based on "door_layer."
- Convert features using the Shapely library for geometric purposes.
- Save the door components as door_polygon, door_polygon_buffer, door_points, and door_lines in GeoJSON format.

- door_polygon: outermost contour
- door_polygon_buffer: buffered door_polygon with a length of "min_point"
- door_points: each edge from door_polygon
- door_lines: each line from door_polygon

## Step d: Room Index
This step is for extracting the "Room Index" to obtain the inner parts of walls (rooms, hallways, etc.).

- Read the door_lines GeoJSON created by Step c.
- Convert features using the Shapely library for geometric purposes.
- Extract lines from door_lines that are longer than the "wall_width."
- Obtain the middle point of the longer door line ("Door Point") and draw an orthogonal line.
- Determine the direction of the orthogonal line with the longer length towards another intersection point with the wall line.
- Place the "Room Index" inside the space (not in the wall).
- Save the room index as GeoJSON.

![Door Point and Room Index](https://github.com/chungkang/L5IN_task1/assets/36185863/d997d6c8-b9cb-4121-aa7b-108911d1c711)

## Step e: Room Polygon
This step is for converting closed lines to polygons.

- Read the GeoJSON created by Step b.
- Convert features using the Shapely library for geometric purposes.
- Create polygons from the closed lines.
- Extract polygons that include the Room Index, which was obtained in Step d.
- Save all closed polygons and the extracted polygons as GeoJSON.

## Processing with QGIS
This step is for drawing the outermost wall of the building with QGIS.

- Read the GeoJSON created by Step b using QGIS.
- Use the snap function in QGIS to draw the outermost wall.

## Step f: Wall Polygon
This step is for extracting the wall polygon from the outermost wall polygon, door polygon, and room polygon.

- Read the GeoJSON files from Step c (door_polygon_buffer.geojson), Step e (final_room_polygon.geojson), and the processed file from QGIS (outer_wall_manual.geojson).
- Utilize the Shapely library for geometric operations.
- Perform subtraction to remove the areas covered by door and room polygons from the outer wall polygon.
- Save the resulting wall polygon as a new GeoJSON file.

## Output
The output includes three GeoJSON files representing the door, room, and wall parts:

1. `door_polygon_buffer.geojson`: This file contains the GeoJSON representation of the door polygons after buffering.
2. `final_room_polygon.geojson`: This file contains the GeoJSON representation of the room polygons extracted from the building's emergency escape plan image.
3. `wall_polygon.geojson`: This file contains the GeoJSON representation of the wall polygons obtained by subtracting the door and room polygons from the outermost wall polygon.

These three GeoJSON files provide valuable information about the building's layout, including the locations of doors, rooms, and the overall structure of the walls. They can be utilized for various purposes, such as indoor navigation, spatial analysis, and building management.

## Library
- ezdxf: [https://github.com/mozman/ezdxf/tree/stable](https://github.com/mozman/ezdxf/tree/stable)
- Geopandas, Shapely, json, geojson, openCV
