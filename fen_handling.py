# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                     fen_handling.py
#
#                   - Tests if a Fen string is valid
#                   - Converts between FEN-Gamestate and Gamestate-FEN
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

import settings as s

import numpy as np
import math


def run_fen_to_board(fen):
    correct_fen = test_fen(fen)
    if not correct_fen:
        print('Incorrect FEN format, please chose a valid FEN')
        return None
    else:
        return fen_to_board(fen)


def test_fen(fen):

    # Test if a value is given at all
    if not fen:
        return False

    # Test if there are 1 king each on the board
    if fen.split(' ')[0].count('k') + fen.split(' ')[0].count('K') != 2:
        return False

    # Test board representation
    fen_board = fen.split(' ')[0]
    number = 0
    for item in fen_board:
        if item.isdigit():
            number = number + int(item)        
        elif item in 'pnbrqkPNBRQK':
            number += 1         
        elif item == '/':
            if number != 8:
                return False
            number = 0       
        else:
            return False

    # Test turn to move
    try:
        if fen.split(' ')[1] not in 'wb':
            return False
    except:
        return False

    # Test castling rights
    try:
        rights = fen.split(' ')[2]
        if not 0 < len(rights) <= 4:
            return False
        for right in rights:
            if right not in 'KQkq-':
                return False
    except:
        return False

    # Test enpassant square
    try:
        ep_square = fen.split(' ')[3]
        if not ep_square:
            return False
        if ep_square[0] not in '-abcdefgh':
            return False
        if len(ep_square) == 2:
            if ep_square[1] not in '3, 6':
                return False
        if len(ep_square) > 2:
            return False
    except:
        return False
        
    # If all conditions are good, return True
    return True


def fen_to_board(fen):

    # Split fen into parts
    fen = fen.split()

    # Init variables
    halfmove_counter = move_counter = 0

    # Turn to move
    is_white_turn = True if fen[1] == 'w' else False

    # Castling rights
    castling_rights = np.uint8(0)
    castling = fen[2]
    if 'K' in castling:
        castling_rights |= s.castling_numbers['wk']
    if 'Q' in castling:
        castling_rights |= s.castling_numbers['wq']
    if 'k' in castling:
        castling_rights |= s.castling_numbers['bk']
    if 'q' in castling:
        castling_rights |= s.castling_numbers['bq']

    # Enpassant square
    if fen[3] != '-':
        ep_square = s.board_to_square[fen[3]]
    else:
        ep_square = None

    # Find halfmove and move counter.
    # If black to move, the move counter should increase after next move, hence the '+ 0.5'
    if fen[-1][0].isnumeric():
        halfmove_counter = int(fen[4])
        if is_white_turn:
            move_counter = int(fen[5])
        else:
            move_counter = int(fen[5]) + 0.5

    # Init the board
    board = {}
    for square in range(120):
        if square in s.real_board_squares:
            board[square] = '--'
        else:
            board[square] = 'FF'

    # Extract the board representation and remove dashes
    fen_board_temp = fen[0]
    fen_board = fen_board_temp.replace('/', '')

    # Loop through the board representation
    number = 0
    for item in fen_board:

        # If it is a number, go corresponding numbers ahead in squares
        if item.isdigit():
            number = number + int(item)
        else:
            square = s.real_board_squares[number]
            color = 'w' if item.isupper() else 'b'
            board_item = item.lower() if item in 'pP' else item.upper()
            board[square] = f'{color}{board_item}'
            number += 1

    return board, castling_rights, ep_square, is_white_turn, halfmove_counter, move_counter


def gamestate_to_fen(gamestate):

    # Go through board to find where all the pieces are located
    fen = ''
    number = 0
    temp_number = 0
    for square in gamestate.board:
        piece = gamestate.board[square]
        fen_item = piece[1].upper() if piece[0] == 'w' else piece[1].lower()
        if piece != 'FF':
            if piece == '--':
                temp_number += 1
                number += 1
            else:
                if temp_number:
                    fen += str(temp_number)
                    temp_number = 0
                fen += fen_item
                number += 1
            if number == 8:
                if temp_number:
                    fen += str(temp_number)
                fen += '/'
                number = temp_number = 0
                
    # Remove last '/'
    fen = fen[:-1]

    # Turn to move
    fen += ' w' if gamestate.is_white_turn else ' b'

    # Castling rights
    fen += s.cr_to_fen[gamestate.castling_rights]

    # Enpassant square
    if not gamestate.enpassant_square:
        fen += ' -'
    else:
        fen += ' ' + s.square_to_board[gamestate.enpassant_square]
                
    # Half move clock
    fen += f' {gamestate.halfmove_counter}'

    # Move counter
    fen += f' {math.floor(gamestate.move_counter)}'
            
    return fen
