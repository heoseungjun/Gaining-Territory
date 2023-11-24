import random
from itertools import product, combinations, chain
from shapely.geometry import LineString, Point, Polygon
from options import PLAYERS, BACKGROUND, RADIUS, LINE_WIDTH, LINE_COLOR, CIRCLE_WIDTH, CIRCLE_COLOR, \
                    USER_COLOR, MACHINE_COLOR, PROGRAM_SIZE, CANVAS_SIZE, GRID_COLOR

INFINITY = 999
class MACHINE():
    """
        [ MACHINE ]
        *** 점 개수가 짝 - 후공, 홀 - 선공이 유리함 ***
        MinMax Algorithm을 통해 수를 선택하는 객체.
        - 모든 Machine Turn마다 변수들이 업데이트 됨

        ** To Do **
        MinMax Algorithm을 이용하여 최적의 수를 찾는 알고리즘 생성
           - class 내에 함수를 추가할 수 있음
           - 최종 결과는 find_best_selection을 통해 Line 형태로 도출
               * Line: [(x1, y1), (x2, y2)] -> MACHINE class에서는 x값이 작은 점이 항상 왼쪽에 위치할 필요는 없음 (System이 organize 함)
    """
    def __init__(self, score=[0, 0], drawn_lines=[], whole_lines=[], whole_points=[], location=[]):
        self.id = "MACHINE"
        self.score = [0, 0] # USER, MACHINE
        self.drawn_lines = [] # Drawn Lines
        self.board_size = 7 # 7 x 7 Matrix
        self.num_dots = 0
        self.whole_points = []
        self.location = []
        self.triangles = [] # [(a, b), (c, d), (e, f)]

    # find_best_selection : 라인 출력. 현재는 랜덤으로 출력되고 있음
    def find_best_selection(self):
        # available : 선분 긋기가 가능한 모든 좌표, 이웃만 뽑아내는 방법 강구해야 함
        available = self.get_available()
        # 초-중반부 : 휴리스틱 값이 모두 0일 떄 available_nonconn 적용
        available_nonconn = [line for line in available if not any(point in line for self.drawn_line in self.drawn_lines for point in self.drawn_line)]
        best_score = -INFINITY
        make_triangle = None
        best_selection = None
        
        if len(available_nonconn) == 0 :
            for line in available :
                self.drawn_lines.append(line)
                if(self.check_triangle(line)) :
                    make_triangle = line
                score = self.minmax(2,False)
                self.drawn_lines.remove(line)
                if score > best_score :
                    best_score = score
                    best_selection = line

            if best_selection != None :
                print("best_selection")
                return best_selection
            if make_triangle != None :
                print("make_triangle")
                return make_triangle
            else :
                print("random")
                return random.choice(available)
    
        else :
            return random.choice(available_nonconn)

    def minmax(self, depth, is_max_step) :
        if(depth == 0 or self.check_endgame()) :
            return self.score[1] - self.score[0]

        if is_max_step :
            best_score = -INFINITY
            for line in self.get_available():
                self.drawn_lines.append(line)
                score = self.minmax(depth-1, False)
                self.drawn_lines.remove(line)
                best_score = max(score, best_score)

        else :
            best_score = -INFINITY
            for line in self.get_available():
                self.drawn_lines.append(line)
                score = self.minmax(depth-1, True)
                self.drawn_lines.remove(line)
                best_score = min(score, best_score)
            
        return best_score
    
    # def distance(point1, point2):
    #     return math.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)
    
    # def is_triangle(point1, point2):
    #     side1 = distance(point1, point2)
    #     point1_connected = []
    #     point2_connected = []
    #     for i in self.drawn_lines :
    #         if available[i] != [point1, point2] :
    #             side2 = distance(point2, available[0])
    #             side3 = distance(point3, point1)

    #     if side1 > 0 and side2 > 0 and side3 > 0:
    #         if side1 + side2 > side3 and side2 + side3 > side1 and side3 + side1 > side2:
    #             return True
    #     return False

    def check_triangle(self, available_list):
        score_max = 0
        score_max_index = 0
        score = [0 for k in range(len(available_list))]

        # 휴리스틱으로 maxs_score 값 구하기
        for i in range(len(available_list)):
            line = available_list[i]
            point1 = line[0]
            point2 = line[1]

            point1_connected = []
            point2_connected = []

            for l in self.drawn_lines:
                score[i] = 0
                if l==line: # 자기 자신 제외
                    continue
                if point1 in l:
                    point1_connected.append(l)
                if point2 in l:
                    point2_connected.append(l)

                if point1_connected and point2_connected: # 최소한 2점 모두 다른 선분과 연결되어 있어야 함
                    for line1, line2 in product(point1_connected, point2_connected):
                    
                        # Check if it is a triangle & Skip the triangle has occupied
                        triangle = self.organize_points(list(set(chain(*[line, line1, line2]))))
                        if len(triangle) != 3 or triangle in self.triangles:
                            continue

                        empty = True
                        for point in self.whole_points:
                            if point in triangle:
                                continue
                            if bool(Polygon(triangle).intersection(Point(point))):
                                empty = False

                        if empty:
                            score[i] += 1
                            # 스코어 추가
                            #self.triangles.append(triangle)
                            #self.score[PLAYERS.index(self.turn)]+=1

                        #color = USER_COLOR if self.turn=="USER" else MACHINE_COLOR
                        #self.occupy_triangle(triangle, color=color)
                        #self.get_score = True
            
            if score_max < score[i]:
                score_max = score[i]
                score_max_index = i
            
            #print("- Compute Heuristic 발생, 최대 라인 개수는 " + str(score_max) + "이고, 그 라인은" + str(available_list[score_max_index]) + "입니다.")
            if score_max == 0:
                return random.choice(available_list)
            else:
                return available_list[score_max_index]
    
    # Organization Functions
    def organize_points(self, point_list):
        point_list.sort(key=lambda x: (x[0], x[1]))
        return point_list
    
    def get_available(self):
        available = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])]
        return available

    def check_availability(self, line):
        line_string = LineString(line)

        # Must be one of the whole points
        condition1 = (line[0] in self.whole_points) and (line[1] in self.whole_points)
        
        # Must not skip a dot
        condition2 = True
        for point in self.whole_points:
            if point==line[0] or point==line[1]:
                continue
            else:
                if bool(line_string.intersection(Point(point))):
                    condition2 = False

        # Must not cross another line
        condition3 = True
        for l in self.drawn_lines:
            if len(list(set([line[0], line[1], l[0], l[1]]))) == 3:
                continue
            elif bool(line_string.intersection(LineString(l))):
                condition3 = False

        # Must be a new line
        condition4 = (line not in self.drawn_lines)

        if condition1 and condition2 and condition3 and condition4:
            return True
        else:
            return False
        
    def check_endgame(self):
        remain_to_draw = [[point1, point2] for (point1, point2) in list(combinations(self.whole_points, 2)) if self.check_availability([point1, point2])]
        return False if remain_to_draw else True