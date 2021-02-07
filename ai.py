# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                          ai.py
#
#                   - Searches for the best move with a Negamax function
#                   - Iterative deepening framework (in GUI or UCI file)
#                   - Sort moves based on PV-line, MVV/LVA, killer moves and history heuristics
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------


import time

import settings as s
import evaluation as e
import evaluation_settings as es
import helper_functions as hf

class Ai:

    def __init__(self, gamestate, search_depth=64, stoptime=0, timeset=0, check_timeout=2000):

        # Input variables
        self.gamestate = gamestate
        self.stoptime = stoptime
        self.timeset = timeset

        if self.stoptime or self.timeset:
            self.search_depth = 64
        else:
            self.search_depth = search_depth

        # Initialize variables abd helper arrays
        self.max_ply = 60
        self.pv_length = [0] * self.max_ply  # ply
        self.pv_table = [[0] * self.max_ply for _ in range(self.max_ply)]  # [ply][ply]
        self.pv_line = ''

        self.print_info = {}

        self.mate_score = 98000
        self.mate_value = 99000
        self.alpha = -100000
        self.beta = 100000

        self.tt = {0: {'key': 0, 'depth': 0, 'flag': 0, 'score': 0}}
        self.tt_move = {}

        # UCI parameters
        self.stopped = False

        # Keep track of 3-fold repetition
        self.repetition_table = {}
        self.repetition_index = 0
        self.repetition_table[self.repetition_index] = self.gamestate.zobrist_key

        # Initialize sort related variables
        self.killer_moves = [[0] * self.max_ply for _ in range(2)]  # [1st or 2nd killer move][ply]
        self.history_moves = [[0] * 64 for _ in range(12)]  # [piece][target square]

        # Initialize check related variables
        self.is_in_check = False

        # Variables to keep track of progress in the tree
        self.follow_pv = False
        self.score_pv = False
        self.nodes = -1
        self.can_reduce = True

        # Time how long time it takes to calculate the move
        self.timer = 0
        self.time_start = time.time()

        # How often to check for timeout (nodes)
        self.check_timeout = check_timeout

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                              Start the search and iterative deepening
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    def ai_make_move(self, current_depth=0, best_move=None, best_score=None):

        # Init variables
        self.timer = 0
        ply = 0

        # Reset killer and history moves
        self.killer_moves = [[0]*self.max_ply for _ in range(2)]  # [1st or 2nd killer move][ply]
        self.history_moves = [[0]*120 for _ in range(12)]  # [piece][target square]

        # Reset stopped timer
        self.stopped = False

        # Initiate PV line variables
        self.follow_pv = True
        self.pv_length = [0] * 60  # ply
        self.pv_table = [[0] * 60 for _ in range(60)]  # [ply][ply]

        # Search the position with the recursive Negamax function
        score = self.negamax(current_depth, ply, self.alpha, self.beta, False)

        # Test if aspiration window failed, if so need to redo with full window
        if self.beta <= score or score <= self.alpha:

            # Reset alpha and beta
            self.alpha, self.beta = -100000, 100000

            # Reset stopped timer
            self.stopped = False

            # Enable follow_pv line
            self.follow_pv = True

            self.pv_length = [0] * 60  # ply
            self.pv_table = [[0] * 60 for _ in range(60)]  # [ply][ply]

            # Search again with full window
            score = self.negamax(current_depth, ply, self.alpha, self.beta, False)

        # Set aspiration window, 50 works the best for som test positions
        self.alpha = score - s.aspiration_window
        self.beta = score + s.aspiration_window

        # Get the timing for the current depth and print the result
        # + small value to not get into division by 0 when calculating nodes/s
        self.timer = 0.001 + time.time() - self.time_start

        # If we have not yet timed out, save parameters to use later, otherwise best values from last iteration is used
        if not self.stopped:

            # Get PV-line on a nice format
            self.pv_line = hf.get_pv_line(self.gamestate, self.pv_table[0][:self.pv_length[0]])

            # Update best move and best score
            best_move = self.pv_table[0][0]
            best_score = score

            # Update print info dict which is used for printing info in GUI
            self.print_info[current_depth - 1] = {'depth': str(current_depth), 'time': f'{self.timer:.2f}', 'nodes': str(self.nodes), 'nodes_s': str(round((self.nodes * 1000) / (self.timer * 1000))),
                                                  'score': score, 'main_line': self.pv_line}

        # Return the best move found before timing out
        return best_move, best_score

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                      Negamax function
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    def negamax(self, depth, ply, alpha, beta, allow_nullmove):

        # TT
        #key = self.gamestate.zobrist_key
        #if key in self.tt:
        #   if self.tt[key]['depth'] >= depth:
        #        return self.tt[key]['score']

        # Init PV length
        self.pv_table[ply][ply] = 0
        self.pv_length[ply] = 0

        # Find if the position is a draw due to 3 fold repetition, if so return a draw score
        if self.is_repetition():
            return 0

        # Check if in check
        is_in_check = self.gamestate.check_for_checks(self.gamestate.king_location[not self.gamestate.is_white_turn])

        # Check extension
        if is_in_check:
            depth += 1

        # Depth with quiescence search
        if depth == 0:
            score = self.quiescence(ply, alpha, beta)
            #self.tt[key] = {'key': key, 'depth': depth, 'flag': 0, 'score': score}
            return score

        # Increment node count
        self.nodes += 1

        # Null move logic
        if allow_nullmove:
            if depth - 1 - s.R >= 0 and ply and not is_in_check:

                # Reset enpassant square
                enpassant_temp = self.gamestate.enpassant_square
                if self.gamestate.enpassant_square:
                    self.gamestate.zobrist_key ^= self.gamestate.zobrist_enpassant[self.gamestate.enpassant_square]
                self.gamestate.enpassant_square = None

                # Switch player turn the move is made
                self.gamestate.is_white_turn = not self.gamestate.is_white_turn
                self.gamestate.zobrist_key ^= self.gamestate.zobrist_side

                temp_key = self.gamestate.zobrist_key

                # Search position
                score = -self.negamax(depth - 1 - s.R, ply + 1, -beta, -beta + 1, False)

                self.gamestate.zobrist_key = temp_key

                # If there was an enpassant square, reset it back to the previous state
                if enpassant_temp:
                    self.gamestate.enpassant_square = enpassant_temp

                # Switch player turn the move is made
                self.gamestate.is_white_turn = not self.gamestate.is_white_turn

                if score >= beta:
                    return beta

        # Get legal moves
        '''if key in self.tt_move:
            children = self.tt_move[key]
        else:
            children = self.gamestate.get_valid_moves()
            self.tt_move[key] = children'''
        children = self.gamestate.get_valid_moves()

        # Extend if there is only one possible move (forced line) and if not in check (since we have that extension above).
        '''if len(children) == 1 and not is_in_check:
            depth += 1'''

        # Sort moves before Negamax
        children = self.sort_moves(ply, children)

        # If we are following PV line, we want to enable PV-scoring
        if self.follow_pv:
            self.enable_pv_scoring(ply, children)

        # Init legal moves counter and best move so far
        legal_moves = 0
        moves_searched = 0

        # Negamax loop
        for child in children:

            # Make the move
            self.gamestate.make_move(child)

            # Increment legal moves
            legal_moves += 1

            # LMR
            '''if moves_searched >= s.full_depth_moves and \
                depth >= s.reduction_limit and \
                not self.gamestate.check_for_checks(self.gamestate.king_location[not self.gamestate.is_white_turn]) and \
                self.gamestate.piece_captured == '--' and \
                self.can_reduce:

                self.can_reduce = False

                score = -self.negamax(depth - s.reduction_limit, ply + s.reduction_limit, -beta, -alpha, True)

                # Re-search
                if score > alpha:
                    score = -self.negamax(depth - 1, ply + 1, -beta, -alpha, True)
                    
            # Normal search
            else:
                self.can_reduce = True
                score = -self.negamax(depth - 1, ply + 1, -beta, -alpha, True)'''
            score = -self.negamax(depth - 1, ply + 1, -beta, -alpha, True)

            # Unmake the move
            self.gamestate.unmake_move()

            # Increase searched moves
            moves_searched += 1

            # Return if time is up, check every x nodes
            if not self.nodes % self.check_timeout:
                if self.timeset == 1 and time.time() >= self.stoptime:
                    self.stopped = True
                    return 0

            # Found a better move (PV-node)
            if score > alpha:
                alpha = score

                # Store history moves, only if it is a non-capturing move
                if self.gamestate.board[child[1]] == '--' and child[2] != 'ep':
                    self.history_moves[es.piece_to_number[child[3]]][child[1]] += depth

                # Write PV move to PV table for the given ply
                self.pv_table[ply][ply] = child

                # Loop over the next ply
                for next_ply in range(0, self.pv_length[ply + 1], 1):

                    # Copy move from deeper ply into current ply's line
                    self.pv_table[ply][ply + 1 + next_ply] = self.pv_table[ply + 1][ply + 1 + next_ply]

                # Adjust PV length
                self.pv_length[ply] = 1 + self.pv_length[ply + 1]

                # Fail-hard beta cutoff (node fails high)
                if score >= beta:

                    # Store killer moves, only if it is a non-capturing move
                    if self.gamestate.board[child[1]] == '--' and child[2] != 'ep':
                        self.killer_moves[1][ply] = self.killer_moves[0][ply]
                        self.killer_moves[0][ply] = child

                    return beta

        # If we don't have a legal move to make in the position, check whether it's checkmate or stalemate
        if not legal_moves:

            # Checkmate, return checkmate score
            if self.gamestate.is_in_check:
                return -self.mate_value + ply

            # Stalemate, return stalemate score
            return 0

        # Node fails low
        return alpha

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                      Quiescence search
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    def quiescence(self, ply, alpha, beta):

        # Return if time is up, check every x nodes
        if not self.nodes % self.check_timeout:
            if self.timeset == 1 and time.time() >= self.stoptime:
                self.stopped = True
                return 0

        # Increment nodes count
        self.nodes += 1

        # Find if the position is a draw due to 3 fold repetition, if so return a draw score
        if self.is_repetition():
            return 0

        # Evaluate the position
        score = e.evaluate(self.gamestate)

        # Fail-hard beta cutoff (node fails high)
        if score >= beta:
            return beta

        # Delta pruning (https://www.chessprogramming.org/Delta_Pruning)
        if score < alpha - 975:
            return alpha

        # Found a better move (PV-node)
        if score > alpha:
            alpha = score

        # Get pseudo legal capture moves
        children = self.gamestate.get_capture_moves()

        # Sort the moves
        children = self.sort_capture_moves(children)

        # Quiescence recursive loop
        for child in children:

            # Make the move
            self.gamestate.make_move(child)

            # Score the position after current move is made
            score = -self.quiescence(ply + 1, -beta, -alpha)

            # Take back move
            self.gamestate.unmake_move()

            # Found a better move (PV-node)
            if score > alpha:
                alpha = score

                # Fail-hard beta cutoff (node fails high)
                if score >= beta:
                    return beta

        # Node fails low
        return alpha

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                          Sort moves
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    def sort_moves(self, ply, moves):

        # Assign a score to each move
        for move in moves:
            move[4] = self.score_move(ply, move)

        # Sort the moves according to the scores
        moves.sort(key=lambda x: x[4], reverse=True)

        return moves

    # Score a move
    def score_move(self, ply, move):

        # If PV scoring is allowed
        if self.score_pv:

            # Make sure we are dealing with PV move
            if self.pv_table[0][ply] == move:
                # Disable score pv flag
                self.score_pv = False

                # Give PV move the highest score
                return s.pv_score

        # Score capture moves
        if self.gamestate.board[move[1]] != '--' or move[2] == 'ep':

            # MVV-LVA captures look-up (target piece(victim) - source piece(attacker))
            if 'ep' in move[2]:
                captured_piece = 'bp' if self.gamestate.is_white_turn else 'wp'
            else:
                captured_piece = self.gamestate.board[move[1]]

            return s.mvv_lva + 8*s.mvv_lva_values[captured_piece] - s.mvv_lva_values[self.gamestate.board[move[0]]]

        # Score quiet moves
        else:

            # Score first killer move
            if self.killer_moves[0][ply] == move:
                return s.first_killer_move

            # Score second killer move
            elif self.killer_moves[1][ply] == move:
                return s.second_killer_move

            # Score history moves
            else:
                return self.history_moves[es.piece_to_number[move[3]]][move[1]]

    def sort_capture_moves(self, moves):

        # Assign a score to each move
        for move in moves:

            # MVV-LVA captures look-up (target piece(victim) - source piece(attacker))
            if 'ep' in move[2]:
                captured_piece = 'bp' if self.gamestate.is_white_turn else 'wp'
            else:
                captured_piece = self.gamestate.board[move[1]]

            move[4] = s.mvv_lva + 8*s.mvv_lva_values[captured_piece] - s.mvv_lva_values[self.gamestate.board[move[0]]]

        # Sort the moves according to the scores
        moves.sort(key=lambda x: x[4], reverse=True)

        return moves

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                            Helper functions
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    # Find if a position is stalemated due to 3 fold repetition or 50 move rule
    def is_repetition(self):

        # Loop over the entire position table
        repetitions = 0
        latest_key = self.gamestate.repetition_table[-1][0]
        for key, piece_moved, piece_captured in reversed(self.gamestate.repetition_table):

            # Check if position has occurred before in the came
            if key == latest_key:
                repetitions += 1

            # If 3 positions has occurred before, return stalemate by 3 fold repetition
            if repetitions == 3:
                return True

            # Break early if there is a pawn move or capture since position can't be the same after such move has been made
            if piece_captured != '--' or piece_moved in 'wpbp':
                return False

        # Check half move counter
        if self.gamestate.halfmove_counter >= 100:
            return True

        # No 3-fold was found
        return False

    def enable_pv_scoring(self, ply, moves):

        # Disable following PV line
        self.follow_pv = False

        # Loop over move within move list
        for move in moves:

            # Make sure we hit PV move
            if self.pv_table[0][ply] == move:

                # Enable move scoring and follow pv
                self.score_pv = True
                self.follow_pv = True

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                    Return a random move
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    def return_random_move(self):
        import random

        random_move = random.choice(self.gamestate.get_valid_moves())
        self.gamestate.make_move(random_move)
        evaluation = e.evaluate(self.gamestate)
        self.gamestate.unmake_move()

        return random_move, evaluation
