from shapely import geometry
import shapely

min_point = 0.01 # minimum length as a point

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
                result_list.extend(list(inter.geoms))
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
                        result_list.extend(list(geom.geoms))
                    elif "MultiLineString" == geom.type:
                        multiLine = [line for line in geom]
                        first_coords = multiLine[0].coords[0]
                        last_coords = multiLine[len(multiLine)-1].coords[1]
                        result_list.append(geometry.Point(first_coords[0], first_coords[1]))
                        result_list.append(geometry.Point(last_coords[0], last_coords[1]))
    return result_list


# get lines from point and a line
def get_lines_from_point_and_line(line, point, filtered_lines):
    result_yn = False
    
    # find all intersection points between line and filtered_lines
    line_inters = find_intersections_baseline_to_all(line, filtered_lines)

    # find the closest point from line_inters and point -> another side's end point
    line_end1 = geometry.Point()
    distance_line_end1 = 100
    for pt in line_inters:
        if pt.distance(point) < distance_line_end1:
            line_end1 = pt
            distance_line_end1 = pt.distance(point)

    # update based on one end point of the line
    splited_line = shapely.ops.split(line, line_end1.buffer(min_point))
    
    for line in splited_line:
        if point.distance(line) < min_point:
            line = line

    # find all the intersections between updated line and filtered lines
    updated_line_inters = find_intersections_baseline_to_all(line, filtered_lines)

    # find most close apposite end point which is not equl to line_end1 inupdated_line_inters
    line_end2 = geometry.Point()
    distance_line_end2 = 100
    for pt in updated_line_inters:
        if pt.distance(line_end1) < min_point:
            continue
        if pt.distance(line_end1) < distance_line_end2:
            line_end2 = pt
            distance_line_end2 = pt.distance(line_end1)

    result_lines = []

    # if there is no endpoint, skip
    if line_end2:
        result_yn = True

        # update line with line_end1 and line_end2
        line = geometry.LineString([line_end1, line_end2])

        # get all lines which is near line_end1 and line_end2
        for line in  filtered_lines:
            line = geometry.shape(line['geometry'])
            if line_end1.distance(line) < min_point or line_end2.distance(line) < min_point:
                result_lines.append(line)
    else:
        result_yn = False

    return [result_yn, result_lines]

