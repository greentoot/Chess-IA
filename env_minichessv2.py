# chess_ai/env_minichess.py
import numpy as np

EMPTY, PAWN, ROOK, KNIGHT = 0, 1, 2, 3
WHITE, BLACK = 1, -1

PIECE_NAMES = {EMPTY: '.', PAWN: 'P', ROOK: 'R', KNIGHT: 'N'}
PIECE_VALUES = {PAWN: 1, KNIGHT: 3, ROOK: 5}

class MiniChessEnv6x6:
    def __init__(self):
        self.reset()

    def reset(self):
        self.board = np.zeros((6, 6), dtype=int)
        self.color_board = np.zeros((6, 6), dtype=int)

        # Place white pieces
        self.board[5] = PAWN
        self.color_board[5] = WHITE
        self.board[4][0] = ROOK
        self.board[4][5] = ROOK
        self.board[4][1] = KNIGHT
        self.board[4][4] = KNIGHT
        self.color_board[4] = WHITE

        # Place black pieces
        self.board[0] = PAWN
        self.color_board[0] = BLACK
        self.board[1][0] = ROOK
        self.board[1][5] = ROOK
        self.board[1][1] = KNIGHT
        self.board[1][4] = KNIGHT
        self.color_board[1] = BLACK

        self.current_player = WHITE
        self.done = False
        return self.get_state()

    def get_state(self):
        return self.board.copy(), self.color_board.copy(), self.current_player

    def get_valid_moves(self):
        moves = []
        for x in range(6):
            for y in range(6):
                if self.color_board[x][y] == self.current_player:
                    piece = self.board[x][y]
                    if piece == PAWN:
                        piece_moves = self._pawn_moves(x, y)
                    elif piece == ROOK:
                        piece_moves = self._rook_moves(x, y)
                    elif piece == KNIGHT:
                        piece_moves = self._knight_moves(x, y)
                    else:
                        piece_moves = []
                    moves.extend(piece_moves)
        return moves

    def _pawn_moves(self, x, y):
        moves = []
        dx = -1 if self.current_player == WHITE else 1
        nx = x + dx
        if 0 <= nx < 6:
            if self.board[nx][y] == 0:
                moves.append(((x, y), (nx, y)))
            for dy in [-1, 1]:
                ny = y + dy
                if 0 <= ny < 6 and self.color_board[nx][ny] == -self.current_player:
                    moves.append(((x, y), (nx, ny)))
        return moves

    def _rook_moves(self, x, y):
        moves = []
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            step = 1
            while True:
                nx, ny = x + dx*step, y + dy*step
                if 0 <= nx < 6 and 0 <= ny < 6:
                    if self.board[nx][ny] == 0:
                        moves.append(((x, y), (nx, ny)))
                    elif self.color_board[nx][ny] == -self.current_player:
                        moves.append(((x, y), (nx, ny)))
                        break
                    else:
                        break
                else:
                    break
                step += 1
        return moves

    def _knight_moves(self, x, y):
        moves = []
        for dx, dy in [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < 6 and 0 <= ny < 6:
                if self.color_board[nx][ny] != self.current_player:
                    moves.append(((x, y), (nx, ny)))
        return moves

    def step(self, move):
        (x1, y1), (x2, y2) = move
        reward = 0.0

        captured_piece = self.board[x2][y2]
        captured_color = self.color_board[x2][y2]

        if captured_color == -self.current_player:
            reward += PIECE_VALUES.get(captured_piece, 0)

        self.board[x2][y2] = self.board[x1][y1]
        self.color_board[x2][y2] = self.current_player
        self.board[x1][y1] = EMPTY
        self.color_board[x1][y1] = 0

        self.current_player *= -1

        # Vérifier si l'adversaire a encore des pièces
        if not np.any(self.color_board == self.current_player):
            self.done = True
            print(f"🏆 Joueur {'Blanc' if -self.current_player == WHITE else 'Noir'} gagne (plus de pièces ennemies)!")
            reward += 20.0
            return self.get_state(), reward, self.done
        
        # Vérifier s'il y a encore des coups possibles
        if len(self.get_valid_moves()) == 0:
            self.done = True
            white_score = sum(PIECE_VALUES.get(self.board[i][j], 0) for i in range(6) for j in range(6) if self.color_board[i][j] == WHITE)
            black_score = sum(PIECE_VALUES.get(self.board[i][j], 0) for i in range(6) for j in range(6) if self.color_board[i][j] == BLACK)
            if white_score > black_score:
                print("🏁 Fin de partie : Blanc gagne par majorité de valeur.")
                reward += 15.0 if self.current_player == BLACK else -15.0
            elif black_score > white_score:
                print("🏁 Fin de partie : Noir gagne par majorité de valeur.")
                reward += 15.0 if self.current_player == WHITE else -15.0
            else:
                print("⚖️ Match nul (égalité parfaite).")
            return self.get_state(), reward, self.done

        return self.get_state(), reward, self.done

    def render(self):
        print("\n  A B C D E F")
        for i in range(6):
            row = [PIECE_NAMES[self.board[i][j]] if self.color_board[i][j] == 0 else
                   (PIECE_NAMES[self.board[i][j]].lower() if self.color_board[i][j] == BLACK else PIECE_NAMES[self.board[i][j]])
                   for j in range(6)]
            print(f"{6 - i} {' '.join(row)}")
