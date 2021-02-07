# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                      evaluation_settings.py
#
#                   - All evaluation related settings are found here
#                   - Base piece values, PST tables, single bonuses/punishments etc
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

import helper_functions as hf

#  --------------------------------------------------------------------------------
#                             Bonuses/Punishments
#  --------------------------------------------------------------------------------

# Extra bonuses/punishments. Not many of them implemented yet, none of them is optimized.

# BONUSES
passed_pawn = [0, 10, 30, 50, 75, 100, 150, 200]  # Give more bonus if pawn is further advanced
semi_open_file = 10
open_file = 10
mobility_factor = [0,  4,  5,  3,  5, 0,  # White pieces
                   0, -4, -5, -3, -5, 0]  # Black pieces
king_shield = 5
bishop_pair_bonus = 15
center_attack_bonus_factor = 1  # Factor to multiply with how many center squares are attacked by own pieces
king_attack_bonus_factor = 5  # Factor to multiply with how many squares around enemy king that are attacked by own pieces
knight_pawn_bonus = 2  # Knights better with lots of pawns
bishop_endgame_bonus = 10  # Bonus for bishops in endgame, per piece
rook_on_semi_open_file_bonus = 20  # Give rook a bonus for being on an open file without any own pawns, right now it is per rook
rook_on_open_file_bonus = 20  # Give rook a bonus for being on an open file without any pawns, right now it is per rook

# PUNISHMENTS
double_pawn = -10
isolated_pawn = -10
double_pawn_punishment = -40  # Give punishment if there are 2 pawns on the same column, maybe increase if late in game. Calibrate value
isolated_pawn_punishment = -40  # If the pawn has no allies on the columns next to it, calibrate value later
knight_endgame_punishment = -10  # Punishment for knights in endgame, per piece
blocking_d_e_pawn_punishment = -40  # Punishment for blocking unmoved pawns on d and e file
bishop_pawn_punishment = -2  # Bishops worse with lots of pawns
rook_pawn_punishment = -2  # Rooks worse with lots of pawns

# --------------------------------------------------------------------------------
#                       Board tables and helpers
# --------------------------------------------------------------------------------

manhattan_distance = [6, 5, 4, 3, 3, 4, 5, 6,
                      5, 4, 3, 2, 2, 3, 4, 5,
                      4, 3, 2, 1, 1, 2, 3, 4,
                      3, 2, 1, 0, 0, 1, 2, 3,
                      3, 2, 1, 0, 0, 1, 2, 3,
                      4, 3, 2, 1, 1, 2, 3, 4,
                      5, 4, 3, 2, 2, 3, 4, 5,
                      6, 5, 4, 3, 3, 4, 5, 6]

real_board_squares = [21, 22, 23, 24, 25, 26, 27, 28,
                      31, 32, 33, 34, 35, 36, 37, 38,
                      41, 42, 43, 44, 45, 46, 47, 48,
                      51, 52, 53, 54, 55, 56, 57, 58,
                      61, 62, 63, 64, 65, 66, 67, 68,
                      71, 72, 73, 74, 75, 76, 77, 78,
                      81, 82, 83, 84, 85, 86, 87, 88,
                      91, 92, 93, 94, 95, 96, 97, 98]

piece_to_number = {'wp': 0, 'wN': 1, 'wB': 2, 'wR': 3, 'wQ': 4, 'wK': 5,
                   'bp': 6, 'bN': 7, 'bB': 8, 'bR': 9, 'bQ': 10, 'bK': 11}

# --------------------------------------------------------------------------------
#                   Pre-calculated king attack square
# --------------------------------------------------------------------------------

king_attack_squares = {}
for square in real_board_squares:
    king_attack_squares[square] = []

for square in real_board_squares:
    for d in (-10, -1, 10, 1, -11, -9, 9, 11):
        attack_square = square + d
        if attack_square in real_board_squares:
            king_attack_squares[square].append(attack_square)

# --------------------------------------------------------------------------------
#                                Base piece values
# --------------------------------------------------------------------------------

# Piece base values
base_mid_game = {'K': 12000,
                 'Q': 1025,
                 'R': 477,
                 'B': 365,
                 'N': 337,
                 'p': 82}

base_end_game = {'K': 12000,
                 'Q': 936,
                 'R': 512,
                 'B': 297,
                 'N': 281,
                 'p': 94}

# --------------------------------------------------------------------------------
#                         Game phase variables
#  (https://www.youtube.com/watch?v=JYF6A0xvvtY&list=PLmN0neTso3Jxh8ZIylk74JpwfiWNI76Cs&index=85)
# --------------------------------------------------------------------------------


# Calculate the phase of the game
piece_phase_calc = {'K': 0,
                    'Q': base_mid_game['Q'],
                    'R': base_mid_game['R'],
                    'B': base_mid_game['B'],
                    'N': base_mid_game['N'],
                    'p': 0}

# Phase scores
opening_phase_score = 6192
endgame_phase_score = 518

# --------------------------------------------------------------------------------
#                         Piece square tables
# --------------------------------------------------------------------------------

# Piece tables
king_mid = [0, 0, 0, 0, 0, 0,  0,  0,  0, 0,
            0, 0, 0, 0, 0, 0,  0,  0,  0, 0,
            0, -65, 23, 16, -15, -56, -34, 2, 13, 0,
            0, 29, -1, -20, -7, -8, -4, -38, -29, 0,
            0, -9, 24, 2, -16, -20, 6, 22, -22, 0,
            0, -17, -20, -12, -27, -30, -25, -14, -36, 0,
            0, -49, -1, -27, -39, -46, -44, -33, -51, 0,
            0, -14, -14, -22, -46, -44, -30, -15, -27, 0,
            0, 1, 7, -8, -64, -43, -16, 9, 8, 0,
            0, -15, 36, 12, -54, 8, -28, 24, 14, 0,
            0, 0,  0,  0,  0,  0,  0,  0,  0, 0,
            0,  0, 0,  0,  0,  0,  0,  0,  0, 0]
queen_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, -28, 0, 29, 12, 59, 44, 43, 45, 0,
             0, -24, -39, -5, 1, -16, 57, 28, 54, 0,
             0, -13, -17, 7, 8, 29, 56, 47, 57, 0,
             0, -27, -27, -16, -16, -1, 17, -2, 1, 0,
             0, -9, -26, -9, -10, -2, -4, 3, -3, 0,
             0, -14, 2, -11, -2, -5, 2, 14, 5, 0,
             0, -35, -8, 11, 2, 8, 15, -3, 1, 0,
             0, -1, -18, -9, 10, -15, -25, -31, -50, 0,
             0, 0, 0, 0, 0,  0, 0, 0,  0, 0,
             0, 0, 0, 0, 0,  0, 0, 0, 0, 0]
rook_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 32, 42, 32, 51, 63, 9, 31, 43, 0,
            0, 27, 32, 58, 62, 80, 67, 26, 44, 0,
            0, -5, 19, 26, 36, 17, 45, 61, 16, 0,
            0, -24, -11, 7, 26, 24, 35, -8, -20, 0,
            0, -36, -26, -12, -1, 9, -7, 6, -23, 0,
            0, -45, -25, -16, -17, 3, 0, -5, -33, 0,
            0, -44, -16, -20, -9, -1, 11, -6, -71, 0,
            0, -19, -13, 1, 17, 16, 7, -37, -26, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bishop_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, -29, 4, -82, -37, -25, -42, 7, -8, 0,
              0, -26, 16, -18, -13, 30, 59, 18, -47, 0,
              0, -16, 37, 43, 40, 35, 50, 37, -2, 0,
              0, -4, 5, 19, 50, 37, 37, 7, -2, 0,
              0, -6, 13, 13, 26, 34, 12, 10, 4, 0,
              0, 0, 15, 15, 15, 14, 27, 18, 10, 0,
              0, 4, 15, 16, 0, 7, 21, 33, 1, 0,
              0, -33, -3, -14, -21, -13, -12, -39, -21, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
knight_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, -167, -89, -34, -49, 61, -97, -15, -107, 0,
              0, -73, -41, 72, 36, 23, 62, 7, -17, 0,
              0, -47, 60, 37, 65, 84, 129, 73, 44, 0,
              0, -9, 17, 19, 53, 37, 69, 18, 22, 0,
              0, -13, 4, 16, 13, 28, 19, 21, -8, 0,
              0, -23, -9, 12, 10, 19, 17, 25, -16, 0,
              0, -29, -53, -12, -3, -1, 18, -14, -19, 0,
              0, -105, -21, -58, -33, -17, -28, -19, -23, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
pawn_mid = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 98, 134, 61, 95, 68, 126, 34, -11, 0,
            0, -6, 7, 26, 31, 65, 56, 25, -20, 0,
            0, -14, 13, 6, 21, 23, 12, 17, -23, 0,
            0, -27, -2, -5, 12, 17, 6, 10, -25, 0,
            0, -26, -4, -4, -10, 3, 3, 33, -12, 0,
            0, -35, -1, -20, -23, -15, 24, 38, -22, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

king_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, -74, -35, -18, -18, -11, 15, 4, -17, 0,
            0, -12, 17, 14, 17, 17, 38, 23, 11, 0,
            0, 10, 17, 23, 15, 20, 45, 44, 13, 0,
            0, -8, 22, 24, 27, 26, 33, 26, 3, 0,
            0, -18, -4, 21, 24, 27, 23, 9, -11, 0,
            0, -19, -3, 11, 21, 23, 16, 7, -9, 0,
            0, -27, -11, 4, 13, 14, 4, -5, -17, 0,
            0, -53, -34, -21, -11, -28, -14, -24, -43, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
queen_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, -9, 22, 22, 27, 27, 19, 10, 20, 0,
             0, -17, 20, 32, 41, 58, 25, 30, 0, 0,
             0, -20, 6, 9, 49, 47, 35, 19, 9, 0,
             0, 3, 22, 24, 45, 57, 40, 57, 36, 0,
             0, -18, 28, 19, 47, 31, 34, 39, 23, 0,
             0, -16, -27, 15, 6, 9, 17, 10, 5, 0,
             0, -22, -23, -30, -16, -16, -23, -36, -32, 0,
             0, -33, -28, -22, -43, -5, -32, -20, -41, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
rook_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 13, 10, 18, 15, 12, 12, 8, 5, 0,
            0, 11, 13, 13, 11, -3, 3, 8, 3, 0,
            0, 7, 7, 7, 5, 4, -3, -5, -3, 0,
            0, 4, 3, 13, 1, 2, 1, -1, 2, 0,
            0, 3, 5, 8, 4, -5, -6, -8, -11, 0,
            0, -4, 0, -5, -1, -7, -12, -8, -16, 0,
            0, -6, -6, 0, 2, -9, -9, -11, -3, 0,
            0, -9, 2, 3, -1, -5, -13, 4, -20, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
bishop_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, -14, -21, -11, -8, -7, -9, -17, -24, 0,
              0, -8, -4, 7, -12, -3, -13, -4, -14, 0,
              0, 2, -8, 0, -1, -2, 6, 0, 4, 0,
              0, -3, 9, 12, 9, 14, 10, 3, 2, 0,
              0, -6, 3, 13, 19, 7, 10, -3, -9, 0,
              0, -12, -3, 8, 10, 13, 3, -7, -15, 0,
              0, -14, -18, -7, -1, 4, -9, -15, -27, 0,
              0, -23, -9, -23, -5, -9, -16, -5, -17, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
knight_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, -58, -38, -13, -28, -31, -27, -63, -99, 0,
              0, -25, -8, -25, -2, -9, -25, -24, -52, 0,
              0, -24, -20, 10, 9, -1, -9, -19, -41, 0,
              0, -17, 3, 22, 22, 22, 11, 8, -18, 0,
              0, -18, -6, 16, 25, 16, 17, 4, -18, 0,
              0, -23, -3, -1, 15, 10, -3, -20, -22, 0,
              0, -42, -20, -10, -5, -2, -20, -23, -44, 0,
              0, -29, -51, -23, -15, -22, -18, -50, -64, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
              0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
pawn_end = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 178, 173, 158, 134, 147, 132, 165, 187, 0,
            0, 94, 100, 85, 67, 56, 53, 82, 84, 0,
            0, 32, 24, 13, 5, -2, 4, 17, 17, 0,
            0, 13, 9, -3, -7, -7, -8, 3, -1, 0,
            0, 4, 7, -6, 1, 0, -5, -1, -8, 0,
            0, 13, 8, 8, 10, 13, 0, 2, -7, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# Negate values for black side.
# Rotate boards for black side to be able to send in the same square no matter piece color.
king_mid_pos = [elem + base_mid_game['K'] for elem in king_mid]
queen_mid_pos = [elem + base_mid_game['Q'] for elem in queen_mid]
rook_mid_pos = [elem + base_mid_game['R'] for elem in rook_mid]
bishop_mid_pos = [elem + base_mid_game['B'] for elem in bishop_mid]
knight_mid_pos = [elem + base_mid_game['N'] for elem in knight_mid]
pawn_mid_pos = [elem + base_mid_game['p'] for elem in pawn_mid]

king_mid_neg = [-elem for elem in hf.rotate_board(king_mid)]
queen_mid_neg = [-elem for elem in hf.rotate_board(queen_mid)]
rook_mid_neg = [-elem for elem in hf.rotate_board(rook_mid)]
bishop_mid_neg = [-elem for elem in hf.rotate_board(bishop_mid)]
knight_mid_neg = [-elem for elem in hf.rotate_board(knight_mid)]
pawn_mid_neg = [-elem for elem in hf.rotate_board(pawn_mid)]

king_end_pos = [elem + base_end_game['K'] for elem in king_end]
queen_end_pos = [elem + base_end_game['Q'] for elem in queen_end]
rook_end_pos = [elem + base_end_game['R'] for elem in rook_end]
bishop_end_pos = [elem + base_end_game['B'] for elem in bishop_end]
knight_end_pos = [elem + base_end_game['N'] for elem in knight_end]
pawn_end_pos = [elem + base_end_game['p'] for elem in pawn_end]

king_end_neg = [-elem for elem in king_end]
queen_end_neg = [-elem for elem in queen_end]
rook_end_neg = [-elem for elem in rook_end]
bishop_end_neg = [-elem for elem in bishop_end]
knight_end_neg = [-elem for elem in knight_end]
pawn_end_neg = [-elem for elem in pawn_end]

# Add to a complete look-up table
pst_mid = [pawn_mid_pos, knight_mid_pos, bishop_mid_pos, rook_mid_pos, queen_mid_pos, king_mid_pos,
           pawn_mid_pos, knight_mid_pos, bishop_mid_pos, rook_mid_pos, queen_mid_pos, king_mid_pos]

pst_end = [pawn_end_pos, knight_end_pos, bishop_end_pos, rook_end_pos, queen_end_pos, king_end_pos,
           pawn_end_pos, knight_end_pos, bishop_end_pos, rook_end_pos, queen_end_pos, king_end_pos]

pst_mid_neg = [pawn_mid_pos, knight_mid_pos, bishop_mid_pos, rook_mid_pos, queen_mid_pos, king_mid_pos,
               pawn_mid_neg, knight_mid_neg, bishop_mid_neg, rook_mid_neg, queen_mid_neg, king_mid_neg]

pst_end_neg = [pawn_end_pos, knight_end_pos, bishop_end_pos, rook_end_pos, queen_end_pos, king_end_pos,
               pawn_end_neg, knight_end_neg, bishop_end_neg, rook_end_neg, queen_end_neg, king_end_neg]


# Just the piece square tables without base values
king_mid_sq = [elem for elem in king_mid]
queen_mid_sq = [elem for elem in queen_mid]
rook_mid_sq = [elem for elem in rook_mid]
bishop_mid_sq = [elem for elem in bishop_mid]
knight_mid_sq = [elem for elem in knight_mid]
pawn_mid_sq = [elem for elem in pawn_mid]

king_end_sq = [elem for elem in king_end]
queen_end_sq = [elem for elem in queen_end]
rook_end_sq = [elem for elem in rook_end]
bishop_end_sq = [elem for elem in bishop_end]
knight_end_sq = [elem for elem in knight_end]
pawn_end_sq = [elem for elem in pawn_end]

pst_mid_squares = [pawn_mid_sq, knight_mid_sq, bishop_mid_sq, rook_mid_sq, queen_mid_sq, king_mid_sq,
                   pawn_mid_sq, knight_mid_sq, bishop_mid_sq, rook_mid_sq, queen_mid_sq, king_mid_sq]

pst_end_square = [pawn_end_sq, knight_end_sq, bishop_end_sq, rook_end_sq, queen_end_sq, king_end_sq,
                  pawn_end_sq, knight_end_sq, bishop_end_sq, rook_end_sq, queen_end_sq, king_end_sq]

