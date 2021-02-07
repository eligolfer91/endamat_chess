# ---------------------------------------------------------------------------------------------------------
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
#
#                                          gui_theme.py
#
#                   - Sends back a theme to the gui based on the input
#
# /////////////////////////////////////////////////////////////////////////////////////////////////////////
# ---------------------------------------------------------------------------------------------------------

import pygame


class Theme:

    def __init__(self):

        # Path to theme images
        self.path = '..\\gui\\imgs'

        # Icon
        self.icon = pygame.image.load(f'{self.path}/icon.ico')

        # Options
        self.toggle_sound = True
        self.forfeit_on_time = False
        self.enable_shortcuts = True
        self.auto_flip = True

        # Timings
        self.fixed_depth = 0
        self.movetime = 0
        self.stoptime = 0
        self.tot_time = 180
        self.inc = 0

        self.movestogo = 50
        self.timeset = 0

        # Start fen
        self.start_fen = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'

    def get_theme(self, theme, win_width=900):

        # Index to decide which theme is chosen
        index = {'Black and Gold': 0, 'Blue and White': 1}[theme]

        # --------------------------------------------------------------
        #                   Window parameters
        # --------------------------------------------------------------

        # Width and height
        self.win_width = win_width
        self.win_height = int(self.win_width/1.05)

        # Extra parameters
        self.sq_size = int(self.win_width / 12)
        self.top_bar_height = int(0.35 * self.sq_size)
        self.board_offset = int(0.4 * self.sq_size)
        self.margin = int(self.sq_size/32.5)

        # Fonts
        pygame.font.init()

        self.button_font = pygame.font.SysFont('Helvetica', int(self.sq_size * 0.26), bold=True)
        self.pv_font = pygame.font.SysFont('Times', int(self.sq_size * 0.21))
        self.board_font = pygame.font.SysFont('Times', int(self.sq_size * 0.35))

        self.menu_font = pygame.font.SysFont('Times', self.top_bar_height - int(self.sq_size / 7))
        self.menu_font_bold = pygame.font.SysFont('Times', self.top_bar_height - int(self.sq_size / 7), bold=True)

        self.popup_font_small = pygame.font.SysFont('Times', self.top_bar_height - int(self.sq_size / 6))
        self.popup_font = pygame.font.SysFont('Times', self.top_bar_height - int(self.sq_size / 7.2))
        self.popup_font_bold = pygame.font.SysFont('Times', self.top_bar_height - int(self.sq_size / 7.2), bold=True)

        self.clock_title_font = pygame.font.SysFont('Times', int(self.sq_size * 0.28))
        self.clock_font = pygame.font.SysFont('Times', int(self.sq_size * 0.35))
        self.clock_move_font = pygame.font.SysFont('Times', int(self.sq_size * 0.25))

        self.fen_font = pygame.font.SysFont('Times', self.top_bar_height - int(self.sq_size / 6.1))

        # --------------------------------------------------------------
        #                      Image choices
        # --------------------------------------------------------------

        bg_themes = [pygame.image.load(f'{self.path}\\black_gold\\bg.png'),
                     pygame.image.load(f'{self.path}\\blue_white\\bg.jpg')][index]
        board_edge_themes = [pygame.image.load(f'{self.path}\\black_gold\\edge.jpg'),
                             pygame.image.load(f'{self.path}\\blue_white\\edge.jpg')][index]

        pv_edge_themes = [pygame.image.load(f'{self.path}\\black_gold\\edge.jpg'),
                          pygame.image.load(f'{self.path}\\blue_white\\edge.jpg')][index]
        pv_image_themes = [pygame.image.load(f'{self.path}\\black_gold\\pv_background.jpg'),
                           pygame.image.load(f'{self.path}\\blue_white\\pv_background.jpg')][index]

        clock_edge_themes = [pygame.image.load(f'{self.path}\\black_gold\\edge.jpg'),
                          pygame.image.load(f'{self.path}\\blue_white\\edge.jpg')][index]
        clock_image_themes = [pygame.image.load(f'{self.path}\\black_gold\\pv_background.jpg'),
                           pygame.image.load(f'{self.path}\\blue_white\\pv_background.jpg')][index]

        pieces_themes = [pygame.image.load(f'{self.path}\\black_gold\\pieces.png'),
                         pygame.image.load(f'{self.path}\\blue_white\\pieces.png')][index]

        light_square_themes = [pygame.transform.rotate(pygame.image.load(f'{self.path}\\black_gold\\light_square.jpg'), 0),
                               pygame.transform.rotate(pygame.image.load(f'{self.path}\\blue_white\\light_square.jpg'), 0)][index]
        dark_square_themes = [pygame.transform.rotate(pygame.image.load(f'{self.path}\\black_gold\\dark_square.jpg'), 0),
                              pygame.transform.rotate(pygame.image.load(f'{self.path}\\blue_white\\dark_square.jpg'), 90)][index]

        # --------------------------------------------------------------
        #                     Transform images
        # --------------------------------------------------------------

        self.bg = pygame.transform.smoothscale(bg_themes, (self.win_width, self.win_height))
        self.board_edge = pygame.transform.smoothscale(board_edge_themes, (8*self.sq_size + 4*self.margin, 8*self.sq_size + 4*self.margin))

        self.pv_width = self.win_width - 2*self.board_offset + 4*self.margin
        self.pv_height = self.win_height - 8*self.sq_size - 3*self.board_offset - self.top_bar_height
        self.pv_edge = pygame.transform.smoothscale(pv_edge_themes, (self.pv_width, self.pv_height))
        self.pv_image = pygame.transform.smoothscale(pv_image_themes, (self.pv_width - 4*self.margin, self.pv_height - 4*self.margin))

        self.clock_width = self.win_width - 8*self.sq_size - 3*self.board_offset
        self.clock_height = int(self.sq_size*1.5)
        self.clock_edge = pygame.transform.smoothscale(clock_edge_themes, (self.clock_width, self.clock_height))
        self.clock_image = pygame.transform.smoothscale(clock_image_themes, (self.clock_width - 4*self.margin, self.clock_height - 4*self.margin))

        self.piece_images = {}
        sprite = pygame.transform.smoothscale(pieces_themes, (self.sq_size*6, self.sq_size*2))
        pieces = ['wK', 'wQ', 'wB', 'wN', 'wR', 'wp', 'bK', 'bQ', 'bB', 'bN', 'bR', 'bp']
        for i in range(2):
            for j in range(6):
                self.piece_images[pieces[i*6 + j]] = pygame.Surface.subsurface(sprite, (j*self.sq_size, i*self.sq_size, self.sq_size, self.sq_size))

        self.light_square = [0]*64
        light_square_sprite = pygame.transform.smoothscale(light_square_themes, (self.sq_size*8, self.sq_size*8))
        for i in range(8):
            for j in range(8):
                self.light_square[i*8 + j] = pygame.Surface.subsurface(light_square_sprite, (j*self.sq_size, i*self.sq_size, self.sq_size, self.sq_size))

        self.dark_square = [0]*64
        dark_square_sprite = pygame.transform.smoothscale(dark_square_themes, (self.sq_size * 8, self.sq_size * 8))
        for i in range(8):
            for j in range(8):
                self.dark_square[i*8 + j] = pygame.Surface.subsurface(dark_square_sprite, (j * self.sq_size, i * self.sq_size, self.sq_size, self.sq_size))

        # --------------------------------------------------------------
        #                           Colors
        # --------------------------------------------------------------

        # Normal
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)
        self.gold = (200, 175, 55)
        self.red = (255, 0, 0)
        self.light_blue = (173, 216, 230)
        self.check_red = (200, 12, 12)
        self.light_red = (249, 59, 59)
        self.green = (0, 255, 0)
        self.orange = (255, 128, 0)
        self.grey = [(x * 32, x * 32, x * 32) for x in reversed(range(1, 8))]  # Grey scale, from light to dark
        self.light_grey = (240, 240, 240)

        # Transparent
        alpha = [90, 140][index]
        self.orange_t = (255, 128, 0, alpha)
        self.green_t = (0, 255, 0, alpha)
        self.green_t_promo = (0, 255, 0, int(alpha/4))
        self.check_red_t = (200, 12, 12, alpha)
        self.blue_t = (173, 216, 230, alpha*1.4)
        self.grey_t = [(x * 32, x * 32, x * 32, alpha) for x in reversed(range(1, 8))]  # Grey scale, from light to dark

        self.board_text_color = [self.gold, self.light_blue][index]
        self.button_text_color = [self.white, self.white][index]


