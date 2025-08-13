# chess_ai/gui_play_with_images.py
import pygame
from env_minichess import MiniChessEnv6x6
from agent_qlearning import QLearningAgent
import os

pygame.init()

# Constantes GUI
WIDTH, HEIGHT = 480, 480
ROWS, COLS = 6, 6
SQUARE_SIZE = WIDTH // COLS

WHITE = (240, 217, 181)
BROWN = (181, 136, 99)
HIGHLIGHT = (0, 255, 0)
BLACK_COLOR = (50, 50, 50)

PIECE_TO_ASSET = {
    (1,  1): 'wp.png',  # White pawn
    (2,  1): 'wr.png',  # White rook
    (3,  1): 'wn.png',  # White knight
    (1, -1): 'bp.png',  # Black pawn
    (2, -1): 'br.png',  # Black rook
    (3, -1): 'bn.png',  # Black knight
}

ASSETS_DIR = 'assets'

def load_images():
    images = {}
    for key, filename in PIECE_TO_ASSET.items():
        path = os.path.join(ASSETS_DIR, filename)
        img = pygame.image.load(path)
        images[key] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
    return images

env = MiniChessEnv6x6()
agent = QLearningAgent()
try:
    agent.load("black_agent.pkl")
except Exception:
    print("Aucun agent chargé, l'IA jouera aléatoirement.")

screen = pygame.display.set_mode((WIDTH, HEIGHT + 40))
pygame.display.set_caption("MiniChess 6x6 - Humain Blanc vs IA Noir")

images = load_images()

selected = None
valid_moves = []
running = True
state = env.reset()
game_over = False

font_info = pygame.font.SysFont('Arial', 24)
prev_state = state

def draw_board():
    for row in range(ROWS):
        for col in range(COLS):
            color = WHITE if (row + col) % 2 == 0 else BROWN
            pygame.draw.rect(screen, color, (col*SQUARE_SIZE, row*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

def draw_pieces():
    board, color_board, _ = state
    for row in range(ROWS):
        for col in range(COLS):
            piece = board[row][col]
            color = color_board[row][col]
            if piece != 0 and color != 0:
                key = (piece, color)
                img = images.get(key)
                if img:
                    screen.blit(img, (col * SQUARE_SIZE, row * SQUARE_SIZE))

def highlight_squares(moves):
    for ((x1, y1), (x2, y2)) in moves:
        if selected == (x1, y1):
            pygame.draw.rect(screen, HIGHLIGHT, (y2*SQUARE_SIZE, x2*SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE), 4)

def draw_info():
    turn = "Blancs (Vous)" if state[2] == 1 else "Noirs (IA)"
    text = font_info.render(f"Tour : {turn}", True, (10, 10, 10))
    screen.blit(text, (10, HEIGHT + 10))

def pos_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def ai_move():
    global state, valid_moves, selected, game_over, prev_state
    valid_moves = env.get_valid_moves()
    action = agent.choose_action(state, valid_moves)
    if action is None:
        game_over = True
        return
    next_state, reward, done = env.step(action)
    next_valid_moves = env.get_valid_moves()
    agent.learn(state, action, reward, next_state, done, next_valid_moves)
    state = next_state
    prev_state = state
    if done:
        game_over = True
    valid_moves = env.get_valid_moves()
    selected = None

while running:
    draw_board()
    draw_pieces()
    highlight_squares(valid_moves)
    draw_info()
    pygame.display.flip()

    if game_over:
        agent.save("black_agent.pkl")
        pygame.time.wait(3000)
        running = False
        continue

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and state[2] == 1 and not game_over:
            pos = pos_from_mouse(event.pos)
            board, color_board, current_player = state

            if selected is None:
                if color_board[pos[0]][pos[1]] == 1:
                    selected = pos
                    valid_moves = [m for m in env.get_valid_moves() if m[0] == selected]
                else:
                    selected = None
                    valid_moves = []
            else:
                move = (selected, pos)
                if move in valid_moves:
                    state, reward, done = env.step(move)
                    if done:
                        print("Partie terminée.")
                        agent.save("black_agent.pkl")
                        game_over = True
                    else:
                        ai_move()
                selected = None
                valid_moves = []

pygame.quit()
