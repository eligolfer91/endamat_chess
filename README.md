# Introduction
Endamat Chess is a chess program/engine written in Python as a hobby project to learn more about programming in general. The program includes a GUI in which you can play against another human or against the built in AI, and also the ability to connect the engine to an external (UCI compatible) GUI.

# Getting started
**Use in external GUI:** In the exe-folder you find the .exe file which you can use to install the engine in an external GUI. You can find all communication and logic in the uci.py file.

**Use in own GUI:** To use the own GUI you need to (pip) install the following modules (tested with Python 3.9.2):

- pygame
- pyperclip
- numpy

The program should be independent of OS, but please let me know if any issues arise if you run it in any other OS than Windows. 

# Own GUI
Playing Endamat Chess in its own GUI is very simple. You can run the command "python gui_main.py" in the terminal from the gui folder. Or you can open up gui_main.py in your favorite IDE and play from there.
<figure>
    <img src='https://user-images.githubusercontent.com/59540119/107938077-1cd53380-6f85-11eb-91ed-0051704c616b.png' alt='missing' width="70%" height="70%" />
    <figcaption><i>Sample view of the Endamat Chess GUI during a game against the AI in the opening stage.</i></figcaption>
  <br>
  <br>
</figure>

You move the pieces by dragging and dropping them on the board. All possibles squares for a piece lights up when you start dragging.

**Chose time control:** 
The default time control is 3 minutes with 2 seconds of increment. You can change the time control by Game-Time control in the top menu bar. You can chose to let the engine think to a specific depth per move, use a certain time per move, or put in the total game time (minutes, seconds, increment per move).

**Options:** 
You can chose some basic game options under File-Options. By default you will not lose by time to the AI, you can use as much time as you want. 

**Themes:** 
There are 2 themes included which you can switch between under Board in the menu bar. You can also add your own theme in the gui_theme.py file by chosing image files and other theme settings.

### Useful keyboard shortcuts
- **n-key**: Start a new game.
- **f-key**: Flip the board.
- **z-key**: Undo the latest move.
- **c-key**: Copy FEN string of current position to clipboard.
- **p-key**: Pause the game.

# Game features
Affinity Chess supports the rules of normal chess.
- [X] Checkmate and stalemate detection
- [X] Castling
- [X] Enpassant
- [X] Pawn promotion to Queen, Rook, Bishop, or Knight
- [X] Draw by:
  - 3 fold repetition
  - 50 move rule
  
Draw by insufficient material is not yet implemented.
  
# AI
The AI is based on a Negamax algorithm with features/optimizations such as Iterative deepening, Aspiration window, Quiescence search, Null move, and some sorting techniques such as to try PV-line first, Killer moves, MVV-LVA and History moves. Parts regarding Transposition Table and Late Move Reduction are commented out since they currently doens't work.

# Evaluation function

The evaluation function is located in evaluation.py. Some parameters such as the PST values are updated in the move/unmake move functions in gamestate.py. 

Endamat Chess in its current state only uses 2 sets of PST for evaluation, one set for opening phase and one set for endgame. The PST values are interpolated to get values for the current gamestate.

For late endgame it also uses a special evaluation function to drive the opponent king towards the edge of the board and find mate. 

Note that the evaluation score given by the AI in the GUI is always from the AI perspective. A positive score means the AI thinks its ahead and a negative score means it thinks the human is ahead, no matter what color it plays. 

# Tests

### Perft
If you make changes to the code you can test that the legal move generator is working properly through perft.py which you find in the tests folder. You have two options to chose from: 

1. A shorter version with some critical test positions including castling prevented king and queen side, promotion, promotion in/out of check, enpassant moves, discovered checks, double checks and more. The positions are found in 'test_positions/short.txt'. The test takes around 5 minutes to run. 

2. A complete test including around 6500 randomly selected test positions, found in 'test_positions/full.txt'. The test takes around 24 hours to run.

To change to the full test you simply change the test_file variable at the top of perft.py to 'full' and run as normal.



