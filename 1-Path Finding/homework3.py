import heapq

class node:
    def __init__(self, coord):
        self.coord = tuple(coord)
        self.parent = None
        self.h = 0
        self.g = 0
        self.cost = 0
        
    def move_cost(self, child, whole_map):
        x, y = self.coord[0], self.coord[1]
        x2, y2 = child.coord[0], child.coord[1]
        cost = abs(x - x2) & abs(y - y2)
        total = 10 if cost == 0 else 14
        return total + abs(whole_map[y][x] - whole_map[y2][x2])
        
    def move_cost_ucs(self, child):
        x, y = self.coord[0], self.coord[1]
        x2, y2 = child.coord[0], child.coord[1]
        cost = abs(x - x2) & abs(y - y2)
        return 10 if cost == 0 else 14

    def __lt__(self, other):
        return self.cost < other.cost

    def __eq__(self, other):
        return self.coord == other.coord

def children(point):
    global map_size, max_diff, whole_map
    childs = []
    x, y, w, h = point.coord[0], point.coord[1], map_size[0], map_size[1]
    for move in [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]:
        temp_x, temp_y = x + move[0], y + move[1]
        if 0 <= temp_x < w and 0 <= temp_y < h:
            if abs(whole_map[y][x] - whole_map[temp_y][temp_x]) <= max_diff:
                childs.append((temp_x, temp_y))
     
    return [node(child) for child in childs]


def read_file():
    file = open('input.txt', 'r')
    lines = file.read().splitlines()
    file.close()
    return lines


def bfs(goal, size, land_site, max_diff, whole_map):
    queue, visited = [node(land_site)], set()
    while queue:
        current = queue.pop(0)
        if current.coord == goal:
            path = []
            while current.parent:
                path.append(current.coord)
                current = current.parent
            path.append(current.coord)
            return path[::-1]
        
        if current.coord not in visited:
            x, y, w, h = current.coord[0], current.coord[1], size[0], size[1]
            for move in [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [1, -1], [-1, 1], [-1, -1]:
                if 0 <= x + move[0] < w and 0 <= y + move[1] < h:
                    temp_x, temp_y = x + move[0], y + move[1]
                    if abs(whole_map[y][x] - whole_map[temp_y][temp_x]) <= max_diff:
                        if (temp_x, temp_y) not in visited:
                            child = node((temp_x, temp_y))
                            child.parent = current
                            queue.append(child)
            visited.add(current.coord)
    return []


def ucs(goal, size, land_site, max_diff, whole_map):
    openset = []
    root = node(land_site)
    opendict, closedict = {land_site: root}, {}
    heapq.heappush(openset, root)
    while openset:
            
        current = heapq.heappop(openset)
        del opendict[current.coord]
        
        if current.coord == goal:
            path = []
            while current.parent:
                path.append(current.coord)
                current = current.parent
            path.append(current.coord)
            return path[::-1]

        for child in children(current):
            
            child.cost = current.cost + current.move_cost_ucs(child)
            child.parent = current
            
            if child.coord in closedict:
                old_child = closedict[child.coord]
                if child.cost < old_child.cost:
                    del closedict[old_child.coord]
                    heapq.heappush(openset, child)
                    opendict[child.coord] = child              
            elif child.coord in opendict:
                old_child = opendict[child.coord]
                if child.cost < old_child.cost:
                    openset.remove(old_child)
                    heapq.heappush(openset, child)
                    opendict[child.coord] = child
            else:
                heapq.heappush(openset, child)
                opendict[child.coord] = child
                
        closedict[current.coord] = current
        
    return []


def a_star(goal, size, land_site, max_diff, whole_map):
    openset = []
    root = node(land_site)
    opendict, closedict = {land_site: root}, {}
    heapq.heappush(openset, root)
    while openset:
            
        current = heapq.heappop(openset)
        
        if current.coord == goal:
            path = []
            while current.parent:
                path.append(current.coord)
                current = current.parent
            path.append(current.coord)
            return path[::-1]

        for child in children(current):
            
            child.g = current.g + current.move_cost(child, whole_map)
            child.h = heuristic(child.coord, goal, whole_map)
            child.cost = child.g + child.h
            child.parent = current
            
            if child.coord in closedict:
                old_child = closedict[child.coord]
                new_g = child.g
                if new_g < old_child.g:
                    del closedict[old_child.coord]
                    heapq.heappush(openset, child)
                    opendict[child.coord] = child           
            elif child.coord in opendict:
                old_child = opendict[child.coord]
                new_g = child.g
                if new_g < old_child.g:
                    openset.remove(old_child)
                    heapq.heappush(openset, child)
                    opendict[child.coord] = child
            else:
                heapq.heappush(openset, child)
                opendict[child.coord] = child
                
        closedict[current.coord] = current
        
    return []


def heuristic(c, g, whole_map):
    x, y = c[0], c[1]
    x2, y2 = g[0], g[1]
    return max(abs(x - x2), abs(y - y2)) + abs(whole_map[y][x] - whole_map[y2][x2])


line = read_file()

algorithm = line[0]
map_size = tuple(map(int, line[1].split(' ')))
land_site = tuple(map(int, line[2].split(' ')))
max_diff = int(line[3])
num_target = int(line[4])
targets, whole_map = [], []

for i in range(len(line)):
    if i > (4 + int(num_target)):
        whole_map.append(list(map(int, line[i].split(' '))))
    elif i > 4:
        targets.append(tuple(map(int, line[i].split(' '))))

output = open('output.txt', 'w')
if algorithm == 'BFS':
    for target in targets:
        result = bfs(target, map_size, land_site, max_diff, whole_map)
        if result:
            for coord in result:
                endl = '\n' if coord == result[-1] else ' '
                if target == targets[-1]:
                    endl = '' if coord == result[-1] else ' '
                print(coord[0], coord[1], sep=',', end=endl, file=output)
        else:
            endl = '' if target == targets[-1] else '\n'
            print("FAIL", file=output, end=endl)
elif algorithm == 'UCS':
    for target in targets:
        result = ucs(target, map_size, land_site, max_diff, whole_map)
        if result:
            for coord in result:
                endl = '\n' if coord == result[-1] else ' '
                if target == targets[-1]:
                    endl = '' if coord == result[-1] else ' '
                print(coord[0], coord[1], sep=',', end=endl, file=output)
        else:
            endl = '' if target == targets[-1] else '\n'
            print("FAIL", file=output, end=endl)
elif algorithm == 'A*':
    for target in targets:
        result = a_star(target, map_size, land_site, max_diff, whole_map)
        if result:
            for coord in result:
                endl = '\n' if coord == result[-1] else ' '
                if target == targets[-1]:
                    endl = '' if coord == result[-1] else ' '
                print(coord[0], coord[1], sep=',', end=endl, file=output)
        else:
            endl = '' if target == targets[-1] else '\n'
            print("FAIL", file=output, end=endl)
output.close()
