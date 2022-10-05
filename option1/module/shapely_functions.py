from shapely import geometry

# door와 접하는 point만 추출
# baseline: single line, all_lines: all walls or filtered walls, result_list: input/output list
def find_intersections_baseline_to_all_door_junction(baseline, all_lines):
    result_list = []
    for line in  all_lines:
        if line["properties"]["door_juction"] == "Y":
            line = geometry.shape(line['geometry'])
            if baseline.intersects(line):
                inter = baseline.intersection(line)
                if "Point" == inter.type:
                    result_list.append(inter)
                elif "MultiPoint" == inter.type:
                    result_list.extend([pt for pt in inter])
                elif "MultiLineString" == inter.type:
                    multiLine = [line for line in inter]
                    first_coords = multiLine[0].coords[0]
                    last_coords = multiLine[len(multiLine)-1].coords[1]
                    result_list.append(geometry.Point(first_coords[0], first_coords[1]))
                    result_list.append(geometry.Point(last_coords[0], last_coords[1]))
                elif "GeometryCollection" == inter.type:
                    for geom in inter:
                        if "Point" == geom.type:
                            result_list.append(geom)
                        elif "MultiPoint" == geom.type:
                            result_list.extend([pt for pt in geom])
                        elif "MultiLineString" == geom.type:
                            multiLine = [line for line in geom]
                            first_coords = multiLine[0].coords[0]
                            last_coords = multiLine[len(multiLine)-1].coords[1]
                            result_list.append(geometry.Point(first_coords[0], first_coords[1]))
                            result_list.append(geometry.Point(last_coords[0], last_coords[1]))
    return result_list

# baseline: single line, all_lines: all walls or filtered walls, result_list: input/output list
def find_intersections_baseline_to_all(baseline, all_lines):
    result_list = []
    for line in  all_lines:
        line = geometry.shape(line['geometry'])
        if baseline.intersects(line):
            inter = baseline.intersection(line)
            if "Point" == inter.type:
                result_list.append(inter)
            elif "MultiPoint" == inter.type:
                result_list.extend([pt for pt in inter])
            elif "MultiLineString" == inter.type:
                multiLine = [line for line in inter]
                first_coords = multiLine[0].coords[0]
                last_coords = multiLine[len(multiLine)-1].coords[1]
                result_list.append(geometry.Point(first_coords[0], first_coords[1]))
                result_list.append(geometry.Point(last_coords[0], last_coords[1]))
            elif "GeometryCollection" == inter.type:
                for geom in inter:
                    if "Point" == geom.type:
                        result_list.append(geom)
                    elif "MultiPoint" == geom.type:
                        result_list.extend([pt for pt in geom])
                    elif "MultiLineString" == geom.type:
                        multiLine = [line for line in geom]
                        first_coords = multiLine[0].coords[0]
                        last_coords = multiLine[len(multiLine)-1].coords[1]
                        result_list.append(geometry.Point(first_coords[0], first_coords[1]))
                        result_list.append(geometry.Point(last_coords[0], last_coords[1]))
    return result_list