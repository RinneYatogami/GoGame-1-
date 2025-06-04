import copy
import random

class GoAI:
    def __init__(self, board_size=9):
        self.size = board_size
        # Hệ số thưởng/phạt
        self.capture_weight = 2.0  
        self.cut_weight = 1.5     
        self.territory_weight = 0.7
        self.influence_weight = 0.5
        self.life_weight = 1.3
        self.connections_weight = 1.2
        self.isolate_weight = 1.0
        self.efficient_weight = 0.5

    def get_neighbors(self, board, x, y):
        neighbors = []
        if x > 0:
            neighbors.append((x - 1, y))
        if x < self.size - 1:
            neighbors.append((x + 1, y))
        if y > 0:
            neighbors.append((x, y - 1))
        if y < self.size - 1:
            neighbors.append((x, y + 1))
        return neighbors

    def get_group(self, board, x, y):
        color = board[x][y]
        if color == 0:
            return []
        visited = set()
        stack = [(x, y)]
        group = []
        while stack:
            cx, cy = stack.pop()
            if (cx, cy) in visited:
                continue
            visited.add((cx, cy))
            group.append((cx, cy))
            for nx, ny in self.get_neighbors(board, cx, cy):
                if board[nx][ny] == color and (nx, ny) not in visited:
                    stack.append((nx, ny))
        return group

    def count_liberties(self, board, group):
        liberties = set()
        for x, y in group:
            for nx, ny in self.get_neighbors(board, x, y):
                if board[nx][ny] == 0:
                    liberties.add((nx, ny))
        return len(liberties)

    def remove_group(self, board, group):
        for x, y in group:
            board[x][y] = 0

    def is_suicide(self, board, x, y, color):
        temp = copy.deepcopy(board)
        temp[x][y] = color
        opp_color = 1 if color == 2 else 2
        for nx, ny in self.get_neighbors(temp, x, y):
            if temp[nx][ny] == opp_color:
                grp = self.get_group(temp, nx, ny)
                if self.count_liberties(temp, grp) == 0:
                    self.remove_group(temp, grp)
        grp = self.get_group(temp, x, y)
        return self.count_liberties(temp, grp) == 0

    def is_eye(self, board, x, y, color):
        for nx, ny in self.get_neighbors(board, x, y):
            if board[nx][ny] != color:
                return False
        opp_color = 1 if color == 2 else 2
        diag_coords = [
            (x-1, y-1), (x-1, y+1),
            (x+1, y-1), (x+1, y+1)
        ]
        bad_diagonals = 0
        for dx, dy in diag_coords:
            if 0 <= dx < self.size and 0 <= dy < self.size:
                if board[dx][dy] == opp_color:
                    bad_diagonals += 1
        return (bad_diagonals<=1)
#===================================================================================
    def count_eyes(self, board, group, color):
        # Đếm mắt thực: các ô trống được xác nhận bởi is_eye và liền kề nhóm
        eyes = set()
        for x, y in group:
            for nx, ny in self.get_neighbors(board, x, y):
                if board[nx][ny] != 0 or (nx, ny) in eyes:
                    continue
                if self.is_eye(board, nx, ny, color):
                    eyes.add((nx, ny))
        return len(eyes)
#==================================================================================
    def valid_moves_sim(self, board, color):
        moves = []
        for x in range(self.size):
            for y in range(self.size):
                if board[x][y] != 0:
                    continue
                if self.is_suicide(board, x, y, color):
                    continue
                # Loại bỏ nước đi vào mắt của chính mình
                if self.is_eye(board, x, y, color):
                    continue
                moves.append((x, y))
        return moves

    def simulate_move_state(self, board, x, y, color):
        new_board = copy.deepcopy(board)
        new_board[x][y] = color
        opp_color = 1 if color == 2 else 2
        captured = 0
        # Bắt quân: nếu nhóm đối phương mất hoàn toàn liberties
        for nx, ny in self.get_neighbors(new_board, x, y):
            if new_board[nx][ny] == opp_color:
                grp = self.get_group(new_board, nx, ny)
                if self.count_liberties(new_board, grp) == 0:
                    captured += len(grp)
                    self.remove_group(new_board, grp)
        return new_board, captured

    def evaluate_board(self, board):
        score = 0
        visited = set()

        for x in range(self.size):
            for y in range(self.size):
                color = board[x][y]
                if color == 0 or (x, y) in visited:
                    continue

                if color==1:
                    for dx, dy in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.size and 0 <= ny < self.size:
                            if self.is_eye(board, nx, ny, 1):
                                score += 20  # cộng ít thôi để tránh overfitting

                grp = self.get_group(board, x, y)
                libs = self.count_liberties(board, grp)
                visited.update(grp)
                size_grp = len(grp)
                #========================================
                eyes = self.count_eyes(board, grp, color)
                #========================================
                if color == 2:
                    # Ảnh hưởng & lãnh thổ
                    border_cnt = sum(1 for gx, gy in grp if gx in (0, self.size-1) or gy in (0, self.size-1))
                    territory = 1.5 * border_cnt
                    influence = (size_grp - border_cnt)
                    # Sống còn
                    life = -5 * size_grp if libs < 2 else (1*size_grp if libs == 2 else 2*size_grp)
                    # Kết nối
                    connections = sum(1 for gx, gy in grp for nx, ny in self.get_neighbors(board, gx, gy)
                                      if board[nx][ny] == 2 and (nx, ny) not in grp)
                    isolate = -3 if connections == 0 else 0
                    # Hiệu quả
                    efficient = libs / size_grp

                    score += territory * self.territory_weight
                    score += influence * self.influence_weight
                    score += life * self.life_weight
                    score += connections * self.life_weight
                    score += isolate * self.isolate_weight
                    score += efficient * self.efficient_weight

                #============================================
                    if eyes >= 2:
                        score += self.life_weight*size_grp
                #============================================

                else:
                    # Tấn công nhóm yếu
                    if libs <= 2:
                        score += (3 - libs) * size_grp * self.capture_weight  # tăng trọng số tấn công
                    # cắt đứt
                    cuts = sum(1 for gx, gy in grp for nx, ny in self.get_neighbors(board, gx, gy)
                               if board[nx][ny] == 2)
                    score += cuts * self.cut_weight
        return score

    def minimax(self, board, depth, alpha, beta, maximizing):
        color = 2 if maximizing else 1
        moves = self.valid_moves_sim(board, color)
        if depth == 0 or not moves:
            return self.evaluate_board(board), None

        best_move = None
        if maximizing:
            max_eval = -float('inf')
            for move in moves:
                new_b, captured = self.simulate_move_state(board, move[0], move[1], color)
                eval_score, _ = self.minimax(new_b, depth-1, alpha, beta, False)
                # thưởng bắt quân
                eval_score += captured * self.capture_weight
                if eval_score > max_eval:
                    max_eval = eval_score
                    best_move = move
                alpha = max(alpha, eval_score)
                if beta <= alpha:
                    break
            return max_eval, best_move
        else:
            min_eval = float('inf')
            for move in moves:
                new_b, captured = self.simulate_move_state(board, move[0], move[1], color)
                eval_score, _ = self.minimax(new_b, depth-1, alpha, beta, True)
                eval_score -= captured * self.capture_weight
                if eval_score < min_eval:
                    min_eval = eval_score
                    best_move = move
                beta = min(beta, eval_score)
                if beta <= alpha:
                    break
            return min_eval, best_move
