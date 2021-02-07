# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                          gui_popup.py
#
#                   - Handles all window popups appearing from the main gui
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

import fen_handling as fh
import pyperclip
import time
import pygame


class Popup:

    def __init__(self, screen, copy_of_screen, theme):

        self.screen = screen
        self.copy_of_screen = copy_of_screen
        self.theme = theme

# ---------------------------------------------------------------------------------------------------------
#
#                   Set time control for the game and calculate time management
#
# ---------------------------------------------------------------------------------------------------------

    def chose_time_control(self):

        # Top coordinates (0, 0) of local window
        width, height = self.theme.win_width/3.4, self.theme.win_height/2.3
        x, y = self.theme.win_width/2 - width/2, self.theme.win_height/2 - height/1.5

        # ---------------------------
        # Pop up loop to ask for input
        # ---------------------------

        # Init variables
        running = True
        depth_blinking = False
        per_move_blinking = False
        blitz_min_blinking = False
        blitz_sec_blinking = False
        blitz_inc_blinking = False
        dragging = False

        depth_text = '0'
        per_move_text = '0'
        blitz_min_text = '0'
        blitz_sec_text = '0'
        blitz_inc_text = '0'

        start_time = time.time()

        while running:

            # Events happening in GUI
            for event in pygame.event.get():

                # Get mouse position
                pos = pygame.mouse.get_pos()

                # ---------------------------
                # Mouse down events
                # ---------------------------
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # Reset fields
                    depth_blinking = False
                    per_move_blinking = False
                    blitz_min_blinking = False
                    blitz_sec_blinking = False
                    blitz_inc_blinking = False

                    # Break if user presses on X or Okay button
                    if exit_button.collidepoint(pos) or okay_button.collidepoint(pos):
                        running = False

                    # Ability to move window when holding top bar
                    elif top_bar_rect.collidepoint(pos):
                        dragging = True
                        mouse_x, mouse_y = event.pos
                        offset_x = window_rect.x - mouse_x
                        offset_y = window_rect.y - mouse_y

                    # Clicks on depth button
                    elif depth_button.collidepoint(pos):
                        depth_blinking = True

                    # Click on seconds per move button
                    elif per_move_button.collidepoint(pos):
                        per_move_blinking = True

                    # Clicks on blitz minute button
                    elif blitz_min_button.collidepoint(pos):
                        blitz_min_blinking = True

                    # Clicks on blitz seconds button
                    elif blitz_sec_button.collidepoint(pos):
                        blitz_sec_blinking = True

                    # Clicks on blitz increment button
                    elif blitz_inc_button.collidepoint(pos):
                        blitz_inc_blinking = True

                # ---------------------------
                # Mouse up events
                # ---------------------------
                elif event.type == pygame.MOUSEBUTTONUP:

                    # Not dragging anymore
                    dragging = False

                # ---------------------------
                # Mouse motion events
                # ---------------------------
                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        mouse_x, mouse_y = event.pos
                        x = mouse_x + offset_x
                        y = mouse_y + offset_y

                # ---------------------------
                # Key down events
                # ---------------------------
                if event.type == pygame.KEYDOWN:

                    # Depth input text or delete text
                    if depth_blinking:
                        if event.unicode.isnumeric():
                            per_move_text = blitz_min_text = blitz_sec_text = blitz_inc_text = '0'
                            depth_text = str(min(int(event.unicode), 8))
                        elif event.key == pygame.K_BACKSPACE:
                            depth_text = ''

                    # Seconds per move input text or delete text
                    elif per_move_blinking:
                        if event.unicode.isnumeric():
                            depth_text = blitz_min_text = blitz_sec_text = blitz_inc_text = '0'
                            per_move_text += event.unicode
                            per_move_text = str(min(int(per_move_text), 3600))
                        elif event.key == pygame.K_BACKSPACE:
                            per_move_text = per_move_text[:-1]

                    # Blitz minutes input text or delete text
                    elif blitz_min_blinking:
                        if event.unicode.isnumeric():
                            per_move_text = depth_text = '0'
                            blitz_min_text += event.unicode
                            blitz_min_text = str(min(int(blitz_min_text), 999))
                        elif event.key == pygame.K_BACKSPACE:
                            blitz_min_text = blitz_min_text[:-1]

                    # Blitz seconds input text or delete text
                    elif blitz_sec_blinking:
                        if event.unicode.isnumeric():
                            per_move_text = depth_text = '0'
                            blitz_sec_text += event.unicode
                            blitz_sec_text = str(min(int(blitz_sec_text), 59))
                        elif event.key == pygame.K_BACKSPACE:
                            blitz_sec_text = blitz_sec_text[:-1]

                    # Blitz increment input text or delete text
                    elif blitz_inc_blinking:
                        if event.unicode.isnumeric():
                            per_move_text = depth_text = '0'
                            blitz_inc_text += event.unicode
                            blitz_inc_text = str(min(int(blitz_inc_text), 300))
                        elif event.key == pygame.K_BACKSPACE:
                            blitz_inc_text = blitz_inc_text[:-1]

            # --------------------------------------
            #              Draw things
            # --------------------------------------

            # Background screen
            self.screen.blit(self.copy_of_screen, (0, 0))

            # Create pop up
            window_rect, top_bar_rect, exit_button = self.create_window('Chose time control', x, y, width, height)

            # Fixed depth
            self.create_text('Fixed depth: ', self.theme.popup_font_bold, self.theme.black, x + 6*self.theme.margin, y + self.theme.sq_size, 'left')
            depth_button = self.create_button('', self.theme.popup_font, self.theme.black, self.theme.black, (x + 1.9*self.theme.sq_size, y + self.theme.sq_size - 4*self.theme.margin - 2, 0.4*self.theme.sq_size, self.theme.popup_font.get_height() + 4*self.theme.margin), True, False)
            self.create_text('(max 8)', self.theme.popup_font, self.theme.black, depth_button[0] + depth_button[2] + 4*self.theme.margin, y + self.theme.sq_size, 'left')

            if depth_blinking and depth_text == '0':
                if (round((time.time() - start_time))) % 2 != 0:
                    pygame.draw.line(self.screen, self.theme.black, (depth_button[0] + depth_button[2] - 2*self.theme.margin, depth_button[1] + 2), (depth_button[0] + depth_button[2] - 2*self.theme.margin, depth_button[1] + depth_button[3] - 4), 1)

            elif depth_text:
                self.create_text(depth_text, self.theme.popup_font, self.theme.black, depth_button[0] + depth_button[2] - 2*self.theme.margin, depth_button[1] + self.theme.popup_font.get_height() - 2*self.theme.margin, 'right')

            # Time per move
            self.create_text('Time/move [s]: ', self.theme.popup_font_bold, self.theme.black, x + 6*self.theme.margin, y + 1.7*self.theme.sq_size, 'left')
            per_move_button = self.create_button('', self.theme.popup_font, self.theme.black, self.theme.black, (x + 1.7*self.theme.sq_size, y + 1.7*self.theme.sq_size - 4*self.theme.margin - 2, 0.6*self.theme.sq_size, self.theme.popup_font.get_height() + 4*self.theme.margin), True, False)
            self.create_text('(max 3600)', self.theme.popup_font, self.theme.black, per_move_button[0] + per_move_button[2] + 4*self.theme.margin, y + 1.7*self.theme.sq_size, 'left')

            if per_move_blinking and per_move_text == '0':
                if (round((time.time() - start_time))) % 2 != 0:
                    pygame.draw.line(self.screen, self.theme.black, (per_move_button[0] + per_move_button[2] - 2*self.theme.margin, per_move_button[1] + 2), (per_move_button[0] + per_move_button[2] - 2*self.theme.margin, per_move_button[1] + per_move_button[3] - 4), 1)

            elif per_move_text:
                self.create_text(per_move_text, self.theme.popup_font, self.theme.black, per_move_button[0] + per_move_button[2] - 2*self.theme.margin, per_move_button[1] + self.theme.popup_font.get_height() - 2*self.theme.margin, 'right')

            # Blitz
            self.create_text('Blitz', self.theme.popup_font_bold, self.theme.black, x + 6*self.theme.margin, y + 2.4*self.theme.sq_size, 'left')

            self.create_text('Minutes: ', self.theme.popup_font, self.theme.black, x + 6*self.theme.margin, y + 2.8 * self.theme.sq_size, 'left')
            blitz_min_button = self.create_button('', self.theme.popup_font, self.theme.black, self.theme.black, (x + 1.7*self.theme.sq_size, y + 2.8*self.theme.sq_size - 4*self.theme.margin - 2, 0.6*self.theme.sq_size, self.theme.popup_font.get_height() + 4*self.theme.margin), True, False)
            self.create_text('(max 999)', self.theme.popup_font, self.theme.black, blitz_min_button[0] + blitz_min_button[2] + 4*self.theme.margin, y + 2.8*self.theme.sq_size, 'left')

            if blitz_min_blinking and blitz_min_text == '0':
                if (round((time.time() - start_time))) % 2 != 0:
                    pygame.draw.line(self.screen, self.theme.black, (blitz_min_button[0] + blitz_min_button[2] - 2*self.theme.margin, blitz_min_button[1] + 2), (blitz_min_button[0] + blitz_min_button[2] - 2*self.theme.margin, blitz_min_button[1] + blitz_min_button[3] - 4), 1)
            elif blitz_min_text:
                self.create_text(blitz_min_text, self.theme.popup_font, self.theme.black, blitz_min_button[0] + blitz_min_button[2] - 2*self.theme.margin, blitz_min_button[1] + self.theme.popup_font.get_height() - 2*self.theme.margin, 'right')

            self.create_text('Seconds: ', self.theme.popup_font, self.theme.black, x + 6*self.theme.margin, y + 3.2 * self.theme.sq_size, 'left')
            blitz_sec_button = self.create_button('', self.theme.popup_font, self.theme.black, self.theme.black, (x + 1.7*self.theme.sq_size, y + 3.2*self.theme.sq_size - 4*self.theme.margin - 2, 0.6*self.theme.sq_size, self.theme.popup_font.get_height() + 4*self.theme.margin), True, False)
            self.create_text('(max 59)', self.theme.popup_font, self.theme.black, blitz_sec_button[0] + blitz_sec_button[2] + 4*self.theme.margin, y + 3.2*self.theme.sq_size, 'left')

            if blitz_sec_blinking and blitz_sec_text == '0':
                if (round((time.time() - start_time))) % 2 != 0:
                    pygame.draw.line(self.screen, self.theme.black, (blitz_sec_button[0] + blitz_sec_button[2] - 2*self.theme.margin, blitz_sec_button[1] + 2), (blitz_sec_button[0] + blitz_sec_button[2] - 2*self.theme.margin, blitz_sec_button[1] + blitz_sec_button[3] - 4), 1)
            elif blitz_sec_text:
                self.create_text(blitz_sec_text, self.theme.popup_font, self.theme.black, blitz_sec_button[0] + blitz_sec_button[2] - 2*self.theme.margin, blitz_sec_button[1] + self.theme.popup_font.get_height() - 2*self.theme.margin, 'right')

            self.create_text('Increment [s]: ', self.theme.popup_font, self.theme.black, x + 6*self.theme.margin, y + 3.8 * self.theme.sq_size, 'left')
            blitz_inc_button = self.create_button('', self.theme.popup_font, self.theme.black, self.theme.black, (x + 1.7*self.theme.sq_size, y + 3.8*self.theme.sq_size - 4*self.theme.margin - 2, 0.6*self.theme.sq_size, self.theme.popup_font.get_height() + 4*self.theme.margin), True, False)
            self.create_text('(max 300)', self.theme.popup_font, self.theme.black, blitz_inc_button[0] + blitz_inc_button[2] + 8, y + 3.8*self.theme.sq_size, 'left')

            if blitz_inc_blinking and blitz_inc_text == '0':
                if (round((time.time() - start_time))) % 2 != 0:
                    pygame.draw.line(self.screen, self.theme.black, (blitz_inc_button[0] + blitz_inc_button[2] - 2*self.theme.margin, blitz_inc_button[1] + 2), (blitz_inc_button[0] + blitz_inc_button[2] - 2*self.theme.margin, blitz_inc_button[1] + blitz_inc_button[3] - 4), 1)
            elif blitz_inc_text:
                self.create_text(blitz_inc_text, self.theme.popup_font, self.theme.black, blitz_inc_button[0] + blitz_inc_button[2] - 2*self.theme.margin, blitz_inc_button[1] + self.theme.popup_font.get_height() - 2*self.theme.margin, 'right')

            # Okay button
            okay_button = self.create_okay_button(x, y, width, height)

            # Update screen
            pygame.display.flip()

        # --------------------------------------
        #     When options have been chosen
        # --------------------------------------
        if not running and any((int(depth_text), int(per_move_text), int(blitz_min_text), int(blitz_sec_text), int(blitz_inc_text))):

            # If increment then blitz mins/seconds needs to be something
            if int(blitz_inc_text):
                if not (int(blitz_min_text)*60 + int(blitz_sec_text)):
                    blitz_min_text = '1'

            # Init variables given from user
            self.theme.fixed_depth = int(depth_text)
            self.theme.movetime = int(per_move_text)
            self.theme.tot_time = (int(blitz_min_text)*60 + int(blitz_sec_text))
            self.theme.inc = int(blitz_inc_text)

# ---------------------------------------------------------------------------------------------------------
#
#                         Collect a FEN string from user pasting on screen
#
# ---------------------------------------------------------------------------------------------------------

    def set_up_position(self):

        # Top coordinates (0, 0) of local window
        width, height = self.theme.win_width / 2, self.theme.win_height / 4.5
        x, y = self.theme.win_width / 2 - width / 2, self.theme.win_height / 2 - height / 1.5

        # ---------------------------
        # Pop up loop to ask for input
        # ---------------------------

        # Init variables
        running = True
        fen_blinking = False
        dragging = False
        wrong_fen = False

        fen_text = ''

        start_time = time.time()

        while running:

            # Events happening in GUI
            for event in pygame.event.get():

                # Get mouse position
                pos = pygame.mouse.get_pos()

                # ---------------------------
                #     Mouse down events
                # ---------------------------
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # Reset fields
                    fen_blinking = False

                    # Break if user presses on X and send in start fen as default
                    if exit_button.collidepoint(pos):
                        fen_text = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'
                        running = False

                    # Break if pressing okay and check if a valid fen was inputted
                    if okay_button.collidepoint(pos):
                        if fh.test_fen(fen_text) or fen_text == '':
                            running = False
                        else:
                            wrong_fen = True

                    # Ability to move window when holding top bar
                    elif top_bar_rect.collidepoint(pos):
                        dragging = True
                        mouse_x, mouse_y = event.pos
                        offset_x = window_rect.x - mouse_x
                        offset_y = window_rect.y - mouse_y

                    # Clicks on fen button
                    elif fen_button.collidepoint(pos):
                        fen_blinking = True

                # ---------------------------
                #      Mouse up events
                # ---------------------------
                elif event.type == pygame.MOUSEBUTTONUP:

                    # Not dragging anymore
                    dragging = False

                # ---------------------------
                # Mouse motion events
                # ---------------------------
                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        mouse_x, mouse_y = event.pos
                        x = mouse_x + offset_x
                        y = mouse_y + offset_y

                # ---------------------------
                #      Key down events
                # ---------------------------
                if event.type == pygame.KEYDOWN:

                    # Depth input text or delete text
                    if fen_blinking:
                        if event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                            fen_text = pyperclip.paste()
                        elif event.key == pygame.K_BACKSPACE:
                            fen_text = ''

            # --------------------------------------
            #              Draw things
            # --------------------------------------

            # Background screen
            self.screen.blit(self.copy_of_screen, (0, 0))

            # Create pop up
            window_rect, top_bar_rect, exit_button = self.create_window('Set start position', x, y, width, height)

            # Insert FEN text
            self.create_text('Insert FEN (Ctrl + v):', self.theme.popup_font_bold, self.theme.black, x + 6*self.theme.margin, y + 0.85*self.theme.sq_size, 'left')
            fen_button = self.create_button('', self.theme.popup_font, self.theme.black, self.theme.black, (x + 6*self.theme.margin, y + 1.15*self.theme.sq_size, width - 0.41*self.theme.sq_size, self.theme.popup_font.get_height() + 4*self.theme.margin), True, False)

            if fen_blinking and fen_text == '':
                if (round((time.time() - start_time))) % 2 != 0:
                    pygame.draw.line(self.screen, self.theme.black, (fen_button[0] + fen_button[2] - 2*self.theme.margin, fen_button[1] + 2), (fen_button[0] + fen_button[2] - 2*self.theme.margin, fen_button[1] + fen_button[3] - 4), 1)

            elif fen_text:
                self.create_text(fen_text, self.theme.fen_font, self.theme.black, fen_button[0] + fen_button[2] - 2*self.theme.margin, fen_button[1] + self.theme.popup_font.get_height() - 2*self.theme.margin, 'right')

            # Okay button
            okay_button = self.create_okay_button(x, y, width, height)

            # Wrong FEN input text
            if wrong_fen:
                self.create_text('Please enter a valid FEN string.', self.theme.popup_font, self.theme.red, x + 7*self.theme.margin, y + 1.7*self.theme.sq_size, 'left')

            # Update screen
            pygame.display.flip()

        # --------------------------------------
        #     When options have been chosen
        # --------------------------------------
        if not running:
            self.theme.start_fen = fen_text if fen_text != '' else 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

# ---------------------------------------------------------------------------------------------------------
#
#                      Game over screen during stalemate or checkmate
#
# ---------------------------------------------------------------------------------------------------------

    def gameover_screen(self, input_text):

        # Change the input text to suit purpose
        text = {'checkmate': 'Checkmate',
                'stalemate': 'Stalemate',
                'white time': 'White lost on time',
                'black time': 'Black lost on time'}[input_text]

        # Top coordinates (0, 0) of local window
        width, height = self.theme.win_width / 2.7, self.theme.win_height / 5
        x, y = self.theme.win_width / 2 - width / 2, self.theme.win_height / 2 - height / 1.5

        # ---------------------------
        # Pop up loop to ask for input
        # ---------------------------

        # Init variables
        running = True
        dragging = False

        yes_box = True

        while running:

            # Events happening in GUI
            for event in pygame.event.get():

                # Get mouse position
                pos = pygame.mouse.get_pos()

                # ---------------------------
                #     Mouse down events
                # ---------------------------
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # Break if user presses on X and send in start fen as default
                    if exit_button.collidepoint(pos) or okay_button.collidepoint(pos):
                        running = False

                    # Ability to move window when holding top bar
                    elif top_bar_rect.collidepoint(pos):
                        dragging = True
                        mouse_x, mouse_y = event.pos
                        offset_x = window_rect.x - mouse_x
                        offset_y = window_rect.y - mouse_y

                    # Clicks on yes button
                    elif yes_button.collidepoint(pos):
                        yes_box = True

                    # Clicks on no button
                    elif no_button.collidepoint(pos):
                        yes_box = False

                # ---------------------------
                #      Mouse up events
                # ---------------------------
                elif event.type == pygame.MOUSEBUTTONUP:

                    # Not dragging anymore
                    dragging = False

                # ---------------------------
                # Mouse motion events
                # ---------------------------
                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        mouse_x, mouse_y = event.pos
                        x = mouse_x + offset_x
                        y = mouse_y + offset_y

                # ---------------------------
                #      Key down events
                # ---------------------------
                if event.type == pygame.KEYDOWN:

                    # Depth input text or delete text
                    if event.key == pygame.K_RETURN:
                        running = False

            # --------------------------------------
            #              Draw things
            # --------------------------------------

            # Background screen
            self.screen.blit(self.copy_of_screen, (0, 0))

            # Create pop up window
            window_rect, top_bar_rect, exit_button = self.create_window(text, x, y, width, height)

            # Draw yes and no circles
            circle_outer, circle_inner = int(self.theme.sq_size/11.82), int(self.theme.sq_size/21.67)
            self.create_text('Do you want to play again?', self.theme.popup_font_bold, self.theme.black, x + 0.8 * self.theme.sq_size + 6*self.theme.margin, y + 0.85 * self.theme.sq_size, 'left')

            self.create_text('Yes', self.theme.popup_font, self.theme.black, x + 1.2 * self.theme.sq_size + 6*self.theme.margin, y + 1.37 * self.theme.sq_size, 'left')
            pygame.draw.circle(self.screen, self.theme.black, (x + 1.65 * self.theme.sq_size + 6*self.theme.margin, y + 1.37 * self.theme.sq_size), circle_outer, width=1)
            self.create_text('No', self.theme.popup_font, self.theme.black, x + 2.2 * self.theme.sq_size + 6*self.theme.margin, y + 1.37 * self.theme.sq_size, 'left')
            pygame.draw.circle(self.screen, self.theme.black, (x + 2.65 * self.theme.sq_size + 6*self.theme.margin, y + 1.37 * self.theme.sq_size), circle_outer, width=1)

            if yes_box:
                pygame.draw.circle(self.screen, self.theme.black, (x + 1.65 * self.theme.sq_size + 6*self.theme.margin, y + 1.37 * self.theme.sq_size), circle_inner, width=0)
            else:
                pygame.draw.circle(self.screen, self.theme.black, (x + 2.65 * self.theme.sq_size + 6*self.theme.margin, y + 1.37 * self.theme.sq_size), circle_inner, width=0)

            yes_button = self.create_button('', self.theme.popup_font, self.theme.green, self.theme.green,
                                            (x + 1.65 * self.theme.sq_size + 6*self.theme.margin - circle_outer-1, y + 1.37 * self.theme.sq_size - circle_outer-1, 2*circle_outer + 2, 2*circle_outer + 2), False, False)
            no_button = self.create_button('', self.theme.popup_font, self.theme.red, self.theme.red,
                                            (x + 2.65 * self.theme.sq_size + 6*self.theme.margin - circle_outer-1, y + 1.37 * self.theme.sq_size - circle_outer-1, 2*circle_outer + 2, 2*circle_outer + 2), False, False)

            # Okay button
            okay_button = self.create_okay_button(x, y, width, height)

            # Update screen
            pygame.display.flip()

        # --------------------------------------
        #     When options have been chosen
        # --------------------------------------
        return True if yes_box else False

# ---------------------------------------------------------------------------------------------------------
#
#                      Game over screen during stalemate or checkmate
#
# ---------------------------------------------------------------------------------------------------------

    def get_promotion(self, move, piece_moved):

        # Top coordinates (0, 0) of local window
        width, height = self.theme.win_width / 7, self.theme.win_height / 3.1
        x, y = self.theme.win_width / 2 - width / 2, self.theme.win_height / 2 - height / 1.5

        # ---------------------------
        # Pop up loop to ask for input
        # ---------------------------

        # Init variables
        running = True
        dragging = False

        queen_box = True
        rook_box = False
        bishop_box = False
        knight_box = False

        chosen_piece = 'Q'

        while running:

            # Events happening in GUI
            for event in pygame.event.get():

                # Get mouse position
                pos = pygame.mouse.get_pos()

                # ---------------------------
                #     Mouse down events
                # ---------------------------
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # Break if user presses on X and send in start fen as default
                    if exit_button.collidepoint(pos) or okay_button.collidepoint(pos):
                        running = False

                    # Ability to move window when holding top bar
                    elif top_bar_rect.collidepoint(pos):
                        dragging = True
                        mouse_x, mouse_y = event.pos
                        offset_x = window_rect.x - mouse_x
                        offset_y = window_rect.y - mouse_y

                    # Clicks on piece buttons
                    elif queen_button.collidepoint(pos):
                        rook_box = bishop_box = knight_box = False
                        queen_box = True
                        chosen_piece = 'Q'
                    elif rook_button.collidepoint(pos):
                        queen_box = bishop_box = knight_box = False
                        rook_box = True
                        chosen_piece = 'R'
                    elif bishop_button.collidepoint(pos):
                        queen_box = rook_box = knight_box = False
                        bishop_box = True
                        chosen_piece = 'B'
                    elif knight_button.collidepoint(pos):
                        queen_box = rook_box = bishop_box = False
                        knight_box = True
                        chosen_piece = 'N'

                # ---------------------------
                #      Mouse up events
                # ---------------------------
                elif event.type == pygame.MOUSEBUTTONUP:

                    # Not dragging anymore
                    dragging = False

                # ---------------------------
                # Mouse motion events
                # ---------------------------
                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        mouse_x, mouse_y = event.pos
                        x = mouse_x + offset_x
                        y = mouse_y + offset_y

                # ---------------------------
                #      Key down events
                # ---------------------------
                if event.type == pygame.KEYDOWN:

                    # Depth input text or delete text
                    if event.key == pygame.K_RETURN:
                        running = False

            # --------------------------------------
            #              Draw things
            # --------------------------------------

            # Background screen
            self.screen.blit(self.copy_of_screen, (0, 0))

            # Create pop up
            window_rect, top_bar_rect, exit_button = self.create_window('Promotion', x, y, width, height)

            # Draw piece choices
            circle_outer, circle_inner = int(self.theme.sq_size / 11.82), int(self.theme.sq_size / 21.67)

            self.create_text('Queen', self.theme.popup_font, self.theme.black, x + 8*self.theme.margin, y + self.theme.top_bar_height + 0.6 * self.theme.sq_size, 'left')
            pygame.draw.circle(self.screen, self.theme.black, (x + 1.1 * self.theme.sq_size, y + self.theme.top_bar_height + 0.62 * self.theme.sq_size), circle_outer, width=1)

            self.create_text('Rook', self.theme.popup_font, self.theme.black, x + 8*self.theme.margin, y + self.theme.top_bar_height + 1.1 * self.theme.sq_size, 'left')
            pygame.draw.circle(self.screen, self.theme.black, (x + 1.1 * self.theme.sq_size, y + self.theme.top_bar_height + 1.12 * self.theme.sq_size), circle_outer, width=1)

            self.create_text('Bishop', self.theme.popup_font, self.theme.black, x + 8*self.theme.margin, y + self.theme.top_bar_height + 1.6 * self.theme.sq_size, 'left')
            pygame.draw.circle(self.screen, self.theme.black, (x + 1.1 * self.theme.sq_size, y + self.theme.top_bar_height + 1.62 * self.theme.sq_size), circle_outer, width=1)

            self.create_text('Knight', self.theme.popup_font, self.theme.black, x + 8*self.theme.margin, y + self.theme.top_bar_height + 2.1 * self.theme.sq_size, 'left')
            pygame.draw.circle(self.screen, self.theme.black, (x + 1.1 * self.theme.sq_size, y + self.theme.top_bar_height + 2.12 * self.theme.sq_size), circle_outer, width=1)

            if queen_box:
                pygame.draw.circle(self.screen, self.theme.black, (x + 1.1 * self.theme.sq_size, y + self.theme.top_bar_height + 0.62 * self.theme.sq_size), circle_inner, width=0)
            elif rook_box:
                pygame.draw.circle(self.screen, self.theme.black, (x + 1.1 * self.theme.sq_size, y + self.theme.top_bar_height + 1.12 * self.theme.sq_size), circle_inner, width=0)
            elif bishop_box:
                pygame.draw.circle(self.screen, self.theme.black, (x + 1.1 * self.theme.sq_size, y + self.theme.top_bar_height + 1.62 * self.theme.sq_size), circle_inner, width=0)
            elif knight_box:
                pygame.draw.circle(self.screen, self.theme.black, (x + 1.1 * self.theme.sq_size, y + self.theme.top_bar_height + 2.12 * self.theme.sq_size), circle_inner, width=0)

            queen_button = self.create_button('', self.theme.popup_font, self.theme.green, self.theme.green,
                                            (x + 1.1 * self.theme.sq_size - circle_outer - 1, y + self.theme.top_bar_height + 0.62 * self.theme.sq_size - circle_outer - 1, 2 * circle_outer + 2,
                                             2 * circle_outer + 2), False, False)
            rook_button = self.create_button('', self.theme.popup_font, self.theme.red, self.theme.red,
                                           (x + 1.1 * self.theme.sq_size - circle_outer - 1, y + self.theme.top_bar_height + 1.12 * self.theme.sq_size - circle_outer - 1, 2 * circle_outer + 2,
                                            2 * circle_outer + 2), False, False)
            bishop_button = self.create_button('', self.theme.popup_font, self.theme.light_blue, self.theme.light_blue,
                                           (x + 1.1 * self.theme.sq_size - circle_outer - 1, y + self.theme.top_bar_height + 1.62 * self.theme.sq_size - circle_outer - 1, 2 * circle_outer + 2,
                                            2 * circle_outer + 2), False, False)
            knight_button = self.create_button('', self.theme.popup_font, self.theme.orange, self.theme.orange,
                                           (x + 1.1 * self.theme.sq_size - circle_outer - 1, y + self.theme.top_bar_height + 2.12 * self.theme.sq_size - circle_outer - 1, 2 * circle_outer + 2,
                                            2 * circle_outer + 2), False, False)

            # Okay button
            okay_button = self.create_okay_button(x, y, width, height)

            # Update screen
            pygame.display.flip()

        move_type = f'p{chosen_piece}'
        promotion_move = ([move[0], move[1], move_type, piece_moved, -50000])

        return promotion_move

# ---------------------------------------------------------------------------------------------------------
#
#                                   Options menu screen
#
# ---------------------------------------------------------------------------------------------------------

    def get_options_menu(self):

        # Top coordinates (0, 0) of local window
        width, height = self.theme.win_width / 5, self.theme.win_height / 3.1
        x, y = self.theme.win_width / 2 - width / 2, self.theme.win_height / 2 - height / 1.5

        # ---------------------------
        # Pop up loop to ask for input
        # ---------------------------

        # Init variables
        running = True
        dragging = False

        sound_box = self.theme.toggle_sound
        forfeit_box = self.theme.forfeit_on_time
        flip_box = self.theme.auto_flip
        shortcuts_box = self.theme.enable_shortcuts

        while running:

            # Events happening in GUI
            for event in pygame.event.get():

                # Get mouse position
                pos = pygame.mouse.get_pos()

                # ---------------------------
                #     Mouse down events
                # ---------------------------
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # Break if user presses on X and send in start fen as default
                    if exit_button.collidepoint(pos) or okay_button.collidepoint(pos):
                        running = False

                    # Ability to move window when holding top bar
                    elif top_bar_rect.collidepoint(pos):
                        dragging = True
                        mouse_x, mouse_y = event.pos
                        offset_x = window_rect.x - mouse_x
                        offset_y = window_rect.y - mouse_y

                    # Clicks on piece buttons
                    elif buttons[0].collidepoint(pos):
                        sound_box = not sound_box
                        self.theme.toggle_sound = not self.theme.toggle_sound
                    elif buttons[1].collidepoint(pos):
                        forfeit_box = not forfeit_box
                        self.theme.forfeit_on_time = not self.theme.forfeit_on_time
                    elif buttons[2].collidepoint(pos):
                        shortcuts_box = not shortcuts_box
                        self.theme.enable_shortcuts = not self.theme.enable_shortcuts
                    elif buttons[3].collidepoint(pos):
                        flip_box = not flip_box
                        self.theme.auto_flip = not self.theme.auto_flip

                # ---------------------------
                #      Mouse up events
                # ---------------------------
                elif event.type == pygame.MOUSEBUTTONUP:

                    # Not dragging anymore
                    dragging = False

                # ---------------------------
                # Mouse motion events
                # ---------------------------
                elif event.type == pygame.MOUSEMOTION:
                    if dragging:
                        mouse_x, mouse_y = event.pos
                        x = mouse_x + offset_x
                        y = mouse_y + offset_y

                # ---------------------------
                #      Key down events
                # ---------------------------
                if event.type == pygame.KEYDOWN:

                    # Depth input text or delete text
                    if event.key == pygame.K_RETURN:
                        running = False

            # --------------------------------------
            #              Draw things
            # --------------------------------------

            # Background screen
            self.screen.blit(self.copy_of_screen, (0, 0))

            # Create pop up
            window_rect, top_bar_rect, exit_button = self.create_window('Options', x, y, width, height)

            # Draw option choices
            x_start, y_start = x + 10*self.theme.margin, y + self.theme.top_bar_height + 0.6 * self.theme.sq_size
            y_next = 0.5*self.theme.sq_size
            x_1 = 10*self.theme.margin
            square_radius = 3*self.theme.margin

            items = [('Enable sound', sound_box), ('Forfeit on time', forfeit_box), ('Keyboard shortcuts', shortcuts_box), ('Auto flip board', flip_box)]
            buttons = []

            for i, item in enumerate(items):

                # Create text and rectangle
                self.create_text(item[0], self.theme.popup_font, self.theme.black, x_start + x_1, y_start + i * y_next, 'left')
                pygame.draw.rect(self.screen, self.theme.black, (x_start, y_start + i * y_next - square_radius, 2 * square_radius, 2 * square_radius), 1, border_radius=1)

                # Mark with X if option is chosen
                if item[1]:
                    pygame.draw.line(self.screen, self.theme.black, (x_start, y_start + i*y_next - square_radius), (x_start + 2 * square_radius - 1, y_start + i*y_next + square_radius - 1), 1)
                    pygame.draw.line(self.screen, self.theme.black, (x_start, y_start + i*y_next + square_radius - 1), (x_start + 2 * square_radius - 1, y_start + i*y_next - square_radius), 1)

                # Buttons
                buttons.append(self.create_button('', self.theme.popup_font, self.theme.light_blue, self.theme.light_blue,
                            (x_start, y_start + i*y_next - square_radius, 2 * square_radius, 2 * square_radius), False, False))

            # Okay button
            okay_button = self.create_okay_button(x, y, width, height)

            # Update screen
            pygame.display.flip()

# ---------------------------------------------------------------------------------------------------------
#
#                                  Helper functions
#
# ---------------------------------------------------------------------------------------------------------

    # Create the pop up window shell
    def create_window(self, text, x, y, width, height):

        # Background
        window_rect = pygame.Rect((x, y, width, height))
        self.create_button('', self.theme.popup_font, self.theme.light_grey, self.theme.grey[4], window_rect, True, True)

        # Title and line
        top_bar_rect = self.create_button('', self.theme.popup_font, self.theme.white, self.theme.grey[5], (x, y, width, self.theme.top_bar_height + 4 * self.theme.margin), True, True)
        exit_button = self.create_button('', self.theme.popup_font_bold, self.theme.light_red, self.theme.light_red,
                                         (x + width - int(self.theme.sq_size / 2.6), y + 4 * self.theme.margin / 2, int(self.theme.sq_size / 3.25), self.theme.top_bar_height), True, True)
        self.create_text('X', self.theme.popup_font_bold, self.theme.black, x + width - int(self.theme.sq_size / 3.3), y + self.theme.popup_font_bold.get_height() / 2 + 4 * self.theme.margin / 1.1,
                         'left')
        self.create_text(text, self.theme.popup_font_bold, self.theme.black, x + 4 * self.theme.margin, y + self.theme.popup_font_bold.get_height() / 2 + 4 * self.theme.margin / 1.1, 'left')

        return window_rect, top_bar_rect, exit_button

    # Creates the Okay button at the end
    def create_okay_button(self, x, y, width, height):

        okay_button = self.create_button('', self.theme.popup_font, self.theme.light_blue, self.theme.grey[5],
                                         (x + 0.5*width - 1.2*self.theme.popup_font.get_height(), y + height - 2.35*self.theme.popup_font.get_height(),
                                          2.6*self.theme.popup_font.get_height(), self.theme.popup_font.get_height() + 4*self.theme.margin),
                                         True, True)
        self.create_text('Okay', self.theme.popup_font_bold, self.theme.black, x + 0.5*width, y + height - 1.7*self.theme.popup_font.get_height(), 'center')

        return okay_button

    # Create a text object and blit on screen
    def create_text(self, text, font, color, x, y, pos):
        text = font.render(text, True, color)
        text_rect = text.get_rect()

        if pos == 'left':
            text_rect.midleft = (x, y)
        elif pos == 'right':
            text_rect.midright = (x, y)
        elif pos == 'center':
            text_rect.center = (x, y)

        self.screen.blit(text, text_rect)

    # Create a button, blit on screen and return the rect object
    def create_button(self, text, font, color, color_border, box, boxed, filled):
        text = font.render(text, True, color)
        text_rect = text.get_rect()
        text_rect.midleft = (box[0], box[1])

        rect_button = pygame.Rect(box)

        # Print the button outline
        if boxed:
            if filled:
                pygame.draw.rect(self.screen, color, rect_button, border_radius=1)
                pygame.draw.rect(self.screen, color_border, rect_button, 1, border_radius=1)
            else:
                pygame.draw.rect(self.screen, color_border, rect_button, 1)

        self.screen.blit(text, text_rect)

        return rect_button

