# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                          evaluation.py
#
#                   - Static evaluation on the gamestate input
#                   - Base piece values and PST evaluation
#                   - Possibility to add other bonuses which are currently commented out
#                   - Special late endgame logic to find common mate patterns
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

import settings as s
import evaluation_settings as es


def evaluate(gamestate):


    # Piece values with base and piece-dependent values (updated in make/unmake move functions)
    # Interpolated between mid and endgame.
    score_opening = gamestate.piece_values[0] - gamestate.piece_values[1]
    score_endgame = gamestate.piece_values[2] - gamestate.piece_values[3]
    score = ((score_opening * gamestate.game_phase_score) + (score_endgame*(es.opening_phase_score - gamestate.game_phase_score))) // es.opening_phase_score

    '''# Bishop pair bonus
    if gamestate.piece_dict[0]['B'] == 2:
        white_score += es.bishop_pair_bonus
    if gamestate.piece_dict[1]['B'] == 2:
        black_score += es.bishop_pair_bonus'''


# -------------------------------------------------------------------------------------------------
#                                  Endgame related functions
# -------------------------------------------------------------------------------------------------

    if gamestate.game_phase_score <= es.endgame_phase_score*2:

        '''# Knights better with lots of pawns, bishops worse. Rooks better with less pawns.
        score += ((gamestate.piece_dict[0]['N'] * gamestate.piece_dict[0]['p']) -
                  (gamestate.piece_dict[1]['N'] * gamestate.piece_dict[1]['p'])) * es.knight_pawn_bonus

        score += ((gamestate.piece_dict[0]['B'] * gamestate.piece_dict[0]['p']) -
                 (gamestate.piece_dict[1]['B'] * gamestate.piece_dict[1]['p'])) * es.bishop_pawn_punishment

        score += ((gamestate.piece_dict[0]['R'] * gamestate.piece_dict[0]['p']) -
                  (gamestate.piece_dict[1]['R'] * gamestate.piece_dict[1]['p'])) * es.rook_pawn_punishment'''

        # Finding mate with no pawns on the board without syzygy. Don't work for KNB vs K yet.
        if gamestate.piece_dict[0]['p'] == gamestate.piece_dict[1]['p'] == 0:

            # Add a small term for piece values, otherwise it sometimes sacrificed a piece for no reason.
            score = 0.5*gamestate.piece_values[2] - 0.5*gamestate.piece_values[3]

            # White advantage (no rooks or queens on enemy side and a winning advantage)
            if gamestate.piece_dict[1]['R'] == gamestate.piece_dict[1]['Q'] == 0 and score > 0:

                # Lone K vs K and (R, Q and/or at least 2xB). Only using mop-up evaluation (https://www.chessprogramming.org/Mop-up_Evaluation).
                if gamestate.piece_dict[0]['R'] >= 1 or gamestate.piece_dict[0]['Q'] >= 1 or gamestate.piece_dict[0]['B'] >= 2:
                    black_king_real_pos = es.real_board_squares.index(gamestate.king_location[1])
                    score += 10 * (4.7 * es.manhattan_distance[black_king_real_pos] + 1.6 * (14 - gamestate.kings_distance))

                # Lone K vs K, N and B (NOT COMPLETED YET)
                if gamestate.piece_dict[0]['R'] == gamestate.piece_dict[0]['Q'] == 0 and gamestate.piece_dict[0]['B'] >= 1 and gamestate.piece_dict[0]['N'] >= 1:
                    pass

            # Black advantage (no rooks or queens on enemy side and a winning advantage)
            if gamestate.piece_dict[0]['R'] == gamestate.piece_dict[0]['Q'] == 0 and score < 0:

                # Lone K vs K and (R, Q and/or at least 2xB). Only using mop-up evaluation (https://www.chessprogramming.org/Mop-up_Evaluation).
                if gamestate.piece_dict[1]['R'] >= 1 or gamestate.piece_dict[1]['Q'] >= 1 or gamestate.piece_dict[1]['B'] >= 2:
                    white_king_real_pos = es.real_board_squares.index(gamestate.king_location[0])
                    score -= 10 * (4.7 * es.manhattan_distance[white_king_real_pos] + 1.6 * (14 - gamestate.kings_distance))

                # Lone K vs K, N and B (NOT COMPLETED YET)
                if gamestate.piece_dict[1]['R'] == gamestate.piece_dict[1]['Q'] == 0 and gamestate.piece_dict[1]['B'] >= 1 and gamestate.piece_dict[1]['N'] >= 1:
                    pass

    return score if gamestate.is_white_turn else -score
