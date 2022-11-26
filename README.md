# L5IN_task1: dxf to geojson
 The main aim of Task1 is converting autoCAD file(dxf) to geojson file. In converting method automate cleaning method should be concerned. That means only the interested lines, such as wall and door should be extracted. To solve this problem 'ezdxf' library for Python is chosen. 'exdxf' is a Python package to create and modify dxf drawings. With this library all the elements from dxf file can be converted to python instance. According to other researches, the other researches were processed with pre-cleaned and pre-organized autoCAD file with autoCAD software manually.

## Input autoCAD 2D floorplan
![image](https://user-images.githubusercontent.com/36185863/146599197-d2d3bb14-1dc3-4afa-a9ba-904a4fff6cf7.png)

## Output geojson 2D floorplan
![image](https://user-images.githubusercontent.com/36185863/146599240-a79d8ea8-4d7b-4b04-a0b9-8810acc17ca4.png)

## Workflow
![image](https://github.com/chungkang/L5IN_task1/blob/main/flow_chart.drawio.png)

### Detailed Workflow
#### Pre processing: modify autoCAD floorplan(dxf)
explode block in block for door block, manual editing of door part, save as dxf format

#### Main logic
##### Step a: Settings
get dxf file name, CRS, mininum point buffer, wall width, extract interested layer name, door layer name, stair layer name, input directory path, output directory path

![image](https://user-images.githubusercontent.com/36185863/204096269-664ea0c4-6ae7-463b-8686-c47a45282914.png)
![image](https://user-images.githubusercontent.com/36185863/204096274-895c4b48-b96c-467b-a418-e21b7514aa58.png)
remove opening part of door block


##### Step b.: Extract all wall lines and room index
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

## Libraries
Ezdxf, Geopandas, Shapely, json, geojson, openCV
