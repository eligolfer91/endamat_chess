# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                          gui_main.py
#
#                   - Handle user input in the main Pygame loop (if playing with own GUI)
#                   - Draws everything (board + pieces, buttons, engine output)
#                   - Highlighting valid moves, latest move and checks
#                   - Keeps track of game over (checkmate and stalemate)
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

# Import from one step above in case of running through simpler IDE such as IDLE
import os
import sys
up1 = os.path.abspath('..')
sys.path.insert(0, up1)

import gamestate as gs
import settings as s
from ai import Ai
import fen_handling as fh
from gui.gui_theme import Theme
from gui.gui_popup import Popup

import time
import pyperclip
import math
import cProfile
import ctypes
import pygame
from pygame.locals import HWSURFACE, DOUBLEBUF, RESIZABLE, VIDEORESIZE


# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                            GUI class
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

class Gui:

    def __init__(self):

        # Initialize GUI theme
        self.current_theme = 'Black and Gold'
        self.theme = Theme()
        self.theme.get_theme(self.current_theme)

        # General
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        pygame.display.set_caption(' Chess')
        pygame.display.set_icon(self.theme.icon)

        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.theme.win_width, self.theme.win_height), HWSURFACE | DOUBLEBUF | RESIZABLE)

        # Game parameters
        self.start_fen = self.current_fen = self.theme.start_fen

        # Initialize to be able to draw GUI before game starts
        self.gamestate = gs.GameState(self.start_fen)
        self.ai = Ai(self.gamestate, search_depth=4)

        # Moves
        self.moves_made = []
        self.latest_move = [(-100, -100, '')]

        # Keep track of mouse button presses and mouse movements
        self.is_dragging = False
        self.square_under_mouse = 0
        self.x, self.y = 0, 0
        self.selected_square = 0

        # Initiate initial gamestate variables
        self.running = True
        self.playing = False

        self.is_flipped = False
        self.game_mode = 'ai'

        # Initiate Gamestate, search and AI
        self.gamestate = gs.GameState(self.start_fen)
        self.ai = Ai(self.gamestate)

        # Flip board if AI is playing as white
        self.is_flipped = False

        # Flag for when a move is made by the human player
        self.is_ai_turn = False
        self.is_ai_white = False

# ---------------------------------------------------------------------------------------------------------

        # Menu item colors
        self.filemenu_button_color = self.theme.grey[0]
        self.positionmenu_button_color = self.theme.grey[0]
        self.gamemenu_button_color = self.theme.grey[0]
        self.boardmenu_button_color = self.theme.grey[0]

        self.menu_items_color = self.theme.grey_t[0]

        # Menu items
        self.chosen_menu_rect = pygame.Rect(-5, -5, -5, -5)

        # Menu items clicked?
        self.filemenu_active = self.positionmenu_active = self.gamemenu_active = self.boardmenu_active = False

        # Init drop down areas
        self.filemenu_dropdown_area = pygame.Rect(-5, -5, -5, -5)
        self.positionmenu_dropdown_area = pygame.Rect(-5, -5, -5, -5)
        self.gamemenu_dropdown_area = pygame.Rect(-5, -5, -5, -5)
        self.boardmenu_dropdown_area = pygame.Rect(-5, -5, -5, -5)

        self.filemenu_item_rects = [pygame.Rect(-5, -5, -5, -5)] * 3
        self.positionmenu_item_rects = [pygame.Rect(-5, -5, -5, -5)] * 2
        self.gamemenu_item_rects = [pygame.Rect(-5, -5, -5, -5)] * 3
        self.boardmenu_item_rects = [pygame.Rect(-5, -5, -5, -5)] * 4

        self.menu_bar_area = pygame.Rect(0, 0, self.theme.win_width, self.theme.top_bar_height)

# ---------------------------------------------------------------------------------------------------------

        # Keep track of game times
        self.white_time = self.black_time = self.theme.tot_time
        self.move_time_white = self.move_time_black = 0
        self.time_log = [(self.white_time, self.black_time, self.move_time_white, self.move_time_black)]
        self.paused = False

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                     Main game loop
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    def main(self):

        # Frames per look
        fps = 60

        while self.running:

            self.draw()

            self.clock.tick(fps)

            self.square_under_mouse, col, row = self.get_square_under_mouse()

            # Get user time left when game starts (user makes first move)
            if self.moves_made and self.playing and not self.paused:

                # Reduce time each iteration with some compensation for lag/drawing functions
                if not self.theme.fixed_depth and not self.theme.movetime:
                    if self.gamestate.is_white_turn:
                        if self.white_time:
                            self.white_time -= (1/fps - 0.01/fps)
                        self.move_time_white += (1 / fps - 0.01 / fps)
                    else:
                        if self.black_time:
                            self.black_time -= (1/fps - 0.01/fps)
                        self.move_time_black += (1/fps - 0.01/fps)

            # Events happening in GUI
            for event in pygame.event.get():

                # Change window size, limit to a certain ratio
                if event.type == VIDEORESIZE:

                    # Limit the window size
                    win_width = min(max(event.size[0], 800), 1000)

                    # Update theme with new variables
                    self.theme.get_theme(self.current_theme, win_width=win_width)

                    # Update screen
                    self.screen = pygame.display.set_mode((self.theme.win_width, self.theme.win_height), HWSURFACE | DOUBLEBUF | RESIZABLE)

                # Get mouse position
                pos = pygame.mouse.get_pos()

                # -----------------------------------------------------
                #                   Mouse hovering
                # -----------------------------------------------------

                # File menu button
                if self.file_button.collidepoint(pos):
                    self.filemenu_active = True
                    self.filemenu_button_color = self.theme.grey[1]
                else:
                    self.filemenu_button_color = self.theme.grey[0]
                if not self.filemenu_dropdown_area.collidepoint(pos) and not self.file_button.collidepoint(pos):
                    self.filemenu_active = False

                # Position menu button
                if self.position_button.collidepoint(pos):
                    self.positionmenu_active = True
                    self.positionmenu_button_color = self.theme.grey[1]
                else:
                    self.positionmenu_button_color = self.theme.grey[0]
                if not self.positionmenu_dropdown_area.collidepoint(pos) and not self.position_button.collidepoint(pos):
                    self.positionmenu_active = False

                # Game menu button
                if self.game_button.collidepoint(pos):
                    self.gamemenu_active = True
                    self.gamemenu_button_color = self.theme.grey[1]
                else:
                    self.gamemenu_button_color = self.theme.grey[0]
                if not self.gamemenu_dropdown_area.collidepoint(pos) and not self.game_button.collidepoint(pos):
                    self.gamemenu_active = False

                # Board menu button
                if self.boardmenu_button.collidepoint(pos):
                    self.boardmenu_active = True
                    self.boardmenu_button_color = self.theme.grey[1]
                else:
                    self.boardmenu_button_color = self.theme.grey[0]
                if not self.boardmenu_dropdown_area.collidepoint(pos) and not self.boardmenu_button.collidepoint(pos):
                    self.boardmenu_active = False

                # All dropdown areas
                rectangle_areas = [self.filemenu_item_rects, self.positionmenu_item_rects, self.gamemenu_item_rects, self.boardmenu_item_rects]
                for rectangles in rectangle_areas:
                    active_windows = [self.filemenu_active, self.positionmenu_active, self.gamemenu_active, self.boardmenu_active]
                    for rectangle in rectangles:
                        if rectangle.collidepoint(pos) and active_windows[rectangle_areas.index(rectangles)]:
                            self.chosen_menu_rect = rectangle

                # -----------------------------------------------------
                #               Mouse button down events
                # -----------------------------------------------------
                if event.type == pygame.MOUSEBUTTONDOWN:

                    if event.button == 1 and not any([self.filemenu_active, self.positionmenu_active, self.gamemenu_active, self.boardmenu_active]):
                        self.is_dragging = True
                        if 1 <= col <= 8 and 2 <= row <= 9 and self.gamestate.board[self.square_under_mouse][0] == ('w' if self.gamestate.is_white_turn else 'b'):
                            self.selected_square = self.square_under_mouse
                        else:
                            self.selected_square = 0
                        self.x, self.y = pygame.mouse.get_pos()[0] - self.theme.sq_size // 2, pygame.mouse.get_pos()[1] - self.theme.sq_size // 2

                    # -----------------------------------------------------
                    #                 GUI button clicks
                    # -----------------------------------------------------
                    if self.undo_button.collidepoint(pos):
                        self.unmake_a_move()

                    elif self.fen_button.collidepoint(pos):
                        pyperclip.copy(self.current_fen)

                    elif self.newgame_button.collidepoint(pos):
                        self.running = False
                        Gui().main()

                    elif self.flip_button.collidepoint(pos):
                        self.is_flipped = not self.is_flipped

                    # -----------------------------------------------------
                    #                 Menu item clicks
                    # -----------------------------------------------------

                    # New game
                    if self.filemenu_item_rects[0].collidepoint(pos) and self.filemenu_active:
                        self.filemenu_active = False
                        self.init_game()

                    # Options
                    if self.filemenu_item_rects[1].collidepoint(pos) and self.filemenu_active:
                        self.filemenu_active = False
                        self.draw()
                        self.draw_highlighting(self.theme.grey_t[4], self.theme.grey_t[4], 0, 0, self.theme.win_width, self.theme.win_height, edge=False)

                        Popup(self.screen, pygame.Surface.copy(self.screen), self.theme).get_options_menu()

                    # Exit
                    elif self.filemenu_item_rects[2].collidepoint(pos) and self.filemenu_active:
                        pygame.quit()
                        self.running = False

                    # Set up position
                    elif self.positionmenu_item_rects[0].collidepoint(pos) and self.positionmenu_active:
                        self.positionmenu_active = False
                        self.draw()
                        self.draw_highlighting(self.theme.grey_t[4], self.theme.grey_t[4], 0, 0, self.theme.win_width, self.theme.win_height, edge=False)

                        Popup(self.screen, pygame.Surface.copy(self.screen), self.theme).set_up_position()
                        self.init_game()
                        self.gamestate = gs.GameState(self.theme.start_fen)

                        self.is_ai_white = False if self.gamestate.is_white_turn else True
                        self.is_flipped = True if self.is_ai_white else False

                    # Copy FEN string to clipboard
                    elif self.positionmenu_item_rects[1].collidepoint(pos) and self.positionmenu_active:
                        pyperclip.copy(self.current_fen)
                        self.positionmenu_active = False

                    # Chose to play vs human or AI
                    elif self.gamemenu_item_rects[0].collidepoint(pos) and self.gamemenu_active:
                        self.game_mode = 'ai' if self.game_mode == 'human' else 'human'
                        self.ai.print_info = {}
                        self.gamemenu_active = False

                    # Chose to play as white or black
                    elif self.gamemenu_item_rects[1].collidepoint(pos) and self.gamemenu_active:
                        self.is_ai_white = not self.is_ai_white
                        self.is_flipped = True if self.is_ai_white else False
                        self.is_ai_turn = self.is_ai_white if self.gamestate.is_white_turn else not self.is_ai_white
                        self.playing = self.is_ai_turn
                        self.gamemenu_active = False

                    # Chose time control when playing vs AI
                    elif self.gamemenu_item_rects[2].collidepoint(pos) and self.gamemenu_active:
                        self.gamemenu_active = False
                        self.draw()
                        self.draw_highlighting(self.theme.grey_t[4], self.theme.grey_t[4], 0, 0, self.theme.win_width, self.theme.win_height, edge=False)
                        Popup(self.screen, pygame.Surface.copy(self.screen), self.theme).chose_time_control()

                        self.white_time = self.black_time = self.theme.tot_time
                        self.time_log = [(self.white_time, self.black_time, 0, 0)]

                        # If started, restart game with new time control
                        if self.playing:
                            self.init_game()

                    # Flip board
                    elif self.boardmenu_item_rects[0].collidepoint(pos) and self.boardmenu_active:
                        self.is_flipped = not self.is_flipped
                        self.boardmenu_active = False

                    # Undo a move
                    elif self.boardmenu_item_rects[1].collidepoint(pos) and self.boardmenu_active:
                        self.unmake_a_move()
                        self.boardmenu_active = False

                    # CHANGE THEME
                    # Black and Gold
                    elif self.boardmenu_item_rects[2].collidepoint(pos) and self.boardmenu_active:
                        self.current_theme = 'Black and Gold'
                        self.theme.get_theme(self.current_theme, win_width=self.theme.win_width)
                        self.boardmenu_active = False

                    # Blue and White
                    elif self.boardmenu_item_rects[3].collidepoint(pos) and self.boardmenu_active:
                        self.current_theme = 'Blue and White'
                        self.theme.get_theme(self.current_theme, win_width=self.theme.win_width)
                        self.boardmenu_active = False

                # -----------------------------------------------------
                #               Mouse button up events
                # -----------------------------------------------------
                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.is_dragging = False
                        move = (self.selected_square, self.get_square_under_mouse()[0])
                        for possible_move in self.gamestate.get_valid_moves():

                            # Promotion moves
                            if move == (possible_move[0], possible_move[1]) and possible_move[2] in 'pQpRpBpN':

                                # Get promotion move
                                self.draw()
                                self.draw_highlighting(self.theme.grey_t[4], self.theme.grey_t[4], 0, 0, self.theme.win_width, self.theme.win_height, edge=False)
                                promotion_move = Popup(self.screen, pygame.Surface.copy(self.screen), self.theme).get_promotion(possible_move, ('wp' if self.gamestate.is_white_turn else 'bp'))

                                # Make the move
                                self.process_move(promotion_move)
                                break

                            # None promotional moves moves
                            elif move == (possible_move[0], possible_move[1]) and possible_move[2] not in 'pQpRpBpN':

                                # Make the move
                                self.process_move(possible_move)
                                break

                # -----------------------------------------------------
                #               Mouse motion events
                # -----------------------------------------------------
                elif event.type == pygame.MOUSEMOTION:
                    if self.is_dragging:
                        self.x, self.y = pygame.mouse.get_pos()[0] - self.theme.sq_size // 2, pygame.mouse.get_pos()[1] - self.theme.sq_size // 2

                # -----------------------------------------------------
                #       Keyboard events (if option is enabled)
                # -----------------------------------------------------
                elif event.type == pygame.KEYDOWN:
                    if self.theme.enable_shortcuts:

                        # Unmake move by pressing 'z'-key
                        if event.key == pygame.K_z:
                            self.unmake_a_move()

                        # New game with 'n'-key
                        elif event.key == pygame.K_n:
                            self.init_game()

                        # Flip screen with 'f'-key
                        elif event.key == pygame.K_f:
                            self.is_flipped = not self.is_flipped

                        # Copy current fen string with 'c'-key
                        elif event.key == pygame.K_c:
                            pyperclip.copy(self.current_fen)

                        # Pause time with 'p'-key
                        elif event.key == pygame.K_p:
                            self.paused = not self.paused

                # -----------------------------------------------------
                #       Quit GUI by pressing the window 'X' icon
                # -----------------------------------------------------
                if event.type == pygame.QUIT:
                    pygame.quit()
                    self.running = False

            # -----------------------------------------------------
            #                 Draw GUI in each loop
            # -----------------------------------------------------

            # Draw the screen after human move if we are still running the game
            if self.running:
                self.draw()

            # -----------------------------------------------------
            #                  Check for game over
            # -----------------------------------------------------

            # Check if stalemated/checkmated and stop the game if so
            game_status = self.check_for_gameover()
            if game_status and self.playing:
                self.draw()
                self.draw_highlighting(self.theme.grey_t[4], self.theme.grey_t[4], 0, 0, self.theme.win_width, self.theme.win_height, edge=False)
                play_again = Popup(self.screen, pygame.Surface.copy(self.screen), self.theme).gameover_screen(game_status)

                if play_again:
                    self.init_game()
                else:
                    self.ai.print_info = {}
                    self.playing = False

            # -----------------------------------------------------
            #                     AI make move
            # -----------------------------------------------------

            # If move made and game not over, change to AI if that option is chosen.
            if (self.is_ai_turn, self.running, self.game_mode, self.playing) == (True, True, 'ai', True):
                move, score = self.ai_make_a_move()
                self.process_move(move)

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                    Draw everything in the GUI
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    # Collection of all drawing actions going on
    def draw(self):

        # Background
        self.screen.blit(self.theme.bg, (0, 0))

        # Top menu bar
        self.draw_menu()

        # Board edge and the board itself
        self.screen.blit(self.theme.board_edge, (self.theme.board_offset - 4, self.theme.board_offset + self.theme.top_bar_height - 4))
        self.draw_board()

        # AI area at the bottom
        self.draw_ai()

        # Buttons
        self.draw_buttons()

        # Time left
        self.draw_time()

        # Draw drop down menus
        self.draw_drop_down()

        # Update screen
        pygame.display.flip()

    # Draw the AI info at the bottom
    def draw_ai(self):

        # Background
        self.screen.blit(self.theme.pv_edge, (self.theme.board_offset - 4, 8 * self.theme.sq_size + self.theme.board_offset + 0.5 * self.theme.sq_size + self.theme.top_bar_height))
        self.screen.blit(self.theme.pv_image, (self.theme.board_offset, 8 * self.theme.sq_size + self.theme.board_offset + 0.5 * self.theme.sq_size + self.theme.top_bar_height + 4))

        # Start coordinates for the text and lines
        start_x = self.theme.board_offset
        start_y = 8 * self.theme.sq_size + self.theme.board_offset + self.theme.top_bar_height + 0.5 * self.theme.sq_size

        start_line = start_y + 2*self.theme.margin
        end_line = start_y + self.theme.pv_height - 2*self.theme.margin - 1

        # Title text (Depth, time, nodes, (nodes/s), score, PV-line)
        self.create_text('Depth', self.theme.pv_font, self.theme.black, start_x + 0.32 * self.theme.sq_size, start_y + 0.2 * self.theme.sq_size, 'center')
        pygame.draw.line(self.screen, self.theme.black, (start_x + 0.65 * self.theme.sq_size, start_line), (start_x + 0.65 * self.theme.sq_size, end_line))

        self.create_text('Time', self.theme.pv_font, self.theme.black, start_x + 1 * self.theme.sq_size, start_y + 0.2 * self.theme.sq_size, 'center')
        pygame.draw.line(self.screen, self.theme.black, (start_x + 1.35 * self.theme.sq_size, start_line), (start_x + 1.35 * self.theme.sq_size, end_line))

        self.create_text('Nodes', self.theme.pv_font, self.theme.black, start_x + 1.78 * self.theme.sq_size, start_y + 0.2 * self.theme.sq_size, 'center')
        pygame.draw.line(self.screen, self.theme.black, (start_x + 2.2 * self.theme.sq_size, start_line), (start_x + 2.2 * self.theme.sq_size, end_line))

        self.create_text('Nodes/s', self.theme.pv_font, self.theme.black, start_x + 2.65 * self.theme.sq_size, start_y + 0.2 * self.theme.sq_size, 'center')
        pygame.draw.line(self.screen, self.theme.black, (start_x + 3.1 * self.theme.sq_size, start_line), (start_x + 3.1 * self.theme.sq_size, end_line))

        self.create_text('Score', self.theme.pv_font, self.theme.black, start_x + 3.5 * self.theme.sq_size, start_y + 0.2 * self.theme.sq_size, 'center')
        pygame.draw.line(self.screen, self.theme.black, (start_x + 3.85 * self.theme.sq_size, start_line), (start_x + 3.85 * self.theme.sq_size, end_line))

        self.create_text('Main line', self.theme.pv_font, self.theme.black, start_x + 4 * self.theme.sq_size, start_y + 0.2 * self.theme.sq_size, 'left')

        pygame.draw.line(self.screen, self.theme.black, (self.theme.board_offset, start_y + 4*self.theme.margin + self.theme.pv_font.get_height()), (self.theme.win_width - self.theme.board_offset - 1, start_y + 4*self.theme.margin + self.theme.pv_font.get_height()))

        # Draw AI info if game has started and AI has info to provide
        if self.ai.pv_line:
            # Draw PV info (Depth, time, nodes, (nodes/s), score, PV-line)
            start_y += 0.27 * self.theme.sq_size
            length = len(self.ai.print_info)
            for items, depth in enumerate(reversed(range(length))):

                # Break to fit the text in the gui vertically
                if items >= 6:
                    break

                # Break fit the text in the gui horizontally
                if len(self.ai.print_info[depth]['main_line'].split()) >= 9:
                    self.ai.print_info[depth]['main_line'] = ' '.join(self.ai.print_info[depth]['main_line'].split()[0:9]).rstrip(',')

                # If score is large enough, make it maximum a mate score and find how many moves we are from mating
                score = self.ai.print_info[depth]['score']
                if -self.ai.mate_value <= score <= -self.ai.mate_score:
                    length_to_mate = math.ceil(len(self.ai.print_info[depth]['main_line'].split()) / 2)
                    score_text = f'-M{length_to_mate:.0f}'
                elif self.ai.mate_score <= score <= self.ai.mate_value:
                    length_to_mate = math.ceil(len(self.ai.print_info[depth]['main_line'].split()) / 2)
                    score_text = f'M{length_to_mate:.0f}'
                else:
                    score_text = f'{score / 100:.2f}'

                self.create_text(self.ai.print_info[depth]['depth'], self.theme.pv_font, self.theme.black, start_x + 0.32 * self.theme.sq_size, start_y + 0.21 * self.theme.sq_size * (length - depth), 'center')
                self.create_text(self.ai.print_info[depth]['time'], self.theme.pv_font, self.theme.black, start_x + 1.3 * self.theme.sq_size, start_y + 0.21 * self.theme.sq_size * (length - depth), 'right')
                self.create_text(f'{self.ai.print_info[depth]["nodes"]}', self.theme.pv_font, self.theme.black, start_x + 2.16 * self.theme.sq_size, start_y + 0.21 * self.theme.sq_size * (length - depth), 'right')
                self.create_text(f'{self.ai.print_info[depth]["nodes_s"]}', self.theme.pv_font, self.theme.black, start_x + 3 * self.theme.sq_size, start_y + 0.21 * self.theme.sq_size * (length - depth), 'right')
                self.create_text(score_text, self.theme.pv_font, self.theme.black, start_x + 3.79 * self.theme.sq_size, start_y + 0.21 * self.theme.sq_size * (length - depth), 'right')
                self.create_text(self.ai.print_info[depth]['main_line'], self.theme.pv_font, self.theme.black, start_x + 4 * self.theme.sq_size, start_y + 0.21 * self.theme.sq_size * (length - depth), 'left')

    # Draws the chess board with pieces
    def draw_board(self):

        # Letters and numbers
        for char in range(8):
            real_char = 7 - char if self.is_flipped else char
            self.create_text(s.letters[char], self.theme.board_font, self.theme.board_text_color, self.theme.board_offset + 0.5*self.theme.sq_size + real_char*self.theme.sq_size, 8 * self.theme.sq_size + self.theme.sq_size - self.theme.board_offset + int(self.theme.sq_size/16.25) + self.theme.top_bar_height, 'center')
            self.create_text(s.numbers[::-1][char], self.theme.board_font, self.theme.board_text_color, 0.5*self.theme.board_offset - int(self.theme.sq_size/32.5), self.theme.board_offset + 0.5*self.theme.sq_size + self.theme.sq_size*real_char + self.theme.top_bar_height, 'center')

        # Board
        self.draw_squares()

        # Highlight squares
        self.highlight_squares()

        # Pieces
        self.draw_pieces()

        # Draw dragged piece
        if self.is_dragging and self.gamestate.board[self.selected_square] not in ('--', 'FF'):
            piece = self.gamestate.board[self.selected_square]
            self.screen.blit(self.theme.piece_images[piece], pygame.Rect(self.x, self.y, self.theme.sq_size, self.theme.sq_size))

    # Draw the squares
    def draw_squares(self):
        real_square = 0
        for row in range(12):
            for col in range(10):
                if 2 <= row <= 9 and 1 <= col <= 8:
                    x, y, w = (self.theme.sq_size * (col - 1) + self.theme.board_offset, self.theme.sq_size * (row - 2) + self.theme.board_offset + self.theme.top_bar_height, self.theme.sq_size) if not self.is_flipped \
                        else (self.theme.sq_size * (8 - col) + self.theme.board_offset, self.theme.sq_size * (9 - row) + self.theme.board_offset + self.theme.top_bar_height, self.theme.sq_size)

                    # Squares
                    square = self.theme.dark_square[real_square] if (row + col) % 2 == 0 else self.theme.light_square[real_square]
                    self.screen.blit(square, pygame.Rect(x, y, w, w))
                    real_square += 1

    # Draw the pieces
    def draw_pieces(self):

        for row in range(12):
            for col in range(10):
                if 2 <= row <= 9 and 1 <= col <= 8:
                    x, y, w = (self.theme.sq_size * (col - 1) + self.theme.board_offset, self.theme.sq_size * (row - 2) + self.theme.board_offset + self.theme.top_bar_height, self.theme.sq_size) if not self.is_flipped \
                        else (self.theme.sq_size * (8 - col) + self.theme.board_offset, self.theme.sq_size * (9 - row) + self.theme.board_offset + self.theme.top_bar_height, self.theme.sq_size)

                    piece = self.gamestate.board[row * 10 + col]
                    if piece != '--' and (row * 10 + col != self.selected_square or not self.is_dragging):
                        self.screen.blit(self.theme.piece_images[piece], pygame.Rect(x, y, w, w))

    # Highlight square when in check, latest move, selected square and its possible moves
    def highlight_squares(self):

        # Highlight if king is in check
        king_pos = self.gamestate.king_location[not self.gamestate.is_white_turn]
        if self.gamestate.check_for_checks(king_pos):
            row, col = (king_pos // 10 - 2, king_pos % 10 - 1) if not self.is_flipped else (9 - king_pos // 10, 8 - king_pos % 10)
            self.draw_highlighting(self.theme.check_red, self.theme.check_red_t, col * self.theme.sq_size + self.theme.board_offset,
                                   row * self.theme.sq_size + self.theme.board_offset + self.theme.top_bar_height,
                                   self.theme.sq_size, self.theme.sq_size, thickness=1)

        # Highlight latest move
        start_row, start_col = (self.latest_move[-1][0] // 10 - 2, self.latest_move[-1][0] % 10 - 1) if not self.is_flipped else \
                               (9 - self.latest_move[-1][0] // 10, 8 - self.latest_move[-1][0] % 10)
        end_row, end_col = (self.latest_move[-1][1] // 10 - 2, self.latest_move[-1][1] % 10 - 1) if not self.is_flipped else \
                           (9 - self.latest_move[-1][1] // 10, 8 - self.latest_move[-1][1] % 10)
        self.draw_highlighting(self.theme.light_blue, self.theme.blue_t, start_col * self.theme.sq_size + self.theme.board_offset, start_row * self.theme.sq_size + self.theme.board_offset + self.theme.top_bar_height,
                               self.theme.sq_size, self.theme.sq_size, thickness=1)
        self.draw_highlighting(self.theme.light_blue, self.theme.blue_t, end_col * self.theme.sq_size + self.theme.board_offset, end_row * self.theme.sq_size + self.theme.board_offset + self.theme.top_bar_height,
                               self.theme.sq_size, self.theme.sq_size, thickness=1)

        # Highlight when dragging a piece
        if self.is_dragging:
            square = self.selected_square
            row, col = (square // 10 - 2, square % 10 - 1) if not self.is_flipped else \
                       (9 - square // 10, 8 - square % 10)

            # Selected square
            if self.gamestate.board[square][0] == ('w' if self.gamestate.is_white_turn else 'b'):
                self.draw_highlighting(self.theme.orange, self.theme.orange_t, col * self.theme.sq_size + self.theme.board_offset, row * self.theme.sq_size + self.theme.board_offset + self.theme.top_bar_height,
                                       self.theme.sq_size, self.theme.sq_size, thickness=1)

            # Possible moves
            valid_moves = self.gamestate.get_valid_moves()
            for move in valid_moves:
                if move[0] == square:
                    row, col = (move[1] // 10 - 2, move[1] % 10 - 1) if not self.is_flipped else \
                               (9 - move[1] // 10, 8 - move[1] % 10)
                    color = self.theme.green_t_promo if move[2] in 'pQpRpBpN' else self.theme.green_t
                    self.draw_highlighting(self.theme.green, color, col * self.theme.sq_size + self.theme.board_offset, row * self.theme.sq_size + self.theme.board_offset + self.theme.top_bar_height,
                                           self.theme.sq_size, self.theme.sq_size, thickness=1)

    # Draw all buttons on the screen
    def draw_buttons(self):

        height = 8 * self.theme.sq_size + self.theme.board_offset
        self.undo_button = self.create_buttons('Undo move', self.theme.button_font, self.theme.button_text_color, self.theme.win_width - self.theme.board_offset - self.theme.clock_width/2, height)
        height -= self.undo_button[3] + int(self.theme.sq_size/13)
        self.flip_button = self.create_buttons('Flip Board', self.theme.button_font, self.theme.button_text_color, self.theme.win_width - self.theme.board_offset - self.theme.clock_width/2, height)
        height -= self.flip_button[3] + int(self.theme.sq_size/13)
        self.fen_button = self.create_buttons('Copy FEN', self.theme.button_font, self.theme.button_text_color, self.theme.win_width - self.theme.board_offset - self.theme.clock_width/2, height)
        height -= self.fen_button[3] + int(self.theme.sq_size/13)
        self.newgame_button = self.create_buttons('New game', self.theme.button_font, self.theme.button_text_color, self.theme.win_width - self.theme.board_offset - self.theme.clock_width/2, height)

    # Draw the time left fields
    def draw_time(self):

        # Background
        self.screen.blit(self.theme.clock_edge, (8*self.theme.sq_size + 2*self.theme.board_offset, self.theme.board_offset + self.theme.top_bar_height - 2*self.theme.margin))
        self.screen.blit(self.theme.clock_image, (8*self.theme.sq_size + 2*self.theme.board_offset + 2*self.theme.margin, self.theme.board_offset + self.theme.top_bar_height))

        # Title text
        x_start, y_start = 8*self.theme.sq_size + 2*self.theme.board_offset, self.theme.board_offset + self.theme.top_bar_height

        self.create_text('White', self.theme.clock_title_font, self.theme.black, x_start + int(0.25*self.theme.clock_width), y_start + int(self.theme.sq_size/3.5), 'center')
        pygame.draw.line(self.screen, self.theme.black, (x_start + int(0.5*self.theme.clock_width), y_start), (x_start + int(0.5*self.theme.clock_width), y_start + self.theme.clock_height - 4*self.theme.margin - 1), 1)
        self.create_text('Black', self.theme.clock_title_font, self.theme.black, x_start + int(0.75*self.theme.clock_width), y_start + int(self.theme.sq_size/3.5), 'center')

        # Clocks
        mins, secs = divmod(self.white_time, 60)
        white_time = '{:02d}:{:02d}'.format(int(mins), int(secs))
        mins, secs = divmod(self.black_time, 60)
        black_time = '{:02d}:{:02d}'.format(int(mins), int(secs))

        self.create_text(white_time, self.theme.clock_font, self.theme.black, x_start + int(0.25*self.theme.clock_width), y_start + int(self.theme.sq_size/1.3), 'center')
        self.create_text(black_time, self.theme.clock_font, self.theme.black, x_start + int(0.75*self.theme.clock_width), y_start + int(self.theme.sq_size / 1.3), 'center')

        # Move time
        mins, secs = divmod(self.move_time_white, 60)
        white_time = '{:02d}:{:02d}'.format(int(mins), int(secs))
        mins, secs = divmod(self.move_time_black, 60)
        black_time = '{:02d}:{:02d}'.format(int(mins), int(secs))

        self.create_text(white_time, self.theme.clock_move_font, self.theme.black, x_start + int(0.25*self.theme.clock_width), y_start + int(self.theme.sq_size*1.12), 'center')
        self.create_text(black_time, self.theme.clock_move_font, self.theme.black, x_start + int(0.75*self.theme.clock_width), y_start + int(self.theme.sq_size*1.12), 'center')

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                  Draw and handle menu events
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    # Draw top bar
    def draw_menu(self):

        # Background
        pygame.draw.rect(self.screen, self.theme.grey[0], (0, 0, self.theme.win_width, self.theme.top_bar_height))

        # Menu items top level
        width = 6*self.theme.margin
        self.file_button = self.create_menu_items('File', self.filemenu_button_color, width, self.theme.top_bar_height / 2, int(self.theme.sq_size / 6.5), int(self.theme.sq_size / 3.25))
        width += self.file_button[2] - self.theme.margin
        self.position_button = self.create_menu_items('Position', self.positionmenu_button_color, width, self.theme.top_bar_height / 2, int(self.theme.sq_size / 13), int(self.theme.sq_size / 5.91))
        width += self.position_button[2] + self.theme.margin
        self.game_button = self.create_menu_items('Game', self.gamemenu_button_color, width, self.theme.top_bar_height / 2, int(self.theme.sq_size / 13), int(self.theme.sq_size / 7.222))
        width += self.game_button[2] + self.theme.margin
        self.boardmenu_button = self.create_menu_items('Board', self.boardmenu_button_color, width, self.theme.top_bar_height / 2, int(self.theme.sq_size / 13), int(self.theme.sq_size / 6.5))

    # Draw drop down menus if they are being clicked
    def draw_drop_down(self):

        if self.filemenu_active:
            self.filemenu_dropdown_area, self.filemenu_item_rects = self.draw_menu_drop_down(['New game', 'Options', 'Exit'], 0, self.theme.top_bar_height)
        elif self.positionmenu_active:
            self.positionmenu_dropdown_area, self.positionmenu_item_rects = self.draw_menu_drop_down(['Set up position', 'Copy FEN to clipboard'], self.file_button[2] + int(self.theme.sq_size / 10.83), self.theme.top_bar_height)
        elif self.gamemenu_active:
            opponent = 'AI' if self.game_mode == 'human' else 'another human'
            if self.game_mode == 'ai':
                pick_color = 'White' if self.is_ai_white else 'Black'
                self.gamemenu_dropdown_area, self.gamemenu_item_rects = self.draw_menu_drop_down([f'Play vs {opponent}', f'Play as {pick_color}', 'Time control'], self.file_button[2] + self.position_button[2] + int(self.theme.sq_size / 8.125), self.theme.top_bar_height)
            else:
                self.gamemenu_dropdown_area, self.gamemenu_item_rects = self.draw_menu_drop_down([f'Play vs {opponent}', ' ', 'Time control'], self.file_button[2] + self.position_button[2], self.theme.top_bar_height)
        elif self.boardmenu_active:
            self.boardmenu_dropdown_area, self.boardmenu_item_rects = self.draw_menu_drop_down(['Flip board', 'Undo move', 'Themes', u'\u2022 Fancy', u'\u2022 Icy rocks'], self.file_button[2] + self.position_button[2] + self.game_button[2] + int(self.theme.sq_size / 6.25), self.theme.top_bar_height)

    def draw_menu_drop_down(self, items, x, y):

        # Background
        drop_down_width = self.theme.menu_font.size(max(items, key=len))[0] + int(self.theme.sq_size/3)
        drop_down_height = len(items)*self.theme.top_bar_height + self.theme.menu_font.get_height() + 2*self.theme.margin if 'Themes' in items else len(items)*self.theme.top_bar_height + self.theme.menu_font.get_height()
        drop_down_rect = pygame.Rect(x, y, drop_down_width, drop_down_height)
        pygame.draw.rect(self.screen, self.theme.grey[0], drop_down_rect)

        # Text
        start_x, start_y = x + 4*self.theme.margin, y + self.theme.menu_font.get_height()/2 + int(self.theme.sq_size/5)
        item_rects = []
        for item in items:

            # Create line and extra space if exit
            if item in 'Exit':
                pygame.draw.line(self.screen, self.theme.grey[3], (x, start_y - 4*self.theme.margin), (x + drop_down_width, start_y - 4*self.theme.margin), 1)
                new_rect = pygame.Rect(x, start_y - self.theme.menu_font.get_height() / 2 - 2*self.theme.margin, drop_down_width, self.theme.menu_font.get_height() + 6*self.theme.margin)
                item_rects.append(new_rect)
                if new_rect == self.chosen_menu_rect:
                    surface = pygame.Surface((new_rect[2], new_rect[3]), pygame.SRCALPHA)
                    surface.fill(self.theme.grey[1])
                    self.screen.blit(surface, (new_rect[0], new_rect[1]))
                self.create_text(item, self.theme.menu_font, self.theme.black, start_x, start_y + self.theme.menu_font.get_height()/2 - 4, 'left')
            elif item == 'Themes':
                pygame.draw.line(self.screen, self.theme.grey[3], (x, start_y - self.theme.menu_font.get_height() + 2*self.theme.margin), (x + drop_down_width, start_y - self.theme.menu_font.get_height() + 2*self.theme.margin), 1)
                self.create_text(item, self.theme.menu_font_bold, self.theme.black, x + drop_down_width/2, start_y + self.theme.menu_font_bold.get_height()/2 - 5*self.theme.margin, 'center')
                pygame.draw.line(self.screen, self.theme.grey[2], (x, start_y + self.theme.menu_font.get_height() - 3*self.theme.margin), (x + drop_down_width, start_y + self.theme.menu_font.get_height() - 3*self.theme.margin), 1)
                start_y += self.theme.menu_font.get_height() + 5*self.theme.margin
            else:
                new_rect = pygame.Rect(x, start_y - self.theme.menu_font.get_height()/2 - 2*self.theme.margin, drop_down_width, self.theme.menu_font.get_height() + 4*self.theme.margin)
                item_rects.append(new_rect)
                if new_rect == self.chosen_menu_rect:
                    surface = pygame.Surface((new_rect[2], new_rect[3]), pygame.SRCALPHA)
                    surface.fill(self.theme.grey[1])
                    self.screen.blit(surface, (new_rect[0], new_rect[1]))
                self.create_text(item, self.theme.menu_font, self.theme.black, start_x, start_y, 'left')
                start_y += self.theme.menu_font.get_height() + 4*self.theme.margin

        return drop_down_rect, item_rects

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                   Helper drawing functions
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    def draw_highlighting(self, color, color_t, x, y, width, height, thickness=0, edge=True):
        surface = pygame.Surface((width, height), pygame.SRCALPHA)
        surface.fill(color_t)
        self.screen.blit(surface, (x, y))
        if edge:
            pygame.draw.rect(self.screen, color, (x, y, self.theme.sq_size, self.theme.sq_size), thickness, border_radius=1)

    def create_menu_items(self, text, color, x, y, box_x_neg, box_x_pos):
        text = self.theme.menu_font.render(text, True, self.theme.black)
        text_rect = text.get_rect()
        text_rect.midleft = (x, y)

        box = (x - box_x_neg + 1, 1, text_rect[2] + box_x_pos - 2, self.theme.top_bar_height-1)
        rect_button = pygame.Rect(box)

        # Highlight when hover over item
        pygame.draw.rect(self.screen, color, box)

        self.screen.blit(text, text_rect)

        return rect_button

    def create_buttons(self, text, font, color, x, y):
        text = font.render(text, True, color)
        text_rect = text.get_rect()
        text_rect.midtop = (x, y)

        box = (8*self.theme.sq_size + 3*self.theme.board_offset, text_rect[1] - 2*self.theme.margin, self.theme.clock_width - 2*self.theme.board_offset, text_rect[3] + 4*self.theme.margin)
        rect_button = pygame.Rect(box)

        pygame.draw.rect(self.screen, self.theme.board_text_color, box, 1)
        self.screen.blit(text, text_rect)

        return rect_button

    def create_text(self, text, font, color, x, y, position):
        text = font.render(text, True, color)
        rect = text.get_rect()
        if position == 'center':
            rect.center = (x, y)
        elif position == 'left':
            rect.midleft = (x, y)
        elif position == 'right':
            rect.midright = (x, y)
        self.screen.blit(text, rect)

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                Other GUI helper functions
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

    # Init a new game
    def init_game(self):

        self.gamestate = gs.GameState(self.start_fen)

        # Moves
        self.moves_made = []
        self.latest_move = [(-100, -100, '')]

        # Keep track of mouse button presses and mouse movements
        self.is_dragging = False
        self.square_under_mouse = 0
        self.x, self.y = 0, 0
        self.selected_square = 0

        # Initiate initial gamestate variables
        self.playing = False

        # PV info
        self.ai.print_info = {}

        # Keep track of game times
        self.white_time = self.black_time = self.theme.tot_time
        self.move_time_white = self.move_time_black = 0
        self.time_log = [(self.white_time, self.black_time, self.move_time_white, self.move_time_black)]
        self.paused = False

    # AI make a move with iterative deepening
    def ai_make_a_move(self):

        # Calculate time parameters
        fixed_depth = 64
        timeset = 0
        stoptime = 0
        starttime = time.time()
        movestogo = max(5, self.theme.movestogo - round(self.gamestate.move_counter))  # If we have less than 5 moves to go, always divide time left by 5

        # Set game time
        tot_time = self.white_time if self.is_ai_white else self.black_time

        # If depth is not available, set it to something large
        if self.theme.fixed_depth != 64:
            fixed_depth = self.theme.fixed_depth

        # If move time was given, update time to movetime and moves to go to 1
        if self.theme.movetime != 0:
            tot_time = self.theme.movetime
            movestogo = 1

        # If time control is available, flag that we play with time control and set timing
        if tot_time != 0:
            timeset = 1

            # Divide time equally between how many moves we should do
            tot_time /= movestogo

            # Add time and increment to get what time we should stop at (with lag compensation)
            stoptime = max(starttime + 0.05, starttime + tot_time + self.theme.inc - 0.1)

        # How often to check for timeout (at what nodes interval)
        if tot_time < 5:
            check_timeout = 800
        elif 5 <= stoptime - starttime <= 10:
            check_timeout = 12000
        else:
            check_timeout = 2000

        # Init AI and variables
        self.ai = Ai(self.gamestate, search_depth=fixed_depth, stoptime=stoptime, timeset=timeset, check_timeout=check_timeout)

        self.ai.pv_line = ''
        self.ai.print_info = {}
        self.ai.nodes = -1

        # Iterative deepening
        best_move, best_score = None, None

        for current_depth in range(1, self.ai.search_depth + 1):

            # Draw GUI
            self.draw()

            # Initiate time
            start_move = time.time()

            # Search position
            move, score = self.ai.ai_make_move(current_depth=current_depth, best_move=best_move, best_score=best_score)

            # Update move times
            end_move = round(time.time() - start_move, 2)
            if self.gamestate.is_white_turn:
                if not self.theme.fixed_depth and not self.theme.movetime:
                    self.white_time -= end_move
                    self.move_time_white += end_move
            else:
                if not self.theme.fixed_depth and not self.theme.movetime:
                    self.black_time -= end_move
                    self.move_time_black += end_move

            # Stop if time runs out, else update best_move and best_score
            if self.ai.stopped:
                break
            else:
                best_move, best_score = move, score

        return best_move, best_score

    # Make a move on the board
    def process_move(self, move):

        # Update time log
        self.time_log.append((self.white_time, self.black_time, self.move_time_white, self.move_time_black))

        # Reset move times and update time increments
        if self.gamestate.is_white_turn:
            self.move_time_black = 0
            self.white_time += self.theme.inc
        else:
            self.move_time_white = 0
            self.black_time += self.theme.inc

        # Change back to playing again and reset paused
        self.playing = True
        self.paused = False

        # Make the move and update move info
        self.gamestate.make_move(move)
        self.latest_move.append(move)

        # Add latest move to the moves_made log
        self.moves_made.append(move)

        # Play a sound when a move is made
        if self.theme.toggle_sound:
            sound = pygame.mixer.Sound('../gui/sounds/capture.wav') if self.gamestate.piece_captured != '--' else pygame.mixer.Sound('../gui/sounds/move.wav')
            sound.play()

        # Flip board if human vs human and if board is not already flipped in the right direction for player turn
        if self.game_mode == 'human' and self.theme.auto_flip:
            if (self.gamestate.is_white_turn and self.is_flipped) or (not self.gamestate.is_white_turn and not self.is_flipped):
                self.is_flipped = not self.is_flipped

        # Update current fen
        self.current_fen = fh.gamestate_to_fen(self.gamestate)

        # Change move made variable
        self.is_ai_turn = not self.is_ai_turn

    # Unmake a move on the board
    def unmake_a_move(self):

        # Can't redo engines first move
        moves_made = 1 if (not self.is_ai_white or (not self.is_ai_white and len(self.gamestate.move_log) == 2)) else 2

        if len(self.gamestate.move_log) > moves_made and not (not self.is_ai_white and self.game_mode == 'ai' and len(self.gamestate.move_log) == 2):

            self.time_log.pop()
            self.white_time = self.time_log[-1][0]
            self.black_time = self.time_log[-1][1]
            self.move_time_white = self.time_log[-1][2]
            self.move_time_black = self.time_log[-1][3]

            self.gamestate.unmake_move()
            self.moves_made.pop()
            self.latest_move.pop()
            if self.game_mode == 'human':
                if ((self.gamestate.is_white_turn and self.is_flipped) or (not self.gamestate.is_white_turn and not self.is_flipped)) and self.theme.auto_flip:
                    self.is_flipped = not self.is_flipped

    # Get current square under the mouse
    def get_square_under_mouse(self):
        pos = pygame.mouse.get_pos()  # (x, y) location of click
        col, row = ((pos[0] + self.theme.sq_size - self.theme.board_offset) // self.theme.sq_size, (pos[1] + 2 * self.theme.sq_size - self.theme.board_offset - self.theme.top_bar_height) // self.theme.sq_size) if not self.is_flipped \
            else (9 - (pos[0] + self.theme.sq_size - self.theme.board_offset) // self.theme.sq_size, 11 - (pos[1] + 2 * self.theme.sq_size - self.theme.board_offset - self.theme.top_bar_height) // self.theme.sq_size)  # Get corresponding square on chess board

        square_under_mouse = row * 10 + col  # Get corresponding square on the 10x12 board

        return square_under_mouse, col, row

    # Checks if current gamestate is checkmate or stalemate or if time ran out
    def check_for_gameover(self):

        # Find if there are any legal moves in the position for the player
        possible_moves = self.gamestate.get_valid_moves()

        # Find if own king is in check
        is_in_check = self.gamestate.check_for_checks(self.gamestate.king_location[not self.gamestate.is_white_turn])

        # If no possible moves, it is either stalemate or checkmate depending on if the king is in check
        if not possible_moves:
            if is_in_check:
                return 'checkmate'
            return 'stalemate'

        # Check for 3-fold repetition
        repetitions = 0
        latest_key = self.gamestate.repetition_table[-1][0]
        for key, piece_moved, piece_captured in reversed(self.gamestate.repetition_table):

            # Check if position has occurred before in the came
            if key == latest_key:
                repetitions += 1

            # If 3 positions has occurred before, return stalemate by 3 fold repetition
            if repetitions == 3:
                return 'stalemate'

            # Break early if there is a pawn move or capture since position can't be the same after such move has been made
            if piece_captured != '--' or piece_moved in 'pP':
                break

        # Check for 50 move rule
        if self.gamestate.halfmove_counter >= 100:
            return 'stalemate'

        # Check for time out (ignore for user if forfeit on time option is not on
        if self.white_time < 0 and not self.theme.fixed_depth and not self.theme.movetime:
            self.white_time = 0
            if self.is_ai_white or (not self.is_ai_white and self.theme.forfeit_on_time):
                return 'white time'
        elif self.black_time < 0 and not self.theme.fixed_depth and not self.theme.movetime:
            self.black_time = 0
            if not self.is_ai_white or (self.is_ai_white and self.theme.forfeit_on_time):
                return 'black time'

        # If nothing was found, return False
        return False

# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                           Run the GUI
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------


if __name__ == '__main__':

    timing = False  # Set to True to time a game and get how much time each function takes
    timing_sort = 'tottime'  # Chose what to sort timing on. See options here: https://blog.alookanalytics.com/2017/03/21/python-profiling-basics/

    # Set the correct icon in Windows taskbar
    if sys.platform.startswith('win'):
        myappid = u'_'
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    # If timing a game, run the cProfile module. Else run normally.
    if timing:
        pr = cProfile.Profile()
        pr.enable()
        Gui().main()
        pr.disable()
        pr.print_stats(sort=timing_sort)
    else:
        Gui().main()
