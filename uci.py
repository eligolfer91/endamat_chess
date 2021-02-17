# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                          uci.py
#
#                   - Handles communication with an external gui
#                   - Handles all common inputs such as fixed depth, time per move,
#                     time per game (with and without increment)
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

import sys
import logging
import time as t

from gamestate import GameState
from ai import Ai
import settings as s


# --------------------------------------------------------------------------------
#                            UCI related functions
# --------------------------------------------------------------------------------

# Disable buffering
class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
        sys.stderr.write(data)
        sys.stderr.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


class UCI:

    def __init__(self):
        self.gamestate = GameState('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

        self.best_move = None
        self.best_score = None

    def main(self):

        logging.basicConfig(filename='log_uci.log', level=logging.DEBUG)

        def output(line):
            print(line, flush=True)
            logging.debug(line)

        engine_quit = False
        while True:
            engine_input = input()

            logging.debug(f'>>> {engine_input} ')

            # Quit engine
            if engine_input in 'quit stop':
                break

            # Engine info
            elif engine_input == 'uci':
                output('id name Endamat Chess')
                output('id author Elias Nilsson')
                output('uciok')

            # Check to see if engine is ready
            elif engine_input == 'isready':
                output('readyok')

            # Create a new game
            elif engine_input == 'ucinewgame':
                self.gamestate = GameState('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

            # Handle a given position
            elif engine_input.startswith('position'):

                # Split engine input into parts
                inputs = engine_input.split()

                try:
                    # Handle building up the board from a FEN string
                    if inputs[1] == "fen":

                        # If moves are given in input, initiate board and make the moves
                        if "moves" in inputs:

                            # Find the entire FEN in the command
                            fen = ' '.join(inputs[2:inputs.index('moves')])
                            self.gamestate = GameState(fen)

                            # Loop through the moves and make them on the board
                            moves = inputs[inputs.index('moves') + 1:]
                            for move in moves:
                                gamestate_move = self.parse_move(move)
                                self.gamestate.make_move(gamestate_move)
                        else:
                            fen = ' '.join(inputs[2:])
                            self.gamestate = GameState(fen)

                    # Handle board from building up the board from the start pos
                    elif inputs[1] == "startpos":

                        # Init board state to start pos
                        self.gamestate = GameState('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')

                        # If moves are given in input, initiate board and make the moves
                        if 'moves' in inputs:

                            # Loop through the moves and make them on the board
                            moves = inputs[inputs.index('moves') + 1:]
                            for move in moves:
                                gamestate_move = self.parse_move(move)
                                self.gamestate.make_move(gamestate_move)
                    else:
                        print("Unknown position type")

                except Exception as exep:
                    print("Something went wrong with the position. Please try again")
                    print(exep)

            # The go command will initiate search and we need to output best move from given position
            elif engine_input.startswith('go'):

                # Default options
                depth = -1
                time = -1
                movetime = -1
                stoptime = 0
                inc = 0
                timeset = 0
                movestogo = 50

                # Loop through given parameters after go command
                _, *params = engine_input.split(' ')
                for param, value in zip(*2*(iter(params),)):

                    # Infinite search
                    if param == 'infinite':
                        pass

                    # Fixed depth search
                    elif param == 'depth':
                        depth = max(1, int(value))  # Can't use 0 or negative values as depth

                    # Black time increment if black turn
                    elif param == 'binc':
                        if not self.gamestate.is_white_turn:
                            inc = int(value)/1000

                    # White time increment if white turn
                    elif param == 'winc':
                        if self.gamestate.is_white_turn:
                            inc = int(value)/1000

                    # Black time limit
                    elif param == 'btime':
                        if not self.gamestate.is_white_turn:
                            time = int(value)/1000

                    # White time limit
                    elif param == 'wtime':
                        if self.gamestate.is_white_turn:
                            time = int(value)/1000

                    # Amount of time allowed to make a move
                    elif param == 'movetime':
                        movetime = int(value)/1000

                    # Number of moves to go before time gets increased
                    elif param == 'movestogo':
                        movestogo = int(value)

                    # Different time controls placeholder
                    else:
                        print(f'"{param}" with value "{value}" is not a valid/legal input command.')

                # If depth is not available, set it to something large
                if depth == -1:
                    depth = 64

                # Init start time
                starttime = t.time()

                # If move time was given, update time to movetime and moves to go to 1 (1 move in x ms)
                if movetime != -1:
                    time = movetime
                    movestogo = 1

                # If time control is available, flag that we play with time control and set timing
                if time != -1:
                    timeset = 1

                    # Divide time equally between how many moves we should do
                    time /= movestogo

                    # Lag compensation 100 ms
                    if time > 1.5:
                        time -= 0.1

                    # Add time and increment to get what time we should stop at
                    stoptime = starttime + time + inc

                    # Increment when time is almost up
                    if time < 1.5 and inc and depth == 64:
                        stoptime = starttime + inc - 0.1

                # Search position given the parameters from GUI
                searcher = Ai(self.gamestate, search_depth=depth, stoptime=stoptime, timeset=timeset)

                searcher.nodes = -1

                searcher.time_start = t.time()

                # Initialize best move and best score
                self.best_move = self.gamestate.get_valid_moves()[0]
                self.best_score = 0

                for current_depth in range(1, depth + 1):

                    # Break if time is up
                    if searcher.stopped or engine_quit:
                        break

                    # Calculate move and score for current depth
                    move, score = searcher.ai_make_move(current_depth=current_depth, best_move=self.best_move, best_score=self.best_score)

                    # Print info to GUI after each depth if we returned a valid move (engine didn't stop calculating).
                    # Check if we reached mate score, if so calculate how many moves left until mate to print in GUI.
                    if not searcher.stopped:
                        if -searcher.mate_value < score < -searcher.mate_score:
                            output('info score mate %d depth %d nodes %ld time %d pv %s' % (-(score + searcher.mate_value) / 2 - 1, current_depth, searcher.nodes, searcher.timer * 1000, searcher.pv_line))

                        elif searcher.mate_score < score < searcher.mate_value:
                            output('info score mate %d depth %d nodes %ld time %d pv %s' % ((searcher.mate_value - score) / 2 + 1, current_depth, searcher.nodes, searcher.timer * 1000, searcher.pv_line))

                        else:
                            output('info score cp %d depth %d nodes %ld time %d pv %s' % (score, current_depth, searcher.nodes, searcher.timer * 1000, searcher.pv_line))

                        # Update best move and best score
                        self.best_move, self.best_score = move, score

                # Output best move to engine console
                if self.best_move[2] in 'pQpRpBpN':
                    output(f'bestmove {f"{s.square_to_board[self.best_move[0]]}{s.square_to_board[self.best_move[1]]}{self.best_move[2][-1].lower()}"}')
                else:
                    output(f'bestmove {f"{s.square_to_board[self.best_move[0]]}{s.square_to_board[self.best_move[1]]}"}')

            elif engine_input.startswith('time'):
                our_time = int(engine_input.split()[1])

            elif engine_input.startswith('otim'):
                opp_time = int(engine_input.split()[1])

            else:
                output(f'"{engine_input}" is currently not a valid input command.')
                pass

    # Get a move from GUI and return it if legal
    def parse_move(self, move_string):

        possible_moves = self.gamestate.get_valid_moves()

        # From and to square
        from_square = s.board_to_square[move_string[0] + move_string[1]]
        to_square = s.board_to_square[move_string[2] + move_string[3]]

        # Loop over possible moves to see if the move is in the list
        for move in possible_moves:

            if move[0] == from_square and move[1] == to_square:

                # Check for promotion
                if move[2] in 'pQpRpBpN':

                    # Queen
                    if move[2][-1] == 'Q' and move_string[4] == 'q':
                        return move

                    # Rook
                    elif move[2][-1] == 'R' and move_string[4] == 'r':
                        return move

                    # Bishop
                    elif move[2][-1] == 'B' and move_string[4] == 'b':
                        return move

                    # Knight
                    elif move[2][-1] == 'N' and move_string[4] == 'n':
                        return move

                # Return legal move if no promotion
                else:
                    return move

        # Else the move is illegal
        return 0


if __name__ == '__main__':
    UCI().main()



