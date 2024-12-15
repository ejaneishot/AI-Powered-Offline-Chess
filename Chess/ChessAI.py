import random

piece_scores = {
    'p': 100,
    'N': 320,
    'B': 330,
    'R': 500,
    'Q': 900,
    'K': 20000
}

# Piece position tables - higher values for better positions
pawn_table = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [ 5,  5, 10, 25, 25, 10,  5,  5],
    [ 0,  0,  0, 20, 20,  0,  0,  0],
    [ 5, -5,-10,  0,  0,-10, -5,  5],
    [ 5, 10, 10,-20,-20, 10, 10,  5],
    [ 0,  0,  0,  0,  0,  0,  0,  0]
]

knight_table = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

bishop_table = [
    [-20,-10,-10,-10,-10,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5, 10, 10,  5,  0,-10],
    [-10,  5,  5, 10, 10,  5,  5,-10],
    [-10,  0, 10, 10, 10, 10,  0,-10],
    [-10, 10, 10, 10, 10, 10, 10,-10],
    [-10,  5,  0,  0,  0,  0,  5,-10],
    [-20,-10,-10,-10,-10,-10,-10,-20]
]

rook_table = [
    [ 0,  0,  0,  0,  0,  0,  0,  0],
    [ 5, 10, 10, 10, 10, 10, 10,  5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [-5,  0,  0,  0,  0,  0,  0, -5],
    [ 0,  0,  0,  5,  5,  0,  0,  0]
]

queen_table = [
    [-20,-10,-10, -5, -5,-10,-10,-20],
    [-10,  0,  0,  0,  0,  0,  0,-10],
    [-10,  0,  5,  5,  5,  5,  0,-10],
    [ -5,  0,  5,  5,  5,  5,  0, -5],
    [  0,  0,  5,  5,  5,  5,  0, -5],
    [-10,  5,  5,  5,  5,  5,  0,-10],
    [-10,  0,  5,  0,  0,  0,  0,-10],
    [-20,-10,-10, -5, -5,-10,-10,-20]
]

king_table = [
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-30,-40,-40,-50,-50,-40,-40,-30],
    [-20,-30,-30,-40,-40,-30,-30,-20],
    [-10,-20,-20,-20,-20,-20,-20,-10],
    [ 20, 20,  0,  0,  0,  0, 20, 20],
    [ 20, 30, 10,  0,  0, 10, 30, 20]
]

piece_position_scores = {
    'p': pawn_table,
    'N': knight_table,
    'B': bishop_table,
    'R': rook_table,
    'Q': queen_table,
    'K': king_table
}

def get_position_score(piece, row, col, is_white):
    if piece == "- -":
        return 0
    
    piece_type = piece[1]
    if piece_type not in piece_position_scores:
        return 0
    
    position_table = piece_position_scores[piece_type]
    
    # For black pieces, we flip the table
    if not is_white:
        row = 7 - row
    
    return position_table[row][col]

def evaluate_board(board):
    """Evaluates the board position. Positive score favors white, negative favors black."""
    score = 0
    
    # Material and position score
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece != "- -":
                # Material score
                piece_value = piece_scores.get(piece[1], 0)
                if piece[0] == 'w':
                    score += piece_value
                    score += get_position_score(piece, row, col, True)
                else:
                    score -= piece_value
                    score -= get_position_score(piece, row, col, False)
    
    return score

def minimax(gs, depth, alpha, beta, is_maximizing):
    """
    Minimax algorithm with alpha-beta pruning for chess AI
    gs: GameState object
    depth: How many moves to look ahead
    alpha, beta: Parameters for alpha-beta pruning
    is_maximizing: True if it's white's turn, False if black's turn
    """
    if depth == 0:
        return evaluate_board(gs.board)
    
    valid_moves = gs.getvalidmoves()
    
    if is_maximizing:
        max_eval = float('-inf')
        for move in valid_moves:
            gs.makemove(move)
            eval = minimax(gs, depth - 1, alpha, beta, False)
            gs.undomove()
            max_eval = max(max_eval, eval)
            alpha = max(alpha, eval)
            if beta <= alpha:
                break
        return max_eval
    else:
        min_eval = float('inf')
        for move in valid_moves:
            gs.makemove(move)
            eval = minimax(gs, depth - 1, alpha, beta, True)
            gs.undomove()
            min_eval = min(min_eval, eval)
            beta = min(beta, eval)
            if beta <= alpha:
                break
        return min_eval

def find_best_move(gs, depth=3):
    """Finds the best move for black using minimax with alpha-beta pruning"""
    valid_moves = gs.getvalidmoves()
    best_move = None
    min_eval = float('inf')
    alpha = float('-inf')
    beta = float('inf')
    
    # Randomize move order for more varied gameplay
    valid_moves = list(valid_moves)
    random.shuffle(valid_moves)
    
    for move in valid_moves:
        gs.makemove(move)
        eval = minimax(gs, depth - 1, alpha, beta, True)
        gs.undomove()
        
        if eval < min_eval:
            min_eval = eval
            best_move = move
        beta = min(beta, eval)
    
    return best_move if best_move else random.choice(valid_moves)  # Fallback to random move if no good move found
