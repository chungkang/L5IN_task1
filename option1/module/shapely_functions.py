from shapely import geometry
import shapely

min_point = 0.01 # minimum length as a point

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


# get lines from point and a line
def get_lines_from_point_and_line(line, point, filtered_lines):
    result_yn = False
    
    # line과 filtered_lines의 모든 교점을 구함
    line_inters = find_intersections_baseline_to_all(line, filtered_lines)

    # line_inters 중에서 point와 가장 가까운 점을 구함 -> 한쪽 끝의 end point
    line_end1 = geometry.Point()
    distance_line_end1 = 100
    for pt in line_inters:
        if pt.distance(point) < distance_line_end1:
            line_end1 = pt
            distance_line_end1 = pt.distance(point)

    # line의 한쪽 end point를 기준으로 업데이트
    splited_line = shapely.ops.split(line, line_end1.buffer(min_point))
    
    for line in splited_line:
        if point.distance(line) < min_point:
            line = line

    # 업데이트된 line과 filtred_lines의 모든 교점을 구함
    updated_line_inters = find_intersections_baseline_to_all(line, filtered_lines)

    # updated_line_inters 중에서 line_end1 과 겹치는 것을 제외하고, 가장 가까운 반대편 end point를 구함
    line_end2 = geometry.Point()
    distance_line_end2 = 100
    for pt in updated_line_inters:
        if pt.distance(line_end1) < min_point:
            continue
        if pt.distance(line_end1) < distance_line_end2:
            line_end2 = pt
            distance_line_end2 = pt.distance(line_end1)

    result_lines = []

    # endpoint 를 못찾으면 스킵
    if line_end2:
        result_yn = True

        # line_end1과 line_end2로 이루어진 선분으로 line을 업데이트
        line = geometry.LineString([line_end1, line_end2])

        # line_end1과 line_end2에 접하는 모든 선분을 추출
        for line in  filtered_lines:
            line = geometry.shape(line['geometry'])
            if line_end1.distance(line) < min_point or line_end2.distance(line) < min_point:
                result_lines.append(line)
    else:
        result_yn = False

    return [result_yn, result_lines]

