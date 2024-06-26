import pygame
import chess
import random
import time
import sys

# Pygame initialization
pygame.init()

# Constants
SCREEN_WIDTH, SCREEN_HEIGHT = 1000, 600  # Increased width for side panel
BOARD_SIZE = 600  # Fixed board size
SQ_SIZE = BOARD_SIZE // 8
FPS = 30
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BUTTON_COLOR = (70, 130, 180)
HOVER_COLOR = (100, 149, 237)
HIGHLIGHT_COLOR = pygame.Color("yellow")
SIDEPANEL_WIDTH = SCREEN_WIDTH - BOARD_SIZE
SIDEPANEL_PADDING = 20
FONT_COLOR = BLACK

# Load chessboard image
board_image = pygame.image.load("images/chessboard.jpeg")
board_image = pygame.transform.scale(board_image, (BOARD_SIZE, BOARD_SIZE))

# Initialize screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Chess Game")


# Fonts
font = pygame.font.SysFont("Arial", 32, bold=True)
button_font = pygame.font.SysFont("Arial", 28)
small_font = pygame.font.SysFont("Arial", 24)
underline_font = pygame.font.SysFont("Arial", 24, bold=True)
underline_font.set_underline(True)

# Helper function to draw text
def draw_text(text, font, color, surface, x, y):
    textobj = font.render(text, True, color)
    textrect = textobj.get_rect(center=(x, y))
    surface.blit(textobj, textrect)

# Helper function to draw button
def draw_button(text, rect, color, hover_color, font, surface):
    mouse_pos = pygame.mouse.get_pos()
    if rect.collidepoint(mouse_pos):
        pygame.draw.rect(surface, hover_color, rect)
    else:
        pygame.draw.rect(surface, color, rect)
    draw_text(text, font, WHITE, surface, rect.centerx, rect.centery)

# Helper function to draw board
def draw_board(board, selected_square=None):
    screen.blit(board_image, (0, 0))
    for row in range(8):
        for col in range(8):
            square = chess.square(col, 7 - row)
            piece = board.piece_at(square)
            if selected_square == square:
                pygame.draw.rect(screen, HIGHLIGHT_COLOR, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE), 5)
            if piece:
                piece_color = 'W' if piece.color == chess.WHITE else 'B'
                piece_type = piece.symbol().upper()
                piece_image = pygame.image.load(f"images/{piece_color}{piece_type}.png")
                piece_image = pygame.transform.scale(piece_image, (SQ_SIZE, SQ_SIZE))
                screen.blit(piece_image, pygame.Rect(col * SQ_SIZE, row * SQ_SIZE, SQ_SIZE, SQ_SIZE))

# Helper function to draw side panel
def draw_side_panel(time_white, time_black, captured_white, captured_black):
    pygame.draw.rect(screen, WHITE, (BOARD_SIZE, 0, SIDEPANEL_WIDTH, SCREEN_HEIGHT))

    # Draw timers with underlined title
    draw_text("White's Time:", underline_font, FONT_COLOR, screen, BOARD_SIZE + SIDEPANEL_WIDTH // 2, 50)
    draw_text(time.strftime("%M:%S", time.gmtime(time_white)), small_font, FONT_COLOR, screen, BOARD_SIZE + SIDEPANEL_WIDTH // 2, 80)

    draw_text("Black's Time:", underline_font, FONT_COLOR, screen, BOARD_SIZE + SIDEPANEL_WIDTH // 2, 150)
    draw_text(time.strftime("%M:%S", time.gmtime(time_black)), small_font, FONT_COLOR, screen, BOARD_SIZE + SIDEPANEL_WIDTH // 2, 180)

    # Draw captured pieces with underlined title
    draw_text("Captured by White:", underline_font, FONT_COLOR, screen, BOARD_SIZE + SIDEPANEL_WIDTH // 2, 250)
    for i, piece in enumerate(captured_black):
        piece_image = pygame.image.load(f"images/B{piece.upper()}.png")
        piece_image = pygame.transform.scale(piece_image, (SQ_SIZE // 2, SQ_SIZE // 2))
        screen.blit(piece_image, (BOARD_SIZE + SIDEPANEL_PADDING + (i * SQ_SIZE // 2), 280))

    draw_text("Captured by Black:", underline_font, FONT_COLOR, screen, BOARD_SIZE + SIDEPANEL_WIDTH // 2, 350)
    for i, piece in enumerate(captured_white):
        piece_image = pygame.image.load(f"images/W{piece.upper()}.png")
        piece_image = pygame.transform.scale(piece_image, (SQ_SIZE // 2, SQ_SIZE // 2))
        screen.blit(piece_image, (BOARD_SIZE + SIDEPANEL_PADDING + (i * SQ_SIZE // 2), 380))

# Get square from coordinates
def get_square(x, y):
    file = x // SQ_SIZE
    rank = 7 - (y // SQ_SIZE)  # Invert because Pygame y=0 is top
    return chess.square(file, rank)

# AI player function
def random_player(board):
    return random.choice(list(board.legal_moves)).uci()

# Human player function
def human_player(board, get_move):
    return get_move(board)

def player5(board):
    score_and_move = alphabeta(board, 3, -float('inf'), float('inf'))
    move = score_and_move[1]
    return move.uci()

def alphabeta(board, depth, alpha, beta):
    # Returns a tuple (score, bestmove) for the position at the given depth
    if depth == 0 or board.is_checkmate() or board.is_stalemate() or board.is_fifty_moves():
        return [staticAnalysis5(board), None]
    else:
        if board.turn == chess.WHITE:
            bestmove = None
            for move in board.legal_moves:
                newboard = board.copy()
                newboard.push(move)
                score_and_move = alphabeta(newboard, depth - 1, alpha, beta)
                score = score_and_move[0]
                if score > alpha:  # white maximizes her score
                    alpha = score
                    bestmove = move
                if alpha >= beta:  # alpha-beta cutoff
                    break
            return [alpha, bestmove]
        else:
            bestmove = None
            for move in board.legal_moves:
                newboard = board.copy()
                newboard.push(move)
                score_and_move = alphabeta(newboard, depth - 1, alpha, beta)
                score = score_and_move[0]
                if score < beta:  # black minimizes his score
                    beta = score
                    bestmove = move
                if alpha >= beta:  # alpha-beta cutoff
                    break
            return [beta, bestmove]

def staticAnalysis5(board):
    score = random.random()
    for (piece, value) in [
        (chess.PAWN, 1),
        (chess.BISHOP, 3),
        (chess.KING, 0),
        (chess.QUEEN, 9),
        (chess.KNIGHT, 3),
        (chess.ROOK, 5)
    ]:
        score += len(board.pieces(piece, chess.WHITE)) * value
        score -= len(board.pieces(piece, chess.BLACK)) * value
        # can also check things about the pieces' position here

    # Check global things about the board
    if board.turn == chess.BLACK and board.is_checkmate():
        score += 100
    if board.turn == chess.WHITE and board.is_checkmate():
        score -= 100

    return score

# Get move function
def get_move(board):
    selected_square = None
    move = None
    while move is None:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    x, y = event.pos
                    if x < BOARD_SIZE:
                        square = get_square(x, y)
                        if selected_square is None:
                            selected_square = square
                        else:
                            move = chess.Move(selected_square, square)
                            if move not in board.legal_moves:
                                move = None
                            else:
                                # Check for pawn promotion
                                if board.piece_at(selected_square).piece_type == chess.PAWN and (chess.square_rank(square) == 0 or chess.square_rank(square) == 7):
                                    uci_move = move.uci() + 'q'
                                    move = chess.Move.from_uci(uci_move)
                            selected_square = None
        draw_board(board, selected_square)
        pygame.display.flip()
        time.sleep(0.1)
    return move.uci()

# Main game function
def play_game(player1, player2):
    board = chess.Board()
    clock = pygame.time.Clock()
    start_time = time.time()
    white_time, black_time = 0, 0
    captured_white, captured_black = [], []

    while True:
        current_time = time.time()
        if board.turn == chess.WHITE:
            white_time = current_time - start_time
        else:
            black_time = current_time - start_time
        
        draw_board(board)
        draw_side_panel(white_time, black_time, captured_white, captured_black)
        pygame.display.flip()

        if board.is_game_over():
            game_over_message = "Game Over: "
            if board.is_checkmate():
                winner = "White" if board.turn == chess.BLACK else "Black"
                game_over_message += f"Checkmate, {winner} wins!"
            elif board.is_stalemate():
                game_over_message += "Draw (Stalemate)"
            elif board.is_insufficient_material():
                game_over_message += "Draw (Insufficient Material)"
            elif board.is_seventyfive_moves():
                game_over_message += "Draw (75-move rule)"
            elif board.is_fivefold_repetition():
                game_over_message += "Draw (Fivefold Repetition)"
            elif board.is_variant_draw():
                game_over_message += "Draw"
            
            draw_board(board)
            draw_text(game_over_message, font, BLACK, screen, SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)

            # Create button for going back to menu
            button_menu = pygame.Rect(SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT - 50, 300, 50)
            draw_button('Go back to menu', button_menu, BUTTON_COLOR, HOVER_COLOR, button_font, screen)
            pygame.display.flip()

            waiting_for_input = True
            while waiting_for_input:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        if event.button == 1:
                            if button_menu.collidepoint(event.pos):
                                return  # Exit the play_game function and go back to menu
                pygame.display.flip()
                time.sleep(0.1)

        if board.turn == chess.WHITE:
            uci = player1(board, get_move) if player1 == human_player else player1(board)
        else:
            uci = player2(board, get_move) if player2 == human_player else player2(board)
        
        move = chess.Move.from_uci(uci)

        # Capture pieces
        if board.is_capture(move):
            captured_piece = board.piece_at(move.to_square)
            if captured_piece:
                piece_type = captured_piece.symbol().upper()
                if board.turn == chess.WHITE:
                    captured_black.append(piece_type)
                else:
                    captured_white.append(piece_type)

        board.push_uci(uci)
        
        draw_board(board)
        draw_side_panel(white_time, black_time, captured_white, captured_black)
        pygame.display.flip()
        clock.tick(FPS)


# Menu function
def menu():
    click = False
    while True:
        screen.fill(WHITE)
        draw_text('Chess Game', font, BLACK, screen, SCREEN_WIDTH // 2, 100)
        
        button_multiplayer = pygame.Rect(SCREEN_WIDTH // 2 - 150, 200, 300, 50)
        button_ai = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 50)
        
        draw_button('Multiplayer', button_multiplayer, BUTTON_COLOR, HOVER_COLOR, button_font, screen)
        draw_button('Play with the Machine', button_ai, BUTTON_COLOR, HOVER_COLOR, button_font, screen)
        
        mx, my = pygame.mouse.get_pos()
        
        if button_multiplayer.collidepoint((mx, my)):
            if click:
                play_game(human_player, human_player)
                click = False  # Reset click after use

        if button_ai.collidepoint((mx, my)):
            if click:
                choose_side_menu()
                click = False  # Reset click after use
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        
        pygame.display.update()
        time.sleep(0.1)

def choose_side_menu():
    click = False
    while True:
        screen.fill(WHITE)
        draw_text('Choose Your Side', font, BLACK, screen, SCREEN_WIDTH // 2, 100)
        
        button_white = pygame.Rect(SCREEN_WIDTH // 2 - 150, 200, 300, 50)
        button_black = pygame.Rect(SCREEN_WIDTH // 2 - 150, 300, 300, 50)
        
        draw_button('Play as White', button_white, BUTTON_COLOR, HOVER_COLOR, button_font, screen)
        draw_button('Play as Black', button_black, BUTTON_COLOR, HOVER_COLOR, button_font, screen)
        
        mx, my = pygame.mouse.get_pos()
        
        if button_white.collidepoint((mx, my)):
            if click:
                play_game(human_player, player5)
                click = False  # Reset click after use

        if button_black.collidepoint((mx, my)):
            if click:
                play_game(player5, human_player)
                click = False  # Reset click after use
        
        click = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    click = True
        
        pygame.display.update()
        time.sleep(0.1)

# Main function
if __name__ == "__main__":
    menu()
