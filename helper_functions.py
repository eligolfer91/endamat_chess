# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                     helper_functions.py
#
#                   - Tasks that are used in several files are handled here
#                   - Printing, board manipulations, getting PV-line etc
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

import settings as s


# Print the principal variation line
def get_pv_line(gamestate, pv_line):

    import copy

    # Copy the gamestate
    gamestate_copy = copy.deepcopy(gamestate)

    # Loop over the PV-line and extract each moves from and to square
    move_list_pv, move_list = [], ''
    for move in pv_line:

        # Make the move on the copied board to not ruin normal gamestate
        gamestate_copy.make_move(move)

        # From and to square for PV line standard print
        from_sq = s.square_to_board[move[0]]
        to_sq = s.square_to_board[move[1]]

        # Piece moved and promotion piece
        piece = move[3][1]
        move_type = move[2]
        promo = move_type[-1].lower() if move_type in 'pQpRpBpN' else ''

        # Captures
        if gamestate_copy.piece_captured != '--':

            # Enpassant are special
            if 'ep' in move_type:
                text = f'{from_sq}x{to_sq} e.p.'

            # Else normal capture
            else:
                if piece in 'pP':
                    text = f'{from_sq}x{to_sq}'
                else:
                    text = f'{piece}{from_sq}x{to_sq}'

        # Quiet moves
        else:

            # Castling king side
            if move_type == 'castling' and move[0] - move[1] == -2:
                text = 'O-O'
                # Queen side
            elif move_type == 'castling' and move[0] - move[1] == 2:
                text = 'O-O-O'

            # Normal quiet moves
            else:
                if piece in 'pP':
                    text = f'{from_sq}-{to_sq}'
                else:
                    text = f'{piece}{from_sq}-{to_sq}'

        # If promotion, add the promoted piece to the text
        if promo:
            text += promo

        # Handle check, checkmate or stalemate
        # See if there are any legal moves left for opponent, break if we find a legal move to speed up process
        possible_moves = gamestate_copy.get_valid_moves()

        # If is in check and no moves -> checkmate. If not in check and no moves -> stalemate.
        if gamestate_copy.is_in_check:

            # Checkmate
            if not possible_moves:
                text += '#'

            # Normal check
            else:
                text += '+'

        elif not possible_moves:

            # Draw
            text += ' 1/2-1/2'

        # Add to move list
        move_list += f'{text}, '

    # Remove last comma
    move_list = move_list[:-2]

    return move_list


# Rotate a board to blacks perspective
def rotate_board(board):

    rotated_board = [0]*120
    for row in range(12):
        rotated_board[row*10:10+row*10] = board[row*10:10+row*10][::-1]

    return rotated_board[::-1]


# Print the given move list
def print_move_list(moves, gamestate=None):
    # Print out all moves in move list
    # [from, to, type, piece_increase, piece_moved]

    print('From    To    Piece    Promo    Capture    Double    Ep    Castling')
    for move in moves:

        from_sq = s.square_to_board[move[0]]
        to_sq = s.square_to_board[move[1]]
        piece = move[3][1].upper() if move[3][0] == 'w' else move[3][1].lower()
        promo = move[2][-1] if move[2][-1] in 'QRBN' else '-'

        double_pawn = 1 if move[2] == 'ts' else 0
        enpassant = 1 if 'e.p.' in move[2] else 0
        castling = 1 if 'castling' in move[2] else 0

        # Can only know if it is capture if we get a gamestate as input
        if gamestate:
            capture = 1 if gamestate.board[move[1]] != '--' else 0
        else:
            capture = '-'

        print(
            f'{from_sq}      {to_sq}      {piece}        {promo}         {capture}          {double_pawn}      {enpassant}        {castling}')


# Print an easy board rep from list
def print_board_list(board):
    for row in range(12):
        print(board[10*row:10+10*row])


# Prints the entire board given the 12 piece bitboards
def print_board(board):

    # Initialise a board list and occupied squares
    dot = u'\xc2\xb7'[1]
    new_board = [dot]*64

    # Get occupied squares for each piece type and put in the board list
    for square in s.real_board_squares:
        color, p = board[square][0], board[square][1]
        piece = p.upper() if color == 'w' else p.lower()

        if piece != '-':
            new_board[s.real_board_squares.index(square)] = piece

    # Print each row on a new line with 2 spaces in between for readability.
    print('\n')
    print('    -  -  -  -  -  -  -  -')
    for row in range(9):

        # Print the board itself along with the numbers on the left
        if row != 8:
            board_row = new_board[row * 8:8 + row * 8]
            print(f'{s.numbers[7 - row]} | {"  ".join(board_row)} |')

        # Print letters at the bottom of the board
        else:
            print('    -  -  -  -  -  -  -  -')
            print(f'    {s.letters[0]}  {s.letters[1]}  {s.letters[2]}  {s.letters[3]}  {s.letters[4]}  {s.letters[5]}  {s.letters[6]}  {s.letters[7]}')
    print('\n')
