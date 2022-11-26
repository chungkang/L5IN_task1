# L5IN_task1: dxf to geojson
 The main aim of Task1 is converting autoCAD file(dxf) to geojson file. In converting method automate cleaning method should be concerned. That means only the interested lines, such as wall and door should be extracted. To solve this problem 'ezdxf' library for Python is chosen. 'exdxf' is a Python package to create and modify dxf drawings. With this library all the elements from dxf file can be converted to python instance. According to other researches, the other researches were processed with pre-cleaned and pre-organized autoCAD file with autoCAD software manually.

## Input autoCAD 2D floorplan
![image](https://user-images.githubusercontent.com/36185863/146599197-d2d3bb14-1dc3-4afa-a9ba-904a4fff6cf7.png)

## Output geojson 2D floorplan
![image](https://user-images.githubusercontent.com/36185863/146599240-a79d8ea8-4d7b-4b04-a0b9-8810acc17ca4.png)

## Workflow
![image](https://github.com/chungkang/L5IN_task1/blob/main/flow_chart.drawio.png)

## Libraries
Ezdxf, Geopandas, Shapely, json, geojson, openCV
