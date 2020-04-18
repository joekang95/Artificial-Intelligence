import copy
import time
import math


class Node:
    def __init__(self, parent, child):
        self.parent = parent
        self.child = child


class GameState:
    def __init__(self, board, player, move, start_time, mode, time):
        self.white_goals = {(0, 0), (1, 0), (2, 0), (3, 0), (4, 0),
                            (0, 1), (1, 1), (2, 1), (3, 1), (4, 1),
                            (0, 2), (1, 2), (2, 2), (3, 2),
                            (0, 3), (1, 3), (2, 3),
                            (0, 4), (1, 4)}
        self.black_goals = {(14, 11), (15, 11),
                            (13, 12), (14, 12), (15, 12),
                            (12, 13), (13, 13), (14, 13), (15, 13),
                            (11, 14), (12, 14), (13, 14), (14, 14), (15, 14),
                            (11, 15), (12, 15), (13, 15), (14, 15), (15, 15)}
        self.white, self.black = [], []
        self.goals, self.origins, self.corner = None, None, None
        self.board = board
        self.player = player
        self.move = move
        self.start_time = start_time
        self.set_pieces()
        self.set_goals()
        self.mode = mode
        self.time = time

    def set_pieces(self):
        for i in range(16):
            for j in range(16):
                if self.board[i][j] == 'W':
                    self.white.append((j, i))
                elif self.board[i][j] == 'B':
                    self.black.append((j, i))

    def set_goals(self):
        self.goals = self.white_goals if self.player == 'WHITE' else self.black_goals
        self.origins = self.black_goals if self.player == 'WHITE' else self.white_goals
        self.corner = 15 if self.player == 'WHITE' else 0

    def utility(self):
        def distance(a, b):
            # print(a, b)
            return math.sqrt((b[0] - a[0]) ** 2 + (b[1] - a[1]) ** 2)

        # (y, x) (x, y) makes difference
        w_score, b_score = 0, 0
        for piece in self.white:
            distances = [distance(piece, (x, y)) for (x, y) in self.white_goals if self.board[y][x] == '.']
            w_score += max(distances) if len(distances) else -50
        for piece in self.black:
            distances = [distance(piece, (x, y)) for (x, y) in self.black_goals if self.board[y][x] == '.']
            b_score += max(distances) if len(distances) else -50
        # print(w_score, b_score, w_score - b_score)
        if self.player == 'WHITE':
            return w_score - b_score
        else:
            return b_score - w_score

    def found_winner(self):
        no_space, all_opponent = True, True
        for (x, y) in self.white_goals:
            if self.board[y][x] == '.':
                no_space = False
            if self.board[y][x] == 'W':
                all_opponent = False
        if no_space and not all_opponent:
            return True

        no_space, all_opponent = True, True
        for (x, y) in self.black_goals:
            if self.board[y][x] == '.':
                no_space = False
            if self.board[y][x] == 'B':
                all_opponent = False
        if no_space and not all_opponent:
            return True
        return False


def max_value(state, alpha, beta, depth):
    if state.mode == 'GAME' and (depth == 0 or state.found_winner() or time.time() - state.start_time > 15):
        return state.utility(), None
    elif state.mode == 'SINGLE' and (
            depth == 0 or state.found_winner() or time.time() - state.start_time > state.time - 0.5):
        return state.utility(), None
    best_v, best_move = -float('inf'), None
    next_player = 'BLACK' if state.player == 'WHITE' else 'WHITE'
    moves = get_moves(state)
    for move in moves:
        # print(move)
        for t in move['To']:
            to = t[-2]
            new_board = copy.deepcopy(state.board)
            piece = new_board[move['From'][1]][move['From'][0]]
            new_board[move['From'][1]][move['From'][0]] = '.'
            new_board[to[1]][to[0]] = piece
            new_state = GameState(new_board, next_player, None, state.start_time, state.mode, state.time)
            # print((move['From'], to))
            # for i in new_board:
            #    print(i)
            new_v, _ = min_value(new_state, alpha, beta, depth - 1)
            # print('-----------------------------')
            # print(depth, new_v, best_v, best_move, (move['From'], to), new_v > best_v, alpha, beta)
            if new_v > best_v:
                best_v = new_v
                best_move = (t[0], move['From'], t[-1])
                alpha = max(alpha, new_v)
            if alpha >= beta:
                return best_v, best_move
            # print(depth, new_v, best_v, best_move, (move['From'], to), alpha, beta)
    # print(depth, best_v, best_move)
    return best_v, best_move


def min_value(state, alpha, beta, depth):
    if state.mode == 'GAME' and (depth == 0 or state.found_winner() or time.time() - state.start_time > 15):
        return state.utility(), None
    elif state.mode == 'SINGLE' and (
            depth == 0 or state.found_winner() or time.time() - state.start_time > state.time - 0.5):
        return state.utility(), None
    best_v, best_move = float('inf'), None
    next_player = 'BLACK' if state.player == 'WHITE' else 'WHITE'
    moves = get_moves(state)
    for move in moves:
        for t in move['To']:
            to = t[-2]
            new_board = copy.deepcopy(state.board)
            piece = new_board[move['From'][1]][move['From'][0]]
            new_board[move['From'][1]][move['From'][0]] = '.'
            new_board[to[1]][to[0]] = piece
            new_state = GameState(new_board, next_player, None, state.start_time, state.mode, state.time)
            # print('---------------------------------')
            # for i in new_board:
            # print(i)
            new_v, _ = max_value(new_state, alpha, beta, depth - 1)
            # print('-----------------------------')
            # print(depth, new_v, best_v, best_move, (move['From'], to), new_v < best_v, alpha, beta)
            if new_v < best_v:
                best_v = new_v
                best_move = (t[0], move['From'], t[-1])
                beta = min(beta, new_v)
            if alpha >= beta:
                return best_v, best_move
            # print(depth, new_v, best_v, best_move, (move['From'], to), alpha, beta)
    # print(depth, best_v, best_move)
    return best_v, best_move


def get_moves(state):
    player = state.player
    moves = []
    positions = state.white if player == 'WHITE' else state.black
    inside, outside = [], []
    for p in positions:
        if p in state.origins:
            # if there are pieces in own camp
            inside.append(p)
        else:
            outside.append(p)
    # Try moving a piece out of camp
    for p in inside:
        to, nodes, _ = valid_moves(state, p)
        if len(nodes):
            new_nodes = []
            for i in range(len(nodes)):
                node = nodes[i]
                if node[0] == 'E' and node[1] not in state.origins:
                    new_nodes.append(node)
                elif node[0] == 'J' and node[2] not in state.origins:
                    new_nodes.append(node)
            if len(new_nodes):
                move = {'From': p, 'To': new_nodes}
                moves.append(move)
    # Try moving a piece in camp further away from the corner of own camp
    if len(moves) == 0:
        for p in inside:
            to, nodes, _ = valid_moves(state, p, False, True)
            if len(nodes):
                move = {'From': p, 'To': nodes}
                # print(move)
                moves.append(move)
    # if cannot move any pieces in own camp out, free to move pieces outside of camp
    if len(moves) == 0:
        for p in outside:
            to, nodes, _ = valid_moves(state, p, True)
            if len(nodes):
                move = {'From': p, 'To': nodes}
                moves.append(move)

    return moves


def valid_moves(state, piece, free=False, further=False, moves=None, adj=True, nodes=None, current=None, previous=None):
    x, y = piece[0], piece[1]
    if moves is None:
        moves = []
    if nodes is None:
        nodes = []
    if previous is None:
        previous = []
    origins = state.origins
    goals = state.goals
    corner = state.corner

    for i in range(-1, 2):
        for j in range(-1, 2):
            new_x = x + i
            new_y = y + j
            new_piece = (new_x, new_y)
            if (new_x == x and new_y == y) or (not 0 <= new_x < 16) or (not 0 <= new_y < 16):
                continue
            if new_piece in origins and piece not in origins and adj:
                continue  # if moving back to own camp
            if piece in goals and new_piece not in goals:
                continue  # if moving out of opponent camp
            if piece in origins and further:
                # if free to move
                if (abs(new_y - corner) < abs(y - corner)) or (abs(new_x - corner) < abs(x - corner)):
                    continue

            new_cell = state.board[new_y][new_x]
            new_node = Node(None, new_piece)
            if new_cell == '.':
                if adj:
                    moves.append(('E', new_piece))
                    previous.append(new_piece)
                    nodes.append(('E', new_piece, new_node))
                continue

            # Check Jumps
            new_x = new_x + i
            new_y = new_y + j
            new_piece = (new_x, new_y)
            new_node = Node(current, new_piece)

            if (not 0 <= new_x < 16) or (not 0 <= new_y < 16):
                continue
            if new_piece in previous:
                continue
            if new_piece in origins and piece not in origins:
                continue  # if moving back to own camp
            if piece in goals and new_piece not in goals:
                continue  # if moving out of opponent camp
            if piece in origins and further:
                # if free to move
                if (abs(new_y - corner) < abs(y - corner)) or (abs(new_x - corner) < abs(x - corner)):
                    continue

            new_cell = state.board[new_y][new_x]
            if new_cell == '.':
                moves.insert(0, ('J', piece, new_piece))
                previous.insert(0, new_piece)
                nodes.insert(0, ('J', piece, new_piece, new_node))
                valid_moves(state, new_piece, free, further, moves, False, nodes, new_node, previous)

    return moves, nodes, previous


start = time.time()

file = open('input.txt', 'r')
lines = file.read().splitlines()
file.close()

play_mode = lines[0].strip()
current_player = lines[1].strip()
time_left = float(lines[2].strip())
max_depth = 1 if time_left > 100 else 1
init_board = [list(lines[i + 3].strip()) for i in range(16)]

game_state = GameState(init_board, current_player, None, start, play_mode, time_left)
next_move = max_value(game_state, -float('inf'), float('inf'), max_depth)

# print(next_move)
path = []
result = next_move[1][2] if next_move[1][1] is not None else None
current_point = next_move[1][1]
move_type = next_move[1][0]

output = open('output.txt', 'w')
if result is not None:
    while result.parent:
        path.append(result.child)
        result = result.parent
    path.append(result.child)
    path = path[::-1]
    for i in range(len(path)):
        # print('%s %d,%d %d,%d' % (move_type, current_point[0], current_point[1], path[i][0], path[i][1]))
        end = '\n' if i != len(path) - 1 else ''
        print('%s %d,%d %d,%d' % (move_type, current_point[0], current_point[1], path[i][0], path[i][1]), end=end, file=output)
        current_point = path[i]
output.close()
# print('%s seconds' % (time.time() - start))
