# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                           gamestate.py
#
#                   - Initialize the gamestate from a given FEN
#                   - Make and unmake move (normal moves, captures, nullmoves)
#                   - Generate valid moves (all, captures, check evasions)
#                   - Helper functions (check for pins and checks)
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

import helper_functions as hf
import settings as s
import fen_handling as fh
import evaluation_settings as es

import numpy as np


class GameState:

    def __init__(self, start_fen):

        # Init the board and relevant variables from an input fen string
        self.start_fen = start_fen
        self.board, self.castling_rights, self.enpassant_square, self.is_white_turn, self.halfmove_counter, self.move_counter = fh.run_fen_to_board(self.start_fen)

        # Init number of pieces on the board
        self.piece_dict = [{'p': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0}, {'p': 0, 'N': 0, 'B': 0, 'R': 0, 'Q': 0, 'K': 0}]  # W, B
        self.init_piece_dict()

        # Init piece values (base and square dependent)
        self.piece_values = [0, 0, 0, 0]  # White mid game, black mid game, white end game black end game
        self.init_piece_values()

        # Init king positions and distance between each other (used in evaluation)
        self.king_location, self.kings_distance = [0, 0], 0
        self.init_king_positions()
        self.update_king_dist()

        # Init game phase scores
        self.game_phase_score = self.init_game_phase()
        self.game_phase = 0  # 0 = opening, 1 = middle game, 2 = end game

        # Get possible moves for a certain piece type
        self.move_functions = {'p': self.get_pawn_moves,
                               'N': self.get_knight_moves,
                               'B': self.get_bishop_moves,
                               'R': self.get_rook_moves,
                               'Q': self.get_queen_moves,
                               'K': self.get_king_moves}
        self.move_capture_functions = {'p': self.get_pawn_captures,
                                       'N': self.get_knight_captures,
                                       'B': self.get_bishop_captures,
                                       'R': self.get_rook_captures,
                                       'Q': self.get_queen_captures,
                                       'K': self.get_king_captures}
        self.move_check_functions = {'p': self.get_pawn_evasions,
                                     'N': self.get_knight_evasions,
                                     'B': self.get_bishop_evasions,
                                     'R': self.get_rook_evasions,
                                     'Q': self.get_queen_evasions,
                                     'K': self.get_king_evasions}
        self.move_check_capture_functions = {'p': self.get_pawn_capture_evasions,
                                             'N': self.get_knight_capture_evasions,
                                             'B': self.get_bishop_capture_evasions,
                                             'R': self.get_rook_capture_evasions,
                                             'Q': self.get_queen_capture_evasions,
                                             'K': self.get_king_capture_evasions}

        # Check, stalemate and checkmate variables
        self.pins, self.checks = [], []
        self.is_in_check = False

        # Move related variables
        self.piece_moved = self.piece_captured = '--'

        self.move_dir = -10
        self.colors = 'wb'
        self.start_row = s.start_row_white
        self.end_row = s.end_row_white

        # Random state number for the game to always get the same zobrist key
        self.random_state = 1804289383

        # Zobrist keys
        self.zobrist_pieces = np.zeros(shape=(13, 120), dtype=np.uint64)
        self.zobrist_enpassant = np.zeros(shape=120, dtype=np.uint64)
        self.zobrist_castling = np.zeros(shape=16, dtype=np.uint64)
        self.zobrist_side = np.uint64(0)
        self.init_zobrist_key()
        self.zobrist_key = self.generate_zobrist_key()

        # Keep track of 3-fold repetition
        self.repetition_table = [(self.zobrist_key, '', [0, 0, 0, 0, 0])]

        # Init the move log. [move(from, to, piece, piece_increase, piece_moved), piece moved, piece_captured, castling rights, enpassant square, zobrist key, piece_values]
        self.move_log = [[[0, 0, 0, 0, 0], '--', '--', self.castling_rights, self.enpassant_square, self.zobrist_key, self.piece_values[:], self.halfmove_counter]]

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                      Make and unmake moves
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

# -------------------------  Normal moves -----------------------------------------------------------------

    def make_move(self, move):

        # Increase move counter
        self.move_counter += 0.5

        # Increase half move counter
        self.halfmove_counter += 1

        start_square, end_square, move_type = move[0], move[1], move[2]

        # Square dependent on white or black
        from_square, to_square = (start_square, end_square) if self.is_white_turn else (s.black_side[start_square], s.black_side[end_square])

        if self.enpassant_square:
            self.zobrist_key ^= self.zobrist_enpassant[self.enpassant_square]
        self.enpassant_square = None

        # Update piece_moved and piece_captured
        self.piece_moved = move[3]
        self.piece_captured = self.board[end_square]

        # Update board
        self.board[start_square] = '--'
        self.board[end_square] = self.piece_moved

        # Update Zobrist key
        self.zobrist_key ^= self.zobrist_pieces[s.zobrist_pieces[self.piece_moved]][start_square]  # Remove piece from start square
        self.zobrist_key ^= self.zobrist_pieces[s.zobrist_pieces[self.piece_moved]][end_square]  # Place the moved piece on its end square

        # Update the king position and kings distance
        if self.piece_moved[1] == 'K':
            self.king_location[not self.is_white_turn] = end_square
            self.update_king_dist()

            if move_type == 'castling':
                rook = 'wR' if self.is_white_turn else 'bR'

                self.board[s.rook_castling[end_square][1]] = '--'  # Remove R
                self.board[s.rook_castling[end_square][0]] = f'{self.piece_moved[0]}R'  # Place R

                self.zobrist_key ^= self.zobrist_pieces[es.piece_to_number[rook]][s.rook_castling[end_square][1]]
                self.zobrist_key ^= self.zobrist_pieces[es.piece_to_number[rook]][s.rook_castling[end_square][0]]

                self.piece_values[(not self.is_white_turn)] += -es.pst_mid_squares[es.piece_to_number[rook]][s.rook_castling[to_square][1]] + es.pst_mid_squares[es.piece_to_number[rook]][
                    s.rook_castling[to_square][0]]
                self.piece_values[(not self.is_white_turn) + 2] += -es.pst_end_square[es.piece_to_number[rook]][s.rook_castling[to_square][1]] + es.pst_end_square[es.piece_to_number[rook]][
                    s.rook_castling[to_square][0]]

        # Pawn promotion
        if move_type in 'pQpRpBpN':

            # Reset half move counter
            self.halfmove_counter = 0

            self.board[end_square] = f'{self.piece_moved[0]}{move_type[1]}'

            self.piece_dict[not self.is_white_turn]['p'] -= 1
            self.piece_dict[not self.is_white_turn][f'{move_type[1]}'] += 1

            self.zobrist_key ^= self.zobrist_pieces[s.zobrist_pieces[self.piece_moved]][end_square]  # Remove the pawn from end_square again since it now changed
            self.zobrist_key ^= self.zobrist_pieces[s.zobrist_pieces[f'{self.piece_moved[0]}{move_type[1]}']][end_square]  # Place the promoted piece there instead

            # Update piece value change
            self.piece_values[(not self.is_white_turn)] += -es.pst_mid[es.piece_to_number[self.piece_moved]][from_square] + es.pst_mid[es.piece_to_number[f'{self.piece_moved[0]}{move_type[-1]}']][to_square]
            self.piece_values[(not self.is_white_turn) + 2] += -es.pst_end[es.piece_to_number[self.piece_moved]][from_square] + es.pst_end[es.piece_to_number[f'{self.piece_moved[0]}{move_type[-1]}']][to_square]

        else:
            self.piece_values[not self.is_white_turn] += -es.pst_mid_squares[es.piece_to_number[self.piece_moved]][from_square] + es.pst_mid_squares[es.piece_to_number[self.piece_moved]][to_square]
            self.piece_values[(not self.is_white_turn) + 2] += -es.pst_end_square[es.piece_to_number[self.piece_moved]][from_square] + es.pst_end_square[es.piece_to_number[self.piece_moved]][to_square]

        # Capture moves
        if self.piece_captured != '--' or move_type == 'ep':

            # Reset half move counter
            self.halfmove_counter = 0

            capture_square = 0

            # Enpassant
            if move_type == 'ep':

                # Remove captured pawn from board and Zobrist key
                d, color = (10, 'b') if self.is_white_turn else (-10, 'w')
                self.board[end_square + d] = '--'
                self.piece_captured = f'{color}p'
                self.zobrist_key ^= self.zobrist_pieces[s.zobrist_pieces[f'{color}p']][end_square + d]  # Remove pawn from its start square

                # Captured piece square is now capture square - d since piece is not on the actual capture square
                capture_square = -10

            # Update piece dict and game phase
            self.piece_dict[self.is_white_turn][self.piece_captured[1]] -= 1
            self.game_phase_score -= es.piece_phase_calc[self.piece_captured[1]]

            capture_square += end_square if not self.is_white_turn else s.black_side[end_square]

            self.piece_values[self.is_white_turn] -= es.pst_mid[es.piece_to_number[self.piece_captured]][capture_square]
            self.piece_values[self.is_white_turn + 2] -= es.pst_end[es.piece_to_number[self.piece_captured]][capture_square]

            if move_type != 'ep':
                self.zobrist_key ^= self.zobrist_pieces[s.zobrist_pieces[self.piece_captured]][end_square]  # Remove the piece that was on the end square

        # Two square pawn move, update enpassant possible square
        elif move_type == 'ts':

            # Reset half move counter
            self.halfmove_counter = 0

            self.enpassant_square = (start_square + end_square) // 2  # Enpassant square is the mean of start_square and end_square for the pawn moving 2 squares
            self.zobrist_key ^= self.zobrist_enpassant[self.enpassant_square]

        # Update castling rights if there are any left
        # Also update Zobrist castling before and after
        if self.castling_rights:
            self.zobrist_key ^= self.zobrist_castling[self.castling_rights]
            self.castling_rights &= s.update_castling_rights[start_square]
            self.castling_rights &= s.update_castling_rights[end_square]
            self.zobrist_key ^= self.zobrist_castling[self.castling_rights]

        # Switch player turn after the move is made
        self.is_white_turn = not self.is_white_turn
        self.zobrist_key ^= self.zobrist_side

        # Generate new Zobrist key
        #self.zobrist_key = self.generate_zobrist_key()

        # Store position to be able to detect 3 fold repetition
        self.repetition_table.append((self.zobrist_key, self.piece_moved, self.piece_captured))

        # Update move log
        self.move_log.append([move, self.piece_moved, self.piece_captured, self.castling_rights,
                              self.enpassant_square, self.zobrist_key, self.piece_values[:], self.halfmove_counter])

        # Test
        '''test_key = self.generate_zobrist_key()
        if self.zobrist_key != test_key:
            print(f'\n Orig key: {self.zobrist_key} \n Test key: {test_key}')
        '''

    def unmake_move(self):

        # Decrease move counter
        self.move_counter -= 0.5

        # Switch player turn back
        self.is_white_turn = not self.is_white_turn

        # Info about latest move
        latest_move = self.move_log.pop()
        start_square, end_square = latest_move[0][0], latest_move[0][1]
        move_type = latest_move[0][2]
        piece_moved, piece_captured = latest_move[0][3], latest_move[2]

        # Update board
        self.board[start_square] = piece_moved
        self.board[end_square] = piece_captured

        # Captures
        if piece_captured != '--':

            # Update piece dict and game phase score
            self.piece_dict[self.is_white_turn][piece_captured[1]] += 1
            self.game_phase_score += es.piece_phase_calc[piece_captured[1]]

        # Update the king position
        if piece_moved[1] == 'K':
            self.king_location[not self.is_white_turn] = start_square
            self.update_king_dist()

        # Update non normal moves
        if move_type != 'no':
            if move_type in 'pQpRpBpN':
                self.piece_dict[not self.is_white_turn]['p'] += 1
                self.piece_dict[not self.is_white_turn][f'{move_type[1]}'] -= 1

            elif move_type == 'castling':
                self.board[s.rook_castling[end_square][0]] = '--'  # Remove R
                self.board[s.rook_castling[end_square][1]] = f'{self.piece_moved[0]}R'  # Place R

            elif move_type == 'ep':
                self.board[start_square] = piece_moved
                self.board[end_square] = '--'

                d, color = (10, 'b') if self.is_white_turn else (-10, 'w')
                self.board[end_square + d] = f'{color}p'

        # Update things from the latest move [move, piece moved, piece_captured, castling rights, enpassant square, enpassant made, zobrist key, piece_values]
        self.piece_moved, self.piece_captured = self.move_log[-1][0][3], self.move_log[-1][2]
        self.castling_rights = self.move_log[-1][3]
        self.enpassant_square = self.move_log[-1][4]
        self.zobrist_key = self.move_log[-1][5]
        self.piece_values = self.move_log[-1][6][:]
        self.halfmove_counter = self.move_log[-1][7]

        # Clear position from repetition table
        self.repetition_table.pop()

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                              Initialize variables at start up
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    def init_piece_values(self):
        for square in self.board:
            color, piece = self.board[square][0], self.board[square]
            if color == 'w':
                self.piece_values[0] += es.pst_mid[es.piece_to_number[piece]][square]
                self.piece_values[2] += es.pst_end[es.piece_to_number[piece]][square]
            elif color == 'b':
                self.piece_values[1] += es.pst_mid[es.piece_to_number[piece]][s.black_side[square]]
                self.piece_values[3] += es.pst_end[es.piece_to_number[piece]][s.black_side[square]]

    def init_piece_dict(self):
        for square in self.board:
            piece_type, color = self.board[square][1], self.board[square][0]
            if piece_type in 'pNBRQK':
                if color == 'w':
                    self.piece_dict[0][piece_type] += 1
                elif color == 'b':
                    self.piece_dict[1][piece_type] += 1

    def init_king_positions(self):
        for square in s.real_board_squares:
            piece_type, color = self.board[square][1], self.board[square][0]
            if piece_type == 'K':
                if color == 'w':
                    self.king_location[0] = square
                else:
                    self.king_location[1] = square

    def init_game_phase(self):
        white_score = black_score = 0

        # White pieces
        for piece in self.piece_dict[0]:
            white_score += self.piece_dict[0][piece] * es.piece_phase_calc[piece]

        # Black pieces
        for piece in self.piece_dict[1]:
            black_score += self.piece_dict[1][piece] * es.piece_phase_calc[piece]

        return white_score + black_score

    def update_king_dist(self):
        horizontal_distance = abs(self.king_location[0] % 10 - self.king_location[1] % 10)
        vertical_distance = abs(self.king_location[0] // 10 - self.king_location[1] // 10)
        self.kings_distance = horizontal_distance + vertical_distance

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                    Initialize Zobrist key
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    # Init Zobrist key
    def init_zobrist_key(self):

        # Loop over pieces and squares and dd random piece key to each position in zobrist piece array
        for piece in s.zobrist_pieces:
            for square in s.real_board_squares:
                self.zobrist_pieces[s.zobrist_pieces[piece]][square] = self.get_random_64bit_number()

        # Loop over board squares and get random enpassant squares
        for square in s.real_board_squares:
            self.zobrist_enpassant[square] = self.get_random_64bit_number()

        # Loop over castling keys
        for index in range(16):
            self.zobrist_castling[index] = self.get_random_64bit_number()

        # Initialize random side key
        self.zobrist_side = np.uint64(self.get_random_64bit_number())

    def generate_zobrist_key(self):

        # Init a key variable
        key = np.uint64(0)

        # Loop over pieces and squares and add the piece and square dependent value to the zobrist key
        for square in s.real_board_squares:
            piece = self.board[square]
            if piece != '--':
                key ^= self.zobrist_pieces[s.zobrist_pieces[piece]][square]

        # Enpassant square if enpassant square is on board
        if self.enpassant_square:
            key ^= self.zobrist_enpassant[self.enpassant_square]

        # Castling rights
        key ^= self.zobrist_castling[self.castling_rights]

        # Side to move if black is to move
        if not self.is_white_turn:
            key ^= self.zobrist_side

        return key

    def get_random_32bit_number(self):

        number = self.random_state

        number ^= number << 13
        number ^= number >> 17
        number ^= number << 5

        self.random_state = number

        return number

    def get_random_64bit_number(self):

        num_1 = self.get_random_32bit_number() & 0xFFFF
        num_2 = self.get_random_32bit_number() & 0xFFFF
        num_3 = self.get_random_32bit_number() & 0xFFFF
        num_4 = self.get_random_32bit_number() & 0xFFFF

        return num_1 | (num_2 << 16) | (num_3 << 32) | (num_4 << 48)

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                  Move generating functions
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

# ---------------------------------------------------------------------------------------------------------
#                              Normal moves: Get all valid moves
# ---------------------------------------------------------------------------------------------------------

    # Get all moves considering checks and pins
    def get_valid_moves(self):

        king_pos = self.king_location[not self.is_white_turn]

        # Find if is in check and all the possible pinned pieces
        self.is_in_check, self.pins, self.checks = self.check_for_pins_and_checks(king_pos)

        if self.is_in_check:
            if len(self.checks) == 1:  # Single check

                # Get the squares in between checker and king. If it is knight you can only take the knight, else go in between or capture the piece.
                check = self.checks[0]
                checking_piece_pos = check[0]

                valid_squares = []
                if self.board[checking_piece_pos][1] == 'N':
                    valid_squares = [checking_piece_pos]
                else:
                    for i in range(1, 8):
                        end_square = king_pos + check[1]*i
                        valid_squares.append(end_square)

                        # Break when finding the checking piece
                        if end_square == checking_piece_pos:
                            break

                moves = self.get_all_check_evasion_moves(valid_squares)

            else:  # Double check, only king can move
                self.colors, self.move_dir, self.start_row, self.end_row = \
                    ('wb', -10, s.start_row_white, s.end_row_white) if self.is_white_turn else \
                    ('bw', 10, s.start_row_black, s.end_row_black)
                valid_squares = [self.checks[0][0], self.checks[1][0]]
                moves = []
                self.get_king_evasions(king_pos, moves, False, 'wK' if self.is_white_turn else 'bK', valid_squares)
        else:
            moves = self.get_all_possible_moves()

        return moves

    def get_all_possible_moves(self):

        # Initiate variables
        moves = []
        self.colors, self.move_dir, self.start_row, self.end_row = \
            ('wb', -10, s.start_row_white, s.end_row_white) if self.is_white_turn else \
            ('bw', 10, s.start_row_black, s.end_row_black)

        # Loop through all squares on the board
        for square in s.real_board_squares:
            piece = self.board[square]
            if piece[0] == self.colors[0]:
                self.move_functions[self.board[square][1]](square, moves, False, piece)

        return moves

# ---------------------------------------------------------------------------------------------------------

    def get_pawn_moves(self, square, moves, piece_pinned, piece):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        # 1 square move
        if self.board[square + self.move_dir] == '--':
            if not piece_pinned or pin_direction in (self.move_dir, -self.move_dir):
                if square + self.move_dir in self.end_row:
                    moves.append([square, square + self.move_dir, 'pQ', piece, -50000])
                    moves.append([square, square + self.move_dir, 'pR', piece, -50000])
                    moves.append([square, square + self.move_dir, 'pB', piece, -50000])
                    moves.append([square, square + self.move_dir, 'pN', piece, -50000])
                else:
                    moves.append([square, square + self.move_dir, 'no', piece, -50000])
                # 2 square move
                if square in self.start_row and self.board[square + 2*self.move_dir] == '--':
                    moves.append([square, square + 2*self.move_dir, 'ts', piece, -50000])

        # Capture to the left
        if self.board[square + self.move_dir - 1][0] == self.colors[1]:
            if not piece_pinned or pin_direction == self.move_dir - 1:
                if square + self.move_dir in self.end_row:
                    moves.append([square, square + self.move_dir - 1, 'pQ', piece, -50000])
                    moves.append([square, square + self.move_dir - 1, 'pR', piece, -50000])
                    moves.append([square, square + self.move_dir - 1, 'pB', piece, -50000])
                    moves.append([square, square + self.move_dir - 1, 'pN', piece, -50000])
                else:
                    moves.append([square, square + self.move_dir - 1, 'no', piece, -50000])

        # Enpassant to the left
        elif self.enpassant_square and square + self.move_dir - 1 == self.enpassant_square:
            if not piece_pinned or pin_direction == self.move_dir - 1:

                # Check if the move would result in check
                self.board[square], self.board[square - 1] = '--', '--'
                self.board[self.enpassant_square] = piece
                is_check = self.check_for_checks(self.king_location[not self.is_white_turn])
                self.board[square], self.board[square - 1] = piece, f'{self.colors[1]}p'
                self.board[self.enpassant_square] = '--'

                if not is_check:
                    moves.append([square, square + self.move_dir - 1, 'ep', piece, -50000])

        # Capture to the right
        if self.board[square + self.move_dir + 1][0] == self.colors[1]:
            if not piece_pinned or pin_direction == self.move_dir + 1:
                if square + self.move_dir in self.end_row:
                    moves.append([square, square + self.move_dir + 1, 'pQ', piece, -50000])
                    moves.append([square, square + self.move_dir + 1, 'pR', piece, -50000])
                    moves.append([square, square + self.move_dir + 1, 'pB', piece, -50000])
                    moves.append([square, square + self.move_dir + 1, 'pN', piece, -50000])
                else:
                    moves.append([square, square + self.move_dir + 1, 'no', piece, -50000])

        # Enpassant to the right
        elif self.enpassant_square and square + self.move_dir + 1 == self.enpassant_square:
            if not piece_pinned or pin_direction == self.move_dir + 1:

                # Check if the move would result in check
                self.board[square], self.board[square + 1] = '--', '--'
                self.board[self.enpassant_square] = piece
                is_check = self.check_for_checks(self.king_location[not self.is_white_turn])
                self.board[square], self.board[square + 1] = piece, f'{self.colors[1]}p'
                self.board[self.enpassant_square] = '--'

                if not is_check:
                    moves.append([square, square + self.move_dir + 1, 'ep', piece, -50000])

    def get_knight_moves(self, square, moves, piece_pinned, piece):
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                break

        for d in s.knight_moves:
            end_square = square + d
            if self.board[end_square] != 'FF' and self.board[end_square][0] != self.colors[0] and not piece_pinned:
                moves.append([square, end_square, 'no', piece, -50000])

    def get_bishop_moves(self, square, moves, piece_pinned, piece):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        for d in s.directions[4:8]:
            for i in range(1, 8):
                end_square = square + d * i
                end_piece = self.board[end_square][0]
                if end_piece in f'{self.colors[1]}-':
                    if not piece_pinned or pin_direction in (-d, d):  # Able to move towards and away from pin
                        moves.append([square, end_square, 'no', piece, -50000])

                        if end_piece == self.colors[1]:
                            break
                else:
                    break

    def get_rook_moves(self, square, moves, piece_pinned, piece):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        for d in s.directions[0:4]:
            for i in range(1, 8):
                end_square = square + d * i
                end_piece = self.board[end_square][0]
                if end_piece in f'{self.colors[1]}-':
                    if not piece_pinned or pin_direction in (d, -d):
                        moves.append([square, end_square, 'no', piece, -50000])

                        if end_piece == self.colors[1]:
                            break
                else:
                    break

    def get_queen_moves(self, square, moves, piece_pinned, piece):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        for d in s.directions:
            for i in range(1, 8):
                end_square = square + d * i
                end_piece = self.board[end_square][0]
                if end_piece in f'{self.colors[1]}-':
                    if not piece_pinned or pin_direction in (-d, d):
                        moves.append([square, end_square, 'no', piece, -50000])

                        if end_piece == self.colors[1]:
                            break
                else:
                    break

    def get_king_moves(self, square, moves, _, piece):

        for d in s.directions:
            end_square = square + d
            end_piece = self.board[end_square]
            if end_piece[0] not in f'{self.colors[0]}F':

                # Temporarily replace piece from the square and check all surrounding squares to see if it is attacked or not
                self.board[end_square] = '--'
                is_in_check = self.check_for_checks(end_square)
                self.board[end_square] = end_piece

                if not is_in_check:
                    moves.append([square, end_square, 'no', piece, -50000])

        # Castling
        # If not in check
        if not self.is_in_check:

            # Castle King side, if no squares in between are occupied and has king side rights.
            if all(x == '--' for x in (self.board[square + 1], self.board[square + 2])) and \
                    (self.castling_rights & s.castling_numbers['wk'] if self.is_white_turn else self.castling_rights & s.castling_numbers['bk']):

                # Check if squares are in check or not
                is_in_check_1 = self.check_for_checks(square + 1)
                is_in_check_2 = self.check_for_checks(square + 2)

                if not (is_in_check_1 or is_in_check_2):
                    moves.append([square, square + 2, 'castling', piece, -50000])

            # Castle Queen side, if no squares in between are occupied and has queen side rights.
            if all(x == '--' for x in (self.board[square - 1], self.board[square - 2], self.board[square - 3])) and \
                    (self.castling_rights & s.castling_numbers['wq'] if self.is_white_turn else self.castling_rights & s.castling_numbers['bq']):

                # Check if squares are in check or not, king doesn't pass the knight square on queenside castle so no use in checking that square
                is_in_check_1 = self.check_for_checks(square - 1)
                is_in_check_2 = self.check_for_checks(square - 2)

                if not (is_in_check_1 or is_in_check_2):
                    moves.append([square, square - 2, 'castling', piece, -50000])

# ---------------------------------------------------------------------------------------------------------
#                             Normal check evasion: Get all valid moves during check
# ---------------------------------------------------------------------------------------------------------

    def get_all_check_evasion_moves(self, valid_squares):

        # Initiate variables
        moves = []
        self.colors, self.move_dir, self.start_row, self.end_row = \
            ('wb', -10, s.start_row_white, s.end_row_white) if self.is_white_turn else \
            ('bw', 10, s.start_row_black, s.end_row_black)

        # Loop through the squares
        for square in s.real_board_squares:
            piece = self.board[square]
            if piece[0] == self.colors[0]:
                self.move_check_functions[self.board[square][1]](square, moves, False, piece, valid_squares)

        return moves

    def get_king_evasions(self, square, moves, _, piece, __):

        for d in s.directions:
            end_square = square + d
            end_piece = self.board[end_square]
            if end_piece[0] not in f'{self.colors[0]}F':

                # Temporarily replace piece from the square and check all surrounding squares to see if it is attacked or not
                self.board[end_square] = '--'
                is_in_check = self.check_for_checks(end_square)
                self.board[end_square] = end_piece

                if not is_in_check:
                    moves.append([square, end_square, 'no', piece, -50000])

    def get_pawn_evasions(self, square, moves, piece_pinned, piece, valid_squares):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        # 1 square move
        if self.board[square + self.move_dir] == '--':
            if not piece_pinned or pin_direction in (self.move_dir, -self.move_dir):

                if square + self.move_dir in valid_squares:
                    if square + self.move_dir in self.end_row:
                        moves.append([square, square + self.move_dir, 'pQ', piece, -50000])
                        moves.append([square, square + self.move_dir, 'pR', piece, -50000])
                        moves.append([square, square + self.move_dir, 'pB', piece, -50000])
                        moves.append([square, square + self.move_dir, 'pN', piece, -50000])
                    else:
                        moves.append([square, square + self.move_dir, 'no', piece, -50000])
                # 2 square move
                if square + 2 * self.move_dir in valid_squares:
                    if square in self.start_row and self.board[square + 2 * self.move_dir] == '--':
                        moves.append([square, square + 2 * self.move_dir, 'ts', piece, -50000])

        # Capture to the left
        if square + self.move_dir - 1 in valid_squares:
            if self.board[square + self.move_dir - 1][0] == self.colors[1]:
                if not piece_pinned or pin_direction == self.move_dir - 1:
                    if square + self.move_dir in self.end_row:
                        moves.append([square, square + self.move_dir - 1, 'pQ', piece, -50000])
                        moves.append([square, square + self.move_dir - 1, 'pR', piece, -50000])
                        moves.append([square, square + self.move_dir - 1, 'pB', piece, -50000])
                        moves.append([square, square + self.move_dir - 1, 'pN', piece, -50000])
                    else:
                        moves.append([square, square + self.move_dir - 1, 'no', piece, -50000])

        # Enpassant to the left
        elif square - 1 in valid_squares:
            if self.enpassant_square and square + self.move_dir - 1 == self.enpassant_square:
                if not piece_pinned or pin_direction == self.move_dir - 1:

                    # Check if the move would result in check
                    self.board[square], self.board[square - 1] = '--', '--'
                    self.board[self.enpassant_square] = piece
                    is_check = self.check_for_checks(self.king_location[not self.is_white_turn])
                    self.board[square], self.board[square - 1] = piece, f'{self.colors[1]}p'
                    self.board[self.enpassant_square] = '--'

                    if not is_check:
                        moves.append([square, square + self.move_dir - 1, 'ep', piece, -50000])

        # Capture to the right
        if square + self.move_dir + 1 in valid_squares:
            if self.board[square + self.move_dir + 1][0] == self.colors[1]:
                if not piece_pinned or pin_direction == self.move_dir + 1:
                    if square + self.move_dir in self.end_row:
                        moves.append([square, square + self.move_dir + 1, 'pQ', piece, -50000])
                        moves.append([square, square + self.move_dir + 1, 'pR', piece, -50000])
                        moves.append([square, square + self.move_dir + 1, 'pB', piece, -50000])
                        moves.append([square, square + self.move_dir + 1, 'pN', piece, -50000])
                    else:
                        moves.append([square, square + self.move_dir + 1, 'no', piece, -50000])

        # Enpassant to the right
        elif square + 1 in valid_squares:
            if self.enpassant_square and square + self.move_dir + 1 == self.enpassant_square:
                if not piece_pinned or pin_direction == self.move_dir + 1:

                    # Check if the move would result in check
                    self.board[square], self.board[square + 1] = '--', '--'
                    self.board[self.enpassant_square] = piece
                    is_check = self.check_for_checks(self.king_location[not self.is_white_turn])
                    self.board[square], self.board[square + 1] = piece, f'{self.colors[1]}p'
                    self.board[self.enpassant_square] = '--'

                    if not is_check:
                        moves.append([square, square + self.move_dir + 1, 'ep', piece, -50000])

    def get_knight_evasions(self, square, moves, piece_pinned, piece, valid_squares):
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                break

        for d in s.knight_moves:
            end_square = square + d
            if end_square in valid_squares and self.board[end_square] != 'FF' and self.board[end_square][0] != self.colors[0] and not piece_pinned:
                moves.append([square, end_square, 'no', piece, -50000])

    def get_bishop_evasions(self, square, moves, piece_pinned, piece, valid_squares):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        for d in s.directions[4:8]:
            for i in range(1, 8):
                end_square = square + d * i
                end_piece = self.board[end_square][0]
                if end_piece in f'{self.colors[1]}-':
                    if end_square in valid_squares and (not piece_pinned or pin_direction in (-d, d)):  # Able to move towards and away from pin
                        moves.append([square, end_square, 'no', piece, -50000])

                    if end_piece == self.colors[1]:
                        break
                else:
                    break

    def get_rook_evasions(self, square, moves, piece_pinned, piece, valid_squares):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        for d in s.directions[0:4]:
            for i in range(1, 8):
                end_square = square + d * i
                end_piece = self.board[end_square][0]
                if end_piece in f'{self.colors[1]}-':
                    if end_square in valid_squares and (not piece_pinned or pin_direction in (d, -d)):
                        moves.append([square, end_square, 'no', piece, -50000])

                    if end_piece == self.colors[1]:
                        break
                else:
                    break

    def get_queen_evasions(self, square, moves, piece_pinned, piece, valid_squares):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        for d in s.directions:
            for i in range(1, 8):
                end_square = square + d * i
                end_piece = self.board[end_square][0]
                if end_piece in f'{self.colors[1]}-':
                    if end_square in valid_squares and (not piece_pinned or pin_direction in (-d, d)):
                        moves.append([square, end_square, 'no', piece, -50000])

                    if end_piece == self.colors[1]:
                        break
                else:
                    break

# ---------------------------------------------------------------------------------------------------------
#                            Capture moves: Get valid capturing moves
# ---------------------------------------------------------------------------------------------------------

    # Get all moves without considering checks
    def get_all_capture_moves(self):

        # Initiate variables
        moves = []
        self.colors, self.move_dir, self.start_row, self.end_row = \
            ('wb', -10, s.start_row_white, s.end_row_white) if self.is_white_turn else \
            ('bw', 10, s.start_row_black, s.end_row_black)

        for square in s.real_board_squares:
            piece = self.board[square]
            if piece[0] == self.colors[0]:
                self.move_capture_functions[self.board[square][1]](square, moves, False, piece)

        return moves

    # Get all moves considering checks and pins
    def get_capture_moves(self):

        king_pos = self.king_location[not self.is_white_turn]

        # Find if is in check and all the possible pinned pieces
        self.is_in_check, self.pins, self.checks = self.check_for_pins_and_checks(king_pos)

        if self.is_in_check:
            if len(self.checks) == 1:  # Single check

                # Get the squares in between checker and king. If it is knight you can only take the knight, else go in between or capture the piece.
                check = self.checks[0]
                checking_piece_pos = check[0]

                valid_squares = []
                if self.board[checking_piece_pos][1] == 'N':
                    valid_squares = [checking_piece_pos]
                else:
                    for i in range(1, 8):
                        end_square = king_pos + check[1] * i
                        valid_squares.append(end_square)

                        # Break when finding the checking piece
                        if end_square == checking_piece_pos:
                            break

                moves = self.get_capturing_check_evasion_moves(valid_squares)

            else:  # Double check
                self.colors, self.move_dir, self.start_row, self.end_row = \
                    ('wb', -10, s.start_row_white, s.end_row_white) if self.is_white_turn else \
                    ('bw', 10, s.start_row_black, s.end_row_black)
                valid_squares = [self.checks[0][0], self.checks[1][0]]
                moves = []
                self.get_king_capture_evasions(king_pos, moves, False, 'wK' if self.is_white_turn else 'bK', valid_squares)
        else:
            moves = self.get_all_capture_moves()

        return moves

# ---------------------------------------------------------------------------------------------------------

    def get_pawn_captures(self, square, moves, piece_pinned, piece):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        # Capture and enpassant to the left
        if self.board[square + self.move_dir - 1][0] == self.colors[1]:
            if not piece_pinned or pin_direction == self.move_dir - 1:
                if square + self.move_dir in self.end_row:
                    moves.append([square, square + self.move_dir - 1, 'pQ', piece, -50000])
                else:
                    moves.append([square, square + self.move_dir - 1, 'no', piece, -50000])

        elif self.enpassant_square and square + self.move_dir - 1 == self.enpassant_square:
            if not piece_pinned or pin_direction == self.move_dir - 1:
                king_pos = self.king_location[not self.is_white_turn]

                # Check if the move would result in check
                self.board[square], self.board[square - 1] = '--', '--'
                self.board[self.enpassant_square] = piece
                is_check = self.check_for_checks(king_pos)
                self.board[square], self.board[square - 1] = piece, f'{self.colors[1]}p'
                self.board[self.enpassant_square] = '--'

                if not is_check:
                    moves.append([square, square + self.move_dir - 1, 'ep', piece, -50000])

        # Capture, and enpassant to the right
        if self.board[square + self.move_dir + 1][0] == self.colors[1]:
            if not piece_pinned or pin_direction == self.move_dir + 1:
                if square + self.move_dir in self.end_row:
                    moves.append([square, square + self.move_dir + 1, 'pQ', piece, -50000])
                else:
                    moves.append([square, square + self.move_dir + 1, 'no', piece, -50000])

        elif self.enpassant_square and square + self.move_dir + 1 == self.enpassant_square:
            if not piece_pinned or pin_direction == self.move_dir + 1:
                king_pos = self.king_location[not self.is_white_turn]

                # Check if the move would result in check
                self.board[square], self.board[square + 1] = '--', '--'
                self.board[self.enpassant_square] = piece
                is_check = self.check_for_checks(king_pos)
                self.board[square], self.board[square + 1] = piece, f'{self.colors[1]}p'
                self.board[self.enpassant_square] = '--'

                if not is_check:
                    moves.append([square, square + self.move_dir + 1, 'ep', piece, -50000])

    def get_knight_captures(self, square, moves, piece_pinned, piece):
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                break

        for d in s.knight_moves:
            end_square = square + d
            if self.board[end_square][0] == self.colors[1] and not piece_pinned:
                moves.append([square, end_square, 'no', piece, -50000])

    def get_bishop_captures(self, square, moves, piece_pinned, piece):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        for d in s.directions[4:8]:
            for i in range(1, 8):
                end_square = square + d * i
                end_piece = self.board[end_square][0]
                if end_piece == self.colors[1]:
                    if not piece_pinned or pin_direction in (-d, d):  # Able to move towards and away from pin
                        moves.append([square, end_square, 'no', piece, -50000])

                        # Already found capture in this direction, can't find more
                        break
                # Friendly piece, break
                elif end_piece in f'{self.colors[0]}F':
                    break

    def get_rook_captures(self, square, moves, piece_pinned, piece):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        for d in s.directions[0:4]:
            for i in range(1, 8):
                end_square = square + d * i
                end_piece = self.board[end_square][0]
                if end_piece in self.colors[1]:
                    if not piece_pinned or pin_direction in (d, -d):
                        moves.append([square, end_square, 'no', piece, -50000])

                        # Already found capture in this direction, can't find more
                        break
                # Friendly piece or off the board, break
                elif end_piece in f'{self.colors[0]}F':
                    break

    def get_queen_captures(self, square, moves, piece_pinned, piece):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        for d in s.directions:
            for i in range(1, 8):
                end_square = square + d * i
                end_piece = self.board[end_square][0]
                if end_piece in self.colors[1]:
                    if not piece_pinned or pin_direction in (-d, d):
                        moves.append([square, end_square, 'no', piece, -50000])

                        # Already found capture in this direction, can't find more
                        break
                # Friendly piece or off board, break
                elif end_piece in f'{self.colors[0]}F':
                    break

    def get_king_captures(self, square, moves, _, piece):

        for d in s.directions:
            end_square = square + d
            end_piece = self.board[end_square]
            if f'{self.colors[1]}' in end_piece[0]:

                # Temporarily replace piece from the square and check all surrounding squares to see if it is attacked or not
                self.board[end_square] = '--'
                is_in_check = self.check_for_checks(end_square)
                self.board[end_square] = end_piece

                if not is_in_check:
                    moves.append([square, end_square, 'no', piece, -50000])

# ---------------------------------------------------------------------------------------------------------
#                         Capture check evasion: Get valid capturing moves during check
# ---------------------------------------------------------------------------------------------------------

    def get_capturing_check_evasion_moves(self, valid_squares):

        # Initiate variables
        moves = []
        self.colors, self.move_dir, self.start_row, self.end_row = \
            ('wb', -10, s.start_row_white, s.end_row_white) if self.is_white_turn else \
            ('bw', 10, s.start_row_black, s.end_row_black)

        # Loop through the squares
        for square in s.real_board_squares:
            piece = self.board[square]
            if piece[0] == self.colors[0]:
                self.move_check_capture_functions[self.board[square][1]](square, moves, False, piece, valid_squares)

        return moves

    def get_king_capture_evasions(self, square, moves, _, piece, valid_squares):

        for d in s.directions:
            end_square = square + d
            end_piece = self.board[end_square]

            if end_square in valid_squares:

                # Temporarily replace piece from the square and check all surrounding squares to see if it is attacked or not
                self.board[end_square] = '--'
                is_in_check = self.check_for_checks(end_square)
                self.board[end_square] = end_piece

                if not is_in_check:
                    moves.append([square, end_square, 'no', piece, -50000])
                break

    def get_pawn_capture_evasions(self, square, moves, piece_pinned, piece, valid_squares):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        # Capture to the left
        if square + self.move_dir - 1 in valid_squares:
            if self.board[square + self.move_dir - 1][0] == self.colors[1]:
                if not piece_pinned or pin_direction == self.move_dir - 1:
                    if square + self.move_dir in self.end_row:
                        moves.append([square, square + self.move_dir - 1, 'pQ', piece, -50000])
                        moves.append([square, square + self.move_dir - 1, 'pR', piece, -50000])
                        moves.append([square, square + self.move_dir - 1, 'pB', piece, -50000])
                        moves.append([square, square + self.move_dir - 1, 'pN', piece, -50000])
                    else:
                        moves.append([square, square + self.move_dir - 1, 'no', piece, -50000])

        # Enpassant to the left
        elif square - 1 in valid_squares:
            if self.enpassant_square and square + self.move_dir - 1 == self.enpassant_square:
                if not piece_pinned or pin_direction == self.move_dir - 1:

                    # Check if the move would result in check
                    self.board[square], self.board[square - 1] = '--', '--'
                    self.board[self.enpassant_square] = piece
                    is_check = self.check_for_checks(self.king_location[not self.is_white_turn])
                    self.board[square], self.board[square - 1] = piece, f'{self.colors[1]}p'
                    self.board[self.enpassant_square] = '--'

                    if not is_check:
                        moves.append([square, square + self.move_dir - 1, 'ep', piece, -50000])

        # Capture to the right
        if square + self.move_dir + 1 in valid_squares:
            if self.board[square + self.move_dir + 1][0] == self.colors[1]:
                if not piece_pinned or pin_direction == self.move_dir + 1:
                    if square + self.move_dir in self.end_row:
                        moves.append([square, square + self.move_dir + 1, 'pQ', piece, -50000])
                        moves.append([square, square + self.move_dir + 1, 'pR', piece, -50000])
                        moves.append([square, square + self.move_dir + 1, 'pB', piece, -50000])
                        moves.append([square, square + self.move_dir + 1, 'pN', piece, -50000])
                    else:
                        moves.append([square, square + self.move_dir + 1, 'no', piece, -50000])

        # Enpassant to the right
        elif square + 1 in valid_squares:
            if self.enpassant_square and square + self.move_dir + 1 == self.enpassant_square:
                if not piece_pinned or pin_direction == self.move_dir + 1:

                    # Check if the move would result in check
                    self.board[square], self.board[square + 1] = '--', '--'
                    self.board[self.enpassant_square] = piece
                    is_check = self.check_for_checks(self.king_location[not self.is_white_turn])
                    self.board[square], self.board[square + 1] = piece, f'{self.colors[1]}p'
                    self.board[self.enpassant_square] = '--'

                    if not is_check:
                        moves.append([square, square + self.move_dir + 1, 'ep', piece, -50000])

    def get_knight_capture_evasions(self, square, moves, piece_pinned, piece, valid_squares):
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                break

        for d in s.knight_moves:
            end_square = square + d
            if end_square in valid_squares and self.board[end_square][0] == self.colors[1] and not piece_pinned:
                moves.append([square, end_square, 'no', piece, -50000])

    def get_bishop_capture_evasions(self, square, moves, piece_pinned, piece, valid_squares):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        for d in s.directions[4:8]:
            for i in range(1, 8):
                end_square = square + d * i
                end_piece = self.board[end_square][0]
                if end_piece == self.colors[1]:
                    if end_square in valid_squares and (not piece_pinned or pin_direction in (-d, d)):  # Able to move towards and away from pin
                        moves.append([square, end_square, 'no', piece, -50000])

                        # Already found capture in this direction, can't find more
                        break

                # Friendly piece, break
                elif end_piece in f'{self.colors[0]}F':
                    break

    def get_rook_capture_evasions(self, square, moves, piece_pinned, piece, valid_squares):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        for d in s.directions[0:4]:
            for i in range(1, 8):
                end_square = square + d * i
                end_piece = self.board[end_square][0]
                if end_piece == self.colors[1]:
                    if end_square in valid_squares and (not piece_pinned or pin_direction in (d, -d)):
                        moves.append([square, end_square, 'no', piece, -50000])

                        # Already found capture in this direction, can't find more
                        break

                # Friendly piece, break
                elif end_piece in f'{self.colors[0]}F':
                    break

    def get_queen_capture_evasions(self, square, moves, piece_pinned, piece, valid_squares):
        pin_direction = ()
        for i in range(len(self.pins)):
            if self.pins[i][0] == square:
                piece_pinned = True
                pin_direction = (self.pins[i][1])
                break

        for d in s.directions:
            for i in range(1, 8):
                end_square = square + d * i
                end_piece = self.board[end_square][0]
                if end_piece == self.colors[1]:
                    if end_square in valid_squares and (not piece_pinned or pin_direction in (-d, d)):
                        moves.append([square, end_square, 'no', piece, -50000])

                        # Already found capture in this direction, can't find more
                        break

                # Friendly piece, break
                elif end_piece in f'{self.colors[0]}F':
                    break

# ---------------------------------------------------------------------------------------------------------
#                        Helpers: Check for checks, pins and both
# ---------------------------------------------------------------------------------------------------------

    # Checks if there are any pinned pieces or current checks
    def check_for_pins_and_checks(self, square):
        pins, checks = [], []
        is_in_check = False

        colors = 'wb' if self.is_white_turn else 'bw'

        # Check out from all directions from the king
        for i in range(8):
            d = s.directions[i]
            possible_pin = False
            for j in range(8):  # Check the entire row/column in that direction
                end_square = square + d*j
                piece_color, piece_type = self.board[end_square][0], self.board[end_square][1]
                if piece_type != 'F':
                    if piece_color == colors[0] and piece_type != 'K':
                        if not possible_pin:  # First own piece, possible pin
                            possible_pin = (end_square, d)
                        else:  # 2nd friendly piece, no pin
                            break
                    elif piece_color == colors[1]:
                        # 5 different cases:
                        # 1. Orthogonally from king and piece is a rook
                        # 2. Diagonally from king and piece is a bishop
                        # 3. 1 square away diagonally from king and piece is a pawn
                        # 4. Any direction and piece is a queen
                        # 5. Any direction 1 square away and piece is a king
                        if (0 <= i <= 3 and piece_type == 'R') or \
                                (4 <= i <= 7 and piece_type == 'B') or \
                                (j == 1 and piece_type == 'p' and ((colors[1] == 'w' and 6 <= i <= 7) or (colors[1] == 'b' and 4 <= i <= 5))) or \
                                (piece_type == 'Q') or \
                                (j == 1 and piece_type == 'K'):
                            if not possible_pin:  # No friendly piece is blocking -> is check
                                is_in_check = True
                                checks.append((end_square, d))
                                break
                            else:  # Friendly piece is blocking -> pinned piece
                                pins.append(possible_pin)
                                break
                        else:  # Enemy piece that is not applying check or pin
                            break
                else:  # i, j is off board
                    break

        # Check for knight checks
        for d in s.knight_moves:
            end_square = square + d
            end_piece = self.board[end_square]
            if end_piece != 'FF':
                if end_piece[0] == colors[1] and end_piece[1] == 'N':  # Enemy knight attacking king
                    is_in_check = True
                    checks.append((end_square, d))

        return is_in_check, pins, checks

    # Checks if there are any pinned pieces or current checks
    def check_for_checks(self, square):

        colors = 'wb' if self.is_white_turn else 'bw'

        # Check out from all directions from the king
        for i, d in enumerate(s.directions):
            for j in range(1, 8):  # Check the entire row/column in that direction
                end_square = square + d * j
                #print(square, end_square)
                piece_color, piece_type = self.board[end_square][0], self.board[end_square][1]
                if piece_type != 'F':
                    if piece_color == colors[0] and piece_type != 'K':
                        break
                    elif piece_color == colors[1]:
                        if (0 <= i <= 3 and piece_type == 'R') or \
                                (4 <= i <= 7 and piece_type == 'B') or \
                                (j == 1 and piece_type == 'p' and ((colors[1] == 'w' and 6 <= i <= 7) or (colors[1] == 'b' and 4 <= i <= 5))) or \
                                (piece_type == 'Q') or \
                                (j == 1 and piece_type == 'K'):
                            return True
                        else:  # Enemy piece that is not applying check or pin
                            break
                else:  # i, j is off board
                    break

        # Check for knight checks
        for d in s.knight_moves:
            end_piece = self.board[square + d]
            if end_piece != 'FF':
                if end_piece[1] == 'N' and end_piece[0] == colors[1]:  # Enemy knight attacking king
                    return True

        return False

    # Checks if there are any pinned pieces or current checks
    def check_for_pins(self, square):
        pins = []

        colors = 'wb' if self.is_white_turn else 'bw'

        # Check out from all directions from the king
        for i in range(8):
            d = s.directions[i]
            possible_pin = False
            for j in range(8):  # Check the entire row/column in that direction
                end_square = square + d * j
                piece_color, piece_type = self.board[end_square][0], self.board[end_square][1]
                if piece_type != 'F':
                    if piece_color == colors[0] and piece_type != 'K':
                        if not possible_pin:  # First own piece, possible pin
                            possible_pin = (end_square, d)
                        else:  # 2nd friendly piece, no pin
                            break
                    elif piece_color == colors[1]:
                        if (0 <= i <= 3 and piece_type == 'R') or \
                                (4 <= i <= 7 and piece_type == 'B') or \
                                (j == 1 and piece_type == 'p' and ((colors[1] == 'w' and 6 <= i <= 7) or (colors[1] == 'b' and 4 <= i <= 5))) or \
                                (piece_type == 'Q') or \
                                (j == 1 and piece_type == 'K'):
                            if not possible_pin:  # No friendly piece is blocking -> is check
                                break
                            else:  # Friendly piece is blocking -> pinned piece
                                pins.append(possible_pin)
                                break
                        else:  # Enemy piece that is not applying check or pin
                            break
                else:  # i, j is off board
                    break

        return pins
