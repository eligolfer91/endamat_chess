# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                        constants.py
#
#                   - All constants used in the game are found here
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

#  --------------------------------------------------------------------------------
#                                  Castling
#  --------------------------------------------------------------------------------

# Bin   Dec       Right
# 0001   1    White kingside
# 0010   2    White queenside
# 0100   4    Black kingside
# 1000   8    Black queenside
castling_numbers = {'wk': 1, 'wq': 2, 'bk': 4, 'bq': 8}

# Used to calculate castling rights from gamestate
cr_to_fen = {15: ' KQkq', 14: ' Qkq', 13: ' Kkq', 12: ' kq', 11: ' KQq', 10: ' Qq', 9: ' Kq', 8: ' q',
             7: ' KQk', 6: ' Qk', 5: ' Kk', 4: ' k', 3: ' KQ', 2: ' Q', 1: ' K', 0: ' -'}

# If king moves to a square, the rook should move to according square (wk, wq, bk, bq)
# and also be removed from original square.
rook_castling = {97: (96, 98), 93: (94, 91), 27: (26, 28), 23: (24, 21)}

# Update castling rights
#
#                               castling     move          in      in
#                                 right     update       binary  decimal
# No piece moved                  1111   &   1111     =   1111     15
#
# White king moved                1111   &   1100     =   1100     12
# White kingside rook             1111   &   1110     =   1110     14
# White queenside rook            1111   &   1101     =   1101     13
#
# Black king moved                1111   &   0011     =   0011     3
# Black kingside rook             1111   &   1011     =   1011     11
# Black queenside rook            1111   &   0111     =   0111     7

update_castling_rights = [0,   0,  0,  0,  0,  0,  0,  0,  0, 0,
                          0,   0,  0,  0,  0,  0,  0,  0,  0, 0,
                          0,   7, 15, 15, 15,  3, 15, 15, 11, 0,
                          0,  15, 15, 15, 15, 15, 15, 15, 15, 0,
                          0,  15, 15, 15, 15, 15, 15, 15, 15, 0,
                          0,  15, 15, 15, 15, 15, 15, 15, 15, 0,
                          0,  15, 15, 15, 15, 15, 15, 15, 15, 0,
                          0,  15, 15, 15, 15, 15, 15, 15, 15, 0,
                          0,  15, 15, 15, 15, 15, 15, 15, 15, 0,
                          0,  13, 15, 15, 15, 12, 15, 15, 14, 0,
                          0,   0,  0,  0,  0,  0,  0,  0,  0, 0,
                          0,   0,  0,  0,  0,  0,  0,  0,  0, 0]


#  --------------------------------------------------------------------------------
#                                Board parameters
#  --------------------------------------------------------------------------------

real_board_squares = [21, 22, 23, 24, 25, 26, 27, 28,
                      31, 32, 33, 34, 35, 36, 37, 38,
                      41, 42, 43, 44, 45, 46, 47, 48,
                      51, 52, 53, 54, 55, 56, 57, 58,
                      61, 62, 63, 64, 65, 66, 67, 68,
                      71, 72, 73, 74, 75, 76, 77, 78,
                      81, 82, 83, 84, 85, 86, 87, 88,
                      91, 92, 93, 94, 95, 96, 97, 98]

# Flip from white to black perspective
black_side = [i for i in reversed(range(120))]
for row in range(12):
    black_side[row*10:10+row*10] = black_side[row*10:10+row*10][::-1]

directions = [-10, -1, 10, 1, -11, -9, 9, 11]  # Up, left, down, right, up/left, up/right, down/left, down/right
knight_moves = [-21, -19, -12, -8, 8, 12, 19, 21]  # Up-up-left, up-up-right ......

# Pawns start and end (promotion) rows
start_row_white = [x for x in range(81, 89)]
start_row_black = [x for x in range(31, 39)]
end_row_white = [x for x in range(21, 29)]
end_row_black = [x for x in range(91, 99)]

# Numbers and letters
numbers = ['1', '2', '3', '4', '5', '6', '7', '8']
letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

# Get square number from a given board, or the board from a given square number
board_to_square = {}
square_to_board = {}
for square in real_board_squares:
    file, rank = square % 10 - 1, square // 10 - 2
    board_to_square[f'{letters[file]}{numbers[::-1][rank]}'] = square
    square_to_board[square] = f'{letters[file]}{numbers[::-1][rank]}'

#  --------------------------------------------------------------------------------
#                             Negamax related
#  --------------------------------------------------------------------------------

zobrist_pieces = {'wp': 0, 'wN': 1, 'wB': 2, 'wR': 3, 'wQ': 4, 'wK': 5,
                  'bp': 6, 'bN': 7, 'bB': 8, 'bR': 9, 'bQ': 10, 'bK': 11,
                  '--': 12}

mvv_lva_values = {'wp': 1, 'wN': 3, 'wB': 3, 'wR': 4, 'wQ': 5, 'wK': 6,
                  'bp': 1, 'bN': 3, 'bB': 3, 'bR': 4, 'bQ': 5, 'bK': 6}

mvv_storing = 10  # How many of the MVV_LVV top candidates to use
full_depth_moves = 4  # How many moves we need to make before starting with LMR
reduction_limit = 2  # How much the depth needs to be to start searching for LMR
R = 2  # Null move reduction of depth
aspiration_window = 50  # Aspiration window for PVS search

# Bonus values depending on type of sorted move
pv_score = 20000
mvv_lva = 10000
first_killer_move = 9000
second_killer_move = 8000
