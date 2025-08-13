
import pygame
import sys
import time
import math
import copy

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w"

PIECE_VALUES = {'p':100, 'n':320, 'b':330, 'r':500, 'q':900, 'k':20000}

class Board:
    def __init__(self):
        self.board = [['' for _ in range(8)] for __ in range(8)]
        self.white_to_move = True
        self.move_stack = [] 
        self.set_start_position()

    def set_start_position(self):
        fen, side = START_FEN.split(' w') if ' w' in START_FEN else (START_FEN, 'w')
        fen = START_FEN.split()[0]
        rows = fen.split('/')
        for r in range(8):
            row = rows[r]
            c = 0
            for ch in row:
                if ch.isdigit():
                    c += int(ch)
                else:
                    color = 'w' if ch.isupper() else 'b'
                    piece = ch.lower()
                    self.board[r][c] = color + piece
                    c += 1
        self.white_to_move = (START_FEN.split()[1] == 'w') if len(START_FEN.split()) > 1 else True

    def clone(self):
        b = Board()
        b.board = [row.copy() for row in self.board]
        b.white_to_move = self.white_to_move
        b.move_stack = self.move_stack.copy()
        return b

    def in_bounds(self, r, c):
        return 0 <= r < 8 and 0 <= c < 8

    def is_empty(self, r, c):
        return self.in_bounds(r, c) and self.board[r][c] == ''

    def piece_at(self, r, c):
        return self.board[r][c] if self.in_bounds(r, c) else None

    def make_move(self, move):
        (sr, sc), (tr, tc), promo = move
        moving = self.board[sr][sc]
        captured = self.board[tr][tc]
        self.board[tr][tc] = moving
        self.board[sr][sc] = ''
        if promo and moving[1] == 'p' and (tr == 0 or tr == 7):
            self.board[tr][tc] = moving[0] + promo
        self.white_to_move = not self.white_to_move
        self.move_stack.append(((sr, sc), (tr, tc), moving, captured, promo))

    def undo_move(self):
        if not self.move_stack: return
        (sr, sc), (tr, tc), moving, captured, promo = self.move_stack.pop()
        self.board[sr][sc] = moving
        self.board[tr][tc] = captured
        self.white_to_move = not self.white_to_move

    def all_moves(self):
        color = 'w' if self.white_to_move else 'b'
        moves = []
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p != '' and p[0] == color:
                    piece_type = p[1]
                    moves.extend(self.piece_moves(r, c, piece_type, color))

        legal = []
        for m in moves:
            self.make_move(m)

            if not self.is_in_check(color):
                legal.append(m)
            self.undo_move()
        return legal


    def piece_moves(self, r, c, piece, color):
        moves = []
        enemy = 'b' if color == 'w' else 'w'
        if piece == 'p':
            dir = -1 if color == 'w' else 1
            start = 6 if color == 'w' else 1
            if self.in_bounds(r+dir, c) and self.board[r+dir][c] == '':
                if (r+dir == 0) or (r+dir == 7):
                    for promo in ['q','r','b','n']:
                        moves.append(((r,c),(r+dir,c),promo))
                else:
                    moves.append(((r,c),(r+dir,c),None))
                    
                    if r == start and self.board[r+2*dir][c] == '':
                        moves.append(((r,c),(r+2*dir,c),None))
            for dc in (-1,1):
                nr, nc = r+dir, c+dc
                if self.in_bounds(nr,nc) and self.board[nr][nc] != '' and self.board[nr][nc][0] == enemy:
                    if (nr == 0) or (nr == 7):
                        for promo in ['q','r','b','n']:
                            moves.append(((r,c),(nr,nc),promo))
                    else:
                        moves.append(((r,c),(nr,nc),None))
        elif piece == 'n':
            for dr,dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
                nr, nc = r+dr, c+dc
                if not self.in_bounds(nr,nc): continue
                if self.board[nr][nc] == '' or self.board[nr][nc][0] == enemy:
                    moves.append(((r,c),(nr,nc),None))
        elif piece == 'b' or piece == 'r' or piece == 'q':
            dirs = []
            if piece in ('b','q'):
                dirs += [(-1,-1),(-1,1),(1,-1),(1,1)]
            if piece in ('r','q'):
                dirs += [(-1,0),(1,0),(0,-1),(0,1)]
            for dr,dc in dirs:
                nr, nc = r+dr, c+dc
                while self.in_bounds(nr,nc):
                    if self.board[nr][nc] == '':
                        moves.append(((r,c),(nr,nc),None))
                    else:
                        if self.board[nr][nc][0] == enemy:
                            moves.append(((r,c),(nr,nc),None))
                        break
                    nr += dr; nc += dc
        elif piece == 'k':
            for dr in (-1,0,1):
                for dc in (-1,0,1):
                    if dr==0 and dc==0: continue
                    nr, nc = r+dr, c+dc
                    if not self.in_bounds(nr,nc): continue
                    if self.board[nr][nc] == '' or self.board[nr][nc][0] == enemy:
                        moves.append(((r,c),(nr,nc),None))
        return moves

    def find_king(self, color):
        for r in range(8):
            for c in range(8):
                if self.board[r][c] == color + 'k':
                    return (r,c)
        return None

    def is_in_check(self, color):
        king_pos = self.find_king(color)
        if not king_pos: return False
        kr,kc = king_pos
        enemy = 'b' if color == 'w' else 'w'
        pawn_row = kr + (1 if enemy == 'w' else -1)
        for dc in (-1, 1):
            r = pawn_row
            c = kc + dc
            if self.in_bounds(r, c) and self.board[r][c] == enemy + 'p':
                return True

        for dr,dc in [(2,1),(2,-1),(-2,1),(-2,-1),(1,2),(1,-2),(-1,2),(-1,-2)]:
            r,c = kr+dr, kc+dc
            if self.in_bounds(r,c) and self.board[r][c] == enemy + 'n':
                return True

        for dr,dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = kr+dr, kc+dc
            while self.in_bounds(nr,nc):
                p = self.board[nr][nc]
                if p != '':
                    if p[0] == enemy and (p[1]=='r' or p[1]=='q'):
                        return True
                    break
                nr += dr; nc += dc
        for dr,dc in [(-1,-1),(-1,1),(1,-1),(1,1)]:
            nr, nc = kr+dr, kc+dc
            while self.in_bounds(nr,nc):
                p = self.board[nr][nc]
                if p != '':
                    if p[0] == enemy and (p[1]=='b' or p[1]=='q'):
                        return True
                    break
                nr += dr; nc += dc
        for dr in (-1,0,1):
            for dc in (-1,0,1):
                if dr==0 and dc==0: continue
                r,c = kr+dr, kc+dc
                if self.in_bounds(r,c) and self.board[r][c] == enemy+'k':
                    return True
        return False

    def evaluate(self):
        score = 0
        for r in range(8):
            for c in range(8):
                p = self.board[r][c]
                if p != '':
                    val = PIECE_VALUES[p[1]]
                    if p[0] == 'w': score += val
                    else: score -= val
        return score

    def game_over(self):
        moves = self.all_moves()
        if len(moves) == 0:
            if self.is_in_check('w' if self.white_to_move else 'b'):
                return 'checkmate'
            else:
                return 'stalemate'
        return None


def minimax(board, depth, alpha, beta, maximizing):
    over = board.game_over()
    if depth == 0 or over is not None:
        if over == 'checkmate':
            return (None, -999999 if maximizing else 999999)
        if over == 'stalemate':
            return (None, 0)
        return (None, board.evaluate())

    best_move = None
    if maximizing:
        max_eval = -10**9
        for m in board.all_moves():
            board.make_move(m)
            _, eval = minimax(board, depth-1, alpha, beta, False)
            board.undo_move()
            if eval > max_eval:
                max_eval = eval; best_move = m
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return (best_move, max_eval)
    else:
        min_eval = 10**9
        for m in board.all_moves():
            board.make_move(m)
            _, eval = minimax(board, depth-1, alpha, beta, True)
            board.undo_move()
            if eval < min_eval:
                min_eval = eval; best_move = m
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return (best_move, min_eval)


SQUARE = 64
WIDTH, HEIGHT = 8*SQUARE, 8*SQUARE

def load_piece_images():
    images = {}
    names = ['p','r','n','b','q','k']
    for color in ('w','b'):
        for n in names:
            key = color + n
            filename = f'assets/{key}.png'
            try:
                img = pygame.image.load(filename)
                img = pygame.transform.smoothscale(img, (SQUARE, SQUARE))
                images[key] = img
            except Exception as e:
                images[key] = None
    return images

def draw_board(screen, board_obj, images, selected, legal_moves):
    colors = [(240,217,181),(181,136,99)]
    for r in range(8):
        for c in range(8):
            color = colors[(r+c) % 2]
            pygame.draw.rect(screen, color, (c*SQUARE, r*SQUARE, SQUARE, SQUARE))
    if selected:
        sr, sc = selected
        pygame.draw.rect(screen, (255,255,0,80), (sc*SQUARE, sr*SQUARE, SQUARE, SQUARE), 4)
    for m in legal_moves:
        (_, _), (tr, tc), _ = m
        center = (tc*SQUARE + SQUARE//2, tr*SQUARE + SQUARE//2)
        pygame.draw.circle(screen, (0,0,0), center, 8)
    for r in range(8):
        for c in range(8):
            p = board_obj.board[r][c]
            if p != '':
                key = p
                img = images.get(key)
                if img:
                    screen.blit(img, (c*SQUARE, r*SQUARE))
                else:
                    pygame.draw.circle(screen, (0,0,0), (c*SQUARE + SQUARE//2, r*SQUARE + SQUARE//2), SQUARE//2 - 6)
                    font = pygame.font.SysFont(None, 28)
                    txt = font.render(p[1].upper(), True, (255,255,255))
                    screen.blit(txt, (c*SQUARE+6, r*SQUARE+10))

def coords_from_mouse(pos):
    x,y = pos
    c = x // SQUARE
    r = y // SQUARE
    return (r,c)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Chess - AI from scratch')
    clock = pygame.time.Clock()
    images = load_piece_images()

    board = Board()
    selected = None
    legal = []
    ai_depth = 5
    human_plays_white = True

    running = True
    thinking = False
    ai_move_start_time = 0

    while running:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and not thinking:
                pos = pygame.mouse.get_pos()
                r,c = coords_from_mouse(pos)
                if selected is None:
                    piece = board.piece_at(r,c)
                    if piece != '' and ((piece[0]=='w') == board.white_to_move):
                        selected = (r,c)
                        all_moves = board.all_moves()
                        legal = [m for m in all_moves if m[0] == (r,c)]
                else:
                    candidate = None
                    for m in legal:
                        if m[1] == (r,c):
                            candidate = m; break
                    if candidate:
                        board.make_move(candidate)
                        selected = None; legal = []
                    else:
                        piece = board.piece_at(r,c)
                        if piece != '' and ((piece[0]=='w') == board.white_to_move):
                            selected = (r,c)
                            all_moves = board.all_moves()
                            legal = [m for m in all_moves if m[0] == (r,c)]
                        else:
                            selected = None; legal = []

        if (board.white_to_move and not human_plays_white) or (not board.white_to_move and human_plays_white):
            if not thinking:
                thinking = True
                ai_move_start_time = time.time()
                best_move, val = minimax(board, ai_depth, -10**9, 10**9, board.white_to_move)
                if best_move is not None:
                    board.make_move(best_move)
                thinking = False
                print(f"AI played in {time.time() - ai_move_start_time:.2f}s, eval={val}")

        screen.fill((0,0,0))
        draw_board(screen, board, images, selected, legal)

        font = pygame.font.SysFont(None, 20)
        turn_text = 'White' if board.white_to_move else 'Black'
        txt = font.render(f'Turn: {turn_text}  (AI depth {ai_depth})', True, (255,255,255))
        screen.blit(txt, (4, HEIGHT-22))

        over = board.game_over()
        if over:
            big = pygame.font.SysFont(None, 48)
            if over == 'checkmate':
                winner = 'Black' if board.white_to_move else 'White'
                msg = f'Checkmate — {winner} wins'
            else:
                msg = 'Stalemate'
            surf = big.render(msg, True, (255,0,0))
            screen.blit(surf, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
