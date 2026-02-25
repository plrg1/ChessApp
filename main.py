import pygame
import sys
import pygame_widgets
import random
import csv     # csv file library
import sqlite3 # database library
import datetime
import math
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox
from pygame_widgets.slider import Slider
from result import SearchResult
from vertical_bar import VerticalBar

from board import Board

#constants & global variables
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
SWITCHED = True # flag to check if a screen has just changed
TIME_SETTING = 10 #amount of minutes a chess timer runs for.
UNDO = False # flag to check if the undo button should be functional
HUMAN_SIDE = "white" # string to hold which side is playing as a human
AI_PLAYING = False # flag to check if the AI is playing
DIFFICULTY = "Easy" # string to hold the difficulty of the AI
# Colours
COLOUR_DICT = {"normal" : [(255,255,255), 
                           (0,0,0), 
                           (149,211,245), 
                           (77,111,130)],
               "red" : [(235, 221, 218), 
                        (145, 43, 15), 
                        (145, 15, 80), 
                        (224, 148, 186)],
               "yellow" : [(255,242,204),
                          (255,217,102),
                          (179,255,102),
                          (102,204,0)],
               "green" : [(213,232,212),
                         (151,208,119),
                         (102,255,211),
                         (0,204,166)],
               "blue" : [(218,232,252),
                        (126,166,224),
                        (255,189,226),
                        (204,45,156)],
               "indigo" : [(225,213,231),
                          (194, 92, 231),
                          (255, 145, 128),
                          (255, 74, 46)]
              }
# colour key value used for the chess boards
# set it to normal initially
COLOUR_KEY = "normal"

# general move lists for the current game
SAN_MOVES = []
UCI_MOVES = []
# Analyse screen move lists
ANALYSE_SAN_MOVES = []
ANALYSE_UCI_MOVES = []
# Resigning flag
RESIGN = False
# which side resigned
WHITE_RESIGNED = False
BLACK_RESIGNED = False
# Won by checkmate flags
WHITE_IS_CHECKMATED = False
BLACK_IS_CHECKMATED = False
# Won on time flags
WHITE_TIME_UP = False
BLACK_TIME_UP = False
# stalemate flag
STALEMATE = False

# sorting variables
SORT_DATE_ASC = False
SORT_DATE_DSC = False
SORT_LEN_ASC = False
SORT_LEN_DSC = False

# counter for how many moves have been shown in Analyse
COUNT = 0

# evaluation and move cycling flag
EVAL = [0.0,0.5]
JUST_MOVED = False

# database connection
con = sqlite3.connect("ChessApp.db")
cur = con.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS game_data(id PRIMARY KEY, datePlayed, length, firstMoves)""")

#global functions/procedures
# sets time setting
def set_time(time):
    global TIME_SETTING
    TIME_SETTING = time
    print(TIME_SETTING)

# toggles the undo setting
def toggle_undo():
    global UNDO
    UNDO = not UNDO
    print(UNDO)

# sets the side of the human player
def set_side(side, RANDOM=False):
    global HUMAN_SIDE
    if RANDOM:
        HUMAN_SIDE = random.choice(["white","black"])
    else:
        HUMAN_SIDE = side
    print(HUMAN_SIDE)

# decides if AI is being used or not
def use_AI(bool, screen):
    global AI_PLAYING
    AI_PLAYING = bool
    print(AI_PLAYING)
    # change screen to chess
    screen.gameStateManager.set_state("playChess")

# sets the resigning flag to true
def set_resign():
    global RESIGN
    RESIGN = True

# undoes a move on the chess board.
def undo(board):
    global UCI_MOVES
    # last move played
    lastMove = UCI_MOVES[-1]
    # piece on square to which piece moved to last move
    piece = board.get_piece_from_pos(board.get_pos_from_coord(lastMove[2:4]))
    # square which piece moved from
    startSquare = board.get_square_from_pos(board.get_pos_from_coord(lastMove[0:2]))

    piece.move(board, startSquare, force=False, undo=True)

    SAN_MOVES = board.sanMoves
    UCI_MOVES = board.uciMoves

    # change the turn
    board.turn = "white" if board.turn == "black" else "black"

# sets up the analyse screen with information from Search screen
def set_analysis(screen, IDlist):
    global SORT_DATE_ASC, SORT_DATE_DSC, SORT_LEN_ASC, SORT_LEN_DSC
    global ANALYSE_SAN_MOVES, ANALYSE_UCI_MOVES

    yVal = pygame.mouse.get_pos()[1]
    ID = IDlist[((yVal-200)//30)-1]
    # get the moves from the csv files

    # get SAN moves
    with open("san_moves.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        for index,row in enumerate(csvreader):
            if index+1 == ID:
                ANALYSE_SAN_MOVES = list(row)
                break

    # get UCI moves
    with open("uci_moves.csv", "r") as csvfile:
        csvreader = csv.reader(csvfile)
        for index,row in enumerate(csvreader):
            if index+1 == ID:
                ANALYSE_UCI_MOVES = list(row)
                break

    print(ANALYSE_SAN_MOVES)
    print(ANALYSE_UCI_MOVES)
    # change screen to analysis
    screen.gameStateManager.set_state("analyse")

# sets the sorting type
def set_sort_type(sortType, screen):
    global SORT_DATE_ASC, SORT_DATE_DSC, SORT_LEN_ASC, SORT_LEN_DSC

    # if sorting by date ascending
    if sortType == "dateAsc":
        SORT_DATE_ASC = True
        SORT_DATE_DSC = False
        SORT_LEN_ASC = False
        SORT_LEN_DSC = False

    # if sorting by date descending
    if sortType == "dateDsc":
        SORT_DATE_ASC = False
        SORT_DATE_DSC = True
        SORT_LEN_ASC = False
        SORT_LEN_DSC = False

    # if sorting by length ascending
    if sortType == "lenAsc":
        SORT_DATE_ASC = False
        SORT_DATE_DSC = False
        SORT_LEN_ASC = True
        SORT_LEN_DSC = False

    # if sorting by length descending
    if sortType == "lenDsc":
        SORT_DATE_ASC = False
        SORT_DATE_DSC = False
        SORT_LEN_ASC = False
        SORT_LEN_DSC = True

    #reset the screen
    screen.gameStateManager.set_state("search")


# shows the next move in Analyse
def next_move(board):
    global COUNT
    global ANALYSE_UCI_MOVES
    global JUST_MOVED

    # if there are no more next moves
    if COUNT == len(ANALYSE_UCI_MOVES):
        return

    # piece on that is moving
    piece = board.get_piece_from_pos(
        board.get_pos_from_coord(ANALYSE_UCI_MOVES[COUNT][0:2])
    )
    # square which piece moved from
    square = board.get_square_from_pos(
        board.get_pos_from_coord(ANALYSE_UCI_MOVES[COUNT][2:4])
    )

    # move the piece
    piece.move(board, square)

    # increment the count
    COUNT += 1

    # set JUST_MOVED to true
    JUST_MOVED = True

    # change the turn
    board.turn = "white" if board.turn == "black" else "black"


# shows the previous move in Analyse
def prev_move(board):
    global COUNT
    global ANALYSE_UCI_MOVES
    global JUST_MOVED

    # if there are no more previous moves
    if COUNT == 0:
        return

    # last move played
    lastMove = ANALYSE_UCI_MOVES[COUNT-1]

    # piece on square to which piece moved to last move
    piece = board.get_piece_from_pos(
        board.get_pos_from_coord(lastMove[2:4])
    )
    # square which piece moved from
    startSquare = board.get_square_from_pos(
        board.get_pos_from_coord(lastMove[0:2])
    )

    # undo the move, showing the previous state
    piece.move(board, startSquare, force=False, undo=True)

    # decrement the count
    COUNT -= 1

    # set JUST_MOVED to true
    JUST_MOVED = True

    # change the turn
    board.turn = "white" if board.turn == "black" else "black"


# get eval as a percentage
def get_eval_percent(board):
    global JUST_MOVED
    global EVAL
    global JUST_MOVED

    if not JUST_MOVED:
        return EVAL[1]

    # get evaluation in pawns
    eval = round(board.minimax(board.chessBoard, 
                               2, 
                               True if board.turn == "white" else False,
                               float('-inf'), 
                               float('inf')
                              )[0] / 100, 1)

    # get the percentage based on eval
    percentage = (((2/math.pi)*math.atan(eval))+1)/2

    # if the board is in checkmate and eval is ±10000
    if eval == 100:
        percentage = 1

    elif eval == -100:
        percentage = 0

    # update global variables
    EVAL = [eval, percentage]
    JUST_MOVED = False

    return percentage


# set the colourkey for the chessboards
def set_colour(requiredGames, playedGames, colour):
    global COLOUR_KEY
    global COLOUR_DICT
    # if the user has played more games than required
    if playedGames >= requiredGames:
        # if the colour specified is in the dictionary
        if colour in COLOUR_DICT.keys():
            COLOUR_KEY = colour
    else:
        pass

    print(COLOUR_KEY)



#Game class, which runs each screen
class Game:
    def __init__(self):
        #setup pygame
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        #setup different screens
        self.gameStateManager = GameStateManager("mainMenu")
        self.mainMenu = MainMenu(self.screen, self.gameStateManager)
        self.playOptions = PlayOptions(self.screen, self.gameStateManager)
        self.playChess = PlayChess(self.screen, self.gameStateManager)
        self.gameOver = GameOver(self.screen, self.gameStateManager)
        self.search = Search(self.screen, self.gameStateManager)
        self.analyse = Analyse(self.screen, self.gameStateManager)
        self.customise = Customise(self.screen, self.gameStateManager)

        self.states = {"mainMenu" : self.mainMenu, 
                       "playOptions" : self.playOptions,
                       "playChess" : self.playChess,
                       "gameOver" : self.gameOver,
                       "search" : self.search,
                       "analyse" : self.analyse,
                       "customise" : self.customise}


    def run(self):
        while True:
            self.states[self.gameStateManager.get_state()].run()


#Main menu class, which appears first when the game starts
class MainMenu:
    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager


    def run(self):
        global SWITCHED
        #background colour
        self.display.fill(pygame.Color("crimson"))

        #button that opens the play options screen
        playButton = Button(self.display, #surface placed on
            50, # x-position
            100, # y-position
            300, # Width
            100, # Height
            text="Play", 
            fontSize=30, 
            margin=20,
            inactiveColour=(71,154,154), # colour when not hovered over
            hoverColour=(22,50,50), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: self.gameStateManager.set_state("playOptions"))

        #button that opens the analyse screen
        analyseButton = Button(self.display, #surface placed on
            50, # x-position
            250, # y-position
            300, # Width
            100, # Height
            text="Analyse", 
            fontSize=30, 
            margin=20,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(51,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: self.gameStateManager.set_state("search"))

        #button that opens the customise screen
        customiseButton = Button(self.display, #surface placed on
            50, # x-position
            400, # y-position
            300, # Width
            100, # Height
            text="Customise", 
            fontSize=30, 
            margin=20,
            inactiveColour=(51,7,5), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: self.gameStateManager.set_state("customise"))

        # textboax to display ChessApp
        title = TextBox(self.display, #surface placed on
                        400,
                        250,
                        300,
                        100,
                        fontSize=70,
                        font=pygame.font.Font("OpenSans-ExtraBold.ttf", 70),
                        colour=pygame.Color("crimson"),
                        textColour=(51,7,5),
                        borderThickness=0,
                        placeholderText="ChessApp")
        title.disable()

        SWITCHED = False
        while not SWITCHED:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()



            pygame_widgets.update(pygame.event.get())
            pygame.display.update()
            pygame.time.Clock().tick(FPS)


#Options class, which appears when the play button is pressed
class PlayOptions:

    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager


    def run(self):
        global SWITCHED
        global DIFFICULTY
        # background colour
        self.display.fill((98,79,70)) #624F46
        # added background drawing
        pygame.draw.rect(self.display, (37,31,14), (30,30,740,540)) #251F0E
        pygame.draw.rect(self.display, pygame.Color("crimson"), (60,60,325,480)) #AC8C22
        pygame.draw.rect(self.display, pygame.Color("crimson"), (415,60,325,480)) #AC8C22
        # buttons onn left side
        playAIButton = Button(self.display, #surface placed on
            140, # x-position
            150, # y-position
            165, # Width
            70, # Height
            text="Play AI",
            fontSize=20,
            margin=10,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(100,0,0), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: use_AI(True, self))

        playHumanButton = Button(self.display, #surface placed on
            140, # x-position
            350, # y-position
            165, # Width
            70, # Height
            text="Play Human",
            fontSize=20,
            margin=10,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(100,0,0), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: use_AI(False, self))

        # Slider for difficulty
        sliderDict = {1:"Easy",
                     2:"Medium",
                     3:"Hard"}

        difficultySlider = Slider(self.display, #surface placed on
            455, # x-position
            100, # y-position
            245, # Width
            20, # Height
            min=100,
            max=399,
            step=1,
            colour=(0,0,0),
            handleColour=pygame.Color("darkred"))

        difficultyText = TextBox(self.display, #surface placed on
            535, # x-position
            140, # y-position
            165, # Width
            40, # Height
            fontSize=20,
            colour=pygame.Color("crimson"),
            borderThickness=0)
        difficultyText.disable()

        # Right side buttons
        setTimeButton1 = Button(self.display, # surface placed on
            445, # x-position
            200, # y-position
            70, # Width
            70, # Height
            text="2 minutes",
            fontSize=15,
            margin=10,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(100,0,0), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_time(2))

        setTimeButton2 = Button(self.display, # surface placed on
            540, # x-position
            200, # y-position
            70, # Width
            70, # Height
            text="5 minutes",
            fontSize=15,
            margin=10,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(100,0,0), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_time(5))

        setTimeButton3 = Button(self.display, # surface placed on
            635, # x-position
            200, # y-position
            70, # Width
            70, # Height
            text="10 minutes",
            fontSize=15,
            margin=10,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(100,0,0), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_time(10))

        toggleUndoButton = Button(self.display, # surface placed on
            480, # x-position
            310, # y-position
            190, # Width
            70, # Height
            text="Toggle Undo",
            fontSize=20,
            margin=10,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(100,0,0), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: toggle_undo())

        setSideWhiteButton = Button(self.display, # surface placed on
            445, # x-position
            420, # y-position
            70, # Width
            70, # Height
            text="White",
            fontSize=15,
            margin=10,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(100,0,0), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_side("white"))

        setSideBlackButton = Button(self.display, # surface placed on
            540, # x-position
            420, # y-position
            70, # Width
            70, # Height
            text="Black",
            fontSize=15,
            margin=10,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(100,0,0), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_side("black"))

        setSideRandomButton = Button(self.display, # surface placed on
            635, # x-position
            420, # y-position
            70, # Width
            70, # Height
            text="Random",
            fontSize=15,
            margin=10,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(100,0,0), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_side("random", True))

        SWITCHED = False
        while not SWITCHED:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            #floor division of slider value lets the slider move freely, but the textbox changes at the correct point.
            difficultyText.setText(sliderDict[difficultySlider.getValue() // 100])

            #update the difficulty global variable
            DIFFICULTY = difficultyText.getText()

            pygame_widgets.update(pygame.event.get())
            pygame.display.update()
            pygame.time.Clock().tick(FPS)
            #undo key
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.gameStateManager.set_state("mainMenu")


class PlayChess:

    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

    def run(self):
        global SWITCHED
        global DIFFICULTY
        global SAN_MOVES
        global UCI_MOVES
        global RESIGN

        global WHITE_RESIGNED
        global BLACK_RESIGNED
        global WHITE_IS_CHECKMATE
        global BLACK_IS_CHECKMATE
        global WHITE_TIME_UP
        global BLACK_TIME_UP
        global STALEMATE

        # reset san and uci moves list
        SAN_MOVES = []
        UCI_MOVES = []
        # background colour
        self.display.fill((37,31,14)) #251F0E

        # add background drawing
        pygame.draw.rect(self.display, pygame.Color("crimson"), (600,20,180,560)) #AC8C22

        # Widgets and other code to instantiate objects on this screen

        # chess board
        mainBoard = Board(560,560,COLOUR_DICT,COLOUR_KEY,SAN_MOVES,UCI_MOVES)

        # initialise value of RESIGN
        RESIGN = False
        # resigning button
        resignButton = Button(self.display, #surface placed on
            620, # x-position
            440, # y-position
            140, # Width
            60, # Height
            text="Resign",
            fontSize=20,
            margin=10,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(100,0,0), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_resign())  

        # creates pygame timer that returns an event every second
        incrementTimerEvent = pygame.USEREVENT + 1
        timer = pygame.time.set_timer(incrementTimerEvent, 1000)


        # black timer textbox
        blackTimer = TextBox(self.display, #surface placed on
            620, # x-position
            40, # y-position
            70, # Width
            40, # Height
            fontSize=20,
            colour=pygame.Color("darkred"),
            borderThickness=0,
            placeholderText="0:00")
        blackTimer.disable()

        # black timer time elapsed variable
        blackTimeElapsed = 0

        # white timer textbox
        whiteTimer = TextBox(self.display, #surface placed on
            620, # x-position
            520, # y-position
            70, # Width
            40, # Height
            fontSize=20,
            colour=pygame.Color("darkred"),
            borderThickness=0,
            placeholderText="0:00")
        whiteTimer.disable()

        # white timer time elapsed variable
        whiteTimeElapsed = 0

        # undo button
        undoButton = Button(self.display, #surface placed on
            720, # x-position
            520, # y-position
            50, # Width
            40, # Height
            text="Undo",
            fontSize=15,
            margin=10,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(100,0,0), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: undo(mainBoard) if not AI_PLAYING and UNDO else None)

        print(DIFFICULTY)

        SWITCHED = False
        while not SWITCHED:
            # mouse position
            mouseX, mouseY = pygame.mouse.get_pos()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                # mouse click on screen
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        # if the mouse is clicked on the chessboard
                        if (
                            mouseX > 20 and
                            mouseX < 580 and
                            mouseY > 20 and
                            mouseY < 580
                        ):
                            mainBoard.handle_click(mouseX, mouseY)

                elif event.type == incrementTimerEvent:
                    # if both players are human
                    if not AI_PLAYING:
                        # if it is white's turn
                        if mainBoard.turn == "white":
                            # increment white timer
                            whiteTimeElapsed += 1
                            # get the time in minutes and seconds
                            minutes = str(whiteTimeElapsed // 60)
                            seconds = whiteTimeElapsed % 60
                            # if seconds is less than 10, add a 0 to the front
                            if seconds < 10:
                                seconds = "0" + str(seconds)
                            else:
                                seconds = str(seconds)

                            whiteTimer.setText(f"{minutes}:{seconds}")

                        # if it is black's turn
                        if mainBoard.turn == "black":
                            # increment black timer
                            blackTimeElapsed += 1
                            # get the time in minutes and seconds
                            minutes = str(blackTimeElapsed // 60)
                            seconds = blackTimeElapsed % 60
                            # if seconds is less than 10, add a 0 to the front
                            if seconds < 10:
                                seconds = "0" + str(seconds)
                            else:
                                seconds = str(seconds)

                            blackTimer.setText(f"{minutes}:{seconds}")



            # chess board code
            # if the board reaches checkmate
            # white wins
            if mainBoard.is_checkmate("black"):
                # set white is checkmate to true
                WHITE_IS_CHECKMATE = True
                SAN_MOVES = mainBoard.sanMoves
                UCI_MOVES = mainBoard.uciMoves
                self.gameStateManager.set_state("gameOver")
                break

            #black wins
            elif mainBoard.is_checkmate("white"):
                # set black is checkmate to true
                BLACK_IS_CHECKMATE = True
                SAN_MOVES = mainBoard.sanMoves
                UCI_MOVES = mainBoard.uciMoves
                self.gameStateManager.set_state("gameOver")
                break

            # stalemate draw
            elif mainBoard.isStalemate:
                # set stalemate flag to true
                STALEMATE = True
                SAN_MOVES = mainBoard.sanMoves
                UCI_MOVES = mainBoard.uciMoves
                self.gameStateManager.set_state("gameOver")
                break

            # if the player resigns
            if RESIGN:
                if mainBoard.turn == "white":
                    # set white resigned flag to true
                    WHITE_RESIGNED = True
                elif mainBoard.turn == "black":
                    # set black resigned flag to true
                    BLACK_RESIGNED = True

                SAN_MOVES = mainBoard.sanMoves
                UCI_MOVES = mainBoard.uciMoves
                self.gameStateManager.set_state("gameOver")
                break

            # if black runs out of time
            if blackTimeElapsed >= TIME_SETTING*60:
                # set black time up flag to true
                BLACK_TIME_UP = True
                SAN_MOVES = mainBoard.sanMoves
                UCI_MOVES = mainBoard.uciMoves
                self.gameStateManager.set_state("gameOver")
                break

            # if white runs out of time
            if whiteTimeElapsed >= TIME_SETTING*60:
                # set white time up flag to true
                WHITE_TIME_UP = True
                SAN_MOVES = mainBoard.sanMoves
                UCI_MOVES = mainBoard.uciMoves
                self.gameStateManager.set_state("gameOver")
                break

            # if the AI should play in this game
            if AI_PLAYING:
                # if it is the AI's turn
                if mainBoard.turn != HUMAN_SIDE: 
                    # decide depth of search tree for minimax
                    if DIFFICULTY == "Hard":
                        depth = 4
                    elif DIFFICULTY == "Medium":
                        depth = 3
                    else:
                        depth = 2

                    # make the best move, returned from minimax
                    mainBoard.make_AI_move(mainBoard.chessBoard, depth)



            mainBoard.draw_board(self.display)

            pygame_widgets.update(pygame.event.get())
            pygame.display.update()
            pygame.time.Clock().tick(FPS)
            #undo key
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.gameStateManager.set_state("playOptions")
                pygame.time.wait(80) #waits so that the key is unpressed


class GameOver:

    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

    def run(self):
        global SWITCHED
        global con
        global cur
        # background colour
        self.display.fill(pygame.Color("darkred")) #251F0E

        # add background drawing
        pygame.draw.rect(self.display, pygame.Color("crimson"), (100,100,600,400))

        # Widgets and other code to instantiate objects on this screen
        # return to menu button
        returnToMenuButton = Button(self.display, #surface placed on
            150, # x-position
            350, # y-position
            200, # Width
            100, # Height
            text="Return to Menu",
            fontSize=20,
            margin=10,
            inactiveColour=(71,154,154), # colour when not hovered over
            hoverColour=(22,50,50), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: self.gameStateManager.set_state("mainMenu"))

        # go to analyser button
        goToAnalyseButton = Button(self.display, #surface placed on
            450, # x-position
            350, # y-position
            200, # Width
            100, # Height
            text="Analyse this Game",
            fontSize=20,
            margin=10,
            inactiveColour=(71,154,154), # colour when not hovered over
            hoverColour=(22,50,50), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: self.gameStateManager.set_state("analyse"))


        # database and csv file writing
        # database

        # get the number of games already stored
        con.commit()
        result = cur.execute("SELECT id FROM game_data")
        numberOfGames = len(result.fetchall())

        if result.fetchall() is None:
            # if there are no games stored
            numberOfGames = 0


        # new id of game
        newID = str(numberOfGames + 1)

        # get the date today
        date = str(datetime.datetime.now())[0:10]

        # get the length of the game played
        length = str(len(SAN_MOVES))

        # get the first few moves
        firstMoves = ""
        # if the game has at least 6 moves
        if len(SAN_MOVES) > 6:
            for i in range(0, 6, 2):
                firstMoves += f"{int((i/2)+1)}. " + SAN_MOVES[i] + " " + SAN_MOVES[i+1] + " "
        else:
            for i in range(0, len(SAN_MOVES), 2):
                # add moves in pairs as many times as possible
                try:
                    firstMoves += f"{int((i/2)+1)}. " + SAN_MOVES[i] + " " + SAN_MOVES[i+1] + " "
                except:
                    break


        # write to the database
        cur.execute(f"""
        INSERT INTO game_data VALUES
            ({newID}, '{date}', {length}, '{firstMoves}')
            """)
        con.commit()



        # write to the csv file
        # SAN moves
        with open("san_moves.csv", 'a') as csvfile:
            # create a csv writer object
            csvwriter = csv.writer(csvfile)
            # write the data
            csvwriter.writerow(SAN_MOVES)

        # UCI moves
        with open("uci_moves.csv", 'a') as csvfile:
            # create a csv writer object
            csvwriter = csv.writer(csvfile)
            # write the data
            csvwriter.writerow(UCI_MOVES)


        SWITCHED = False
        while not SWITCHED:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame_widgets.update(pygame.event.get())
            pygame.display.update()
            pygame.time.Clock().tick(FPS)
            #undo key
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.gameStateManager.set_state("mainMenu")
                pygame.time.wait(80) #waits so that the key is unpressed


class Search:

    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

    def run(self):
        global SWITCHED
        global con
        global cur

        global SORT_DATE_ASC
        global SORT_DATE_DSC
        global SORT_LENGTH_ASC
        global SORT_LENGTH_DSC

        # background colour
        self.display.fill((37,31,14)) #251F0E
        # added background drawing
        pygame.draw.rect(self.display, pygame.Color("crimson"), (30,30,740,540)) #251F0E

        # Widgets and other code to instantiate objects on this screen

        # create search results
        # creates search results list
        searchResults = []
        # open database to get values for each game
        cur.execute("SELECT * FROM game_data")
        gameData = cur.fetchall()

        # sort the data by date ascending
        if SORT_DATE_ASC:
            gameData = sorted(gameData, key=lambda x: datetime.date(
                int(x[1].split("-")[0]),
                int(x[1].split("-")[1]),
                int(x[1].split("-")[2])
            ),
                             reverse=False)

        # sort the data by date decending
        if SORT_DATE_DSC:
            gameData = sorted(gameData, key=lambda x: datetime.date(
                int(x[1].split("-")[0]),
                int(x[1].split("-")[1]),
                int(x[1].split("-")[2])
            ),
                             reverse=True)

        # sort the data by length ascending
        if SORT_LEN_ASC:
            gameData = sorted(gameData, key=lambda x: int(x[2]), reverse = False)

        # sort the data by length decending
        if SORT_LEN_DSC:
            gameData = sorted(gameData, key=lambda x: int(x[2]), reverse = True)


        # get id's sorted
        sortedIDs = [x[0] for x in gameData]

        for index, game in enumerate(gameData):
            # get the position of the result in the sorted list
            position = index + 1
            # get the id of the game
            id = int(game[0])
            # get the date of the game
            date = game[1]
            # get the length of the game
            length = game[2]
            # get the first few moves
            firstMoves = game[3]

            # create SearchResult object
            searchResult = SearchResult(self.display,
                                        50,
                                        200+(position*30), # y-position
                                        700,
                                        30,
                                        date,
                                        length,
                                        firstMoves,
                                        id,
                                        command=lambda: set_analysis(self, sortedIDs))

            # add search result to list
            searchResults.append(searchResult)

        # create sorting buttons

        # sort by date ascending
        sortDateAscButton = Button(self.display, #surface placed on
            100, # x-position
            130, # y-position
            135, # Width
            70, # Height
            text="Sort Date Ascending",
            fontSize=10,
            margin=10,
            inactiveColour=(51,7,5), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_sort_type("dateAsc", self))

        # sort by date descending
        sortDateDscButton = Button(self.display, #surface placed on
            255, # x-position
            130, # y-position
            135, # Width
            70, # Height
            text="Sort Date Descending",
            fontSize=10,
            margin=10,
            inactiveColour=(51,7,5), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_sort_type("dateDsc", self))

        # sort by length ascending
        sortLenAscButton = Button(self.display, #surface placed on
            410, # x-position
            130, # y-position
            135, # Width
            70, # Height
            text="Sort Length Ascending",
            fontSize=10,
            margin=10,
            inactiveColour=(51,7,5), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_sort_type("lenAsc", self))

        # sort by length descending
        sortLenDscButton = Button(self.display, #surface placed on
            565, # x-position
            130, # y-position
            135, # Width
            70, # Height
            text="Sort Length Descending",
            fontSize=10,
            margin=10,
            inactiveColour=(51,7,5), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_sort_type("lenDsc", self))



        SWITCHED = False
        while not SWITCHED:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame_widgets.update(pygame.event.get())
            pygame.display.update()
            pygame.time.Clock().tick(FPS)
            #undo key
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.gameStateManager.set_state("mainMenu")
                pygame.time.wait(80) #waits so that the key is unpressed


class Analyse:

    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

    def run(self):
        global SWITCHED
        global ANALYSE_SAN_MOVES
        global ANALYSE_UCI_MOVES
        global COUNT
        global EVAL

        EVAL = [0.0, 0.5]

        COUNT = 0

        # background colour
        self.display.fill((37,31,14)) #251F0E

        # add background drawing
        pygame.draw.rect(self.display, pygame.Color("crimson"), (600,20,180,560))

        # Widgets and other code to instantiate objects on this screen

        # chess board
        analyseBoard = Board(560,560,COLOUR_DICT,COLOUR_KEY,[],[])





        # create eval textbox
        evalScore = TextBox(self.display, #surface placed on
            620, # x-position
            40, # y-position
            90, # Width
            60, # Height
            fontSize=20,
            colour=pygame.Color("darkred"),
            borderThickness=0,)
        evalScore.disable()  

        # background of moves list
        pygame.draw.rect(self.display, (71,154,154), (620,120,90,380)) #AC8C22

        # list of textboxes
        movesTextList = []
        for i in range(0, len(ANALYSE_UCI_MOVES), 2):
            # create textbox
            moveSet = TextBox(self.display, #surface placed on
                620, # x-position
                120+(i*8), # y-position
                90, # Width
                20, # Height
                fontSize=8,
                colour=(71,154,154),
                borderThickness=0,)
            moveSet.disable()    

            # add move set to list
            movesTextList.append(moveSet)

        # next move button
        nextButton = Button(self.display, #surface placed on
            670, # x-position
            520, # y-position
            40, # Width
            40, # Height
            text="→", 
            fontSize=30, 
            margin=20,
            inactiveColour=(51,7,5), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: next_move(analyseBoard))

        # next move button
        prevButton = Button(self.display, #surface placed on
            620, # x-position
            520, # y-position
            40, # Width
            40, # Height
            text="←", 
            fontSize=30, 
            margin=20,
            inactiveColour=(51,7,5), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: prev_move(analyseBoard))

        # create vertical bar
        evalBar = VerticalBar(self.display, #surface placed on
                              730,
                              40,
                              30,
                              520,
                              lambda: get_eval_percent(analyseBoard),
                              completedColour=(255,255,255),
                              incompletedColour=(0,0,0))

        SWITCHED = False
        while not SWITCHED:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # draw the analysis board
            analyseBoard.draw_board(self.display)

            # get current moves and add to moves Text
            currentMoves = ANALYSE_SAN_MOVES[0:COUNT]
            for i, move in enumerate(currentMoves):
                # skip all odd instances of i
                if i % 2 == 1:
                    continue
                # calculate which textbox to use
                boxNum = i//2
                # get the textbox
                textbox = movesTextList[boxNum]
                # set the text
                # if the current move is the last
                if move == currentMoves[-1]:
                    textbox.setText(f"{(i//2)+1}. {move}")
                else:
                    textbox.setText(f"{(i//2)+1}. {move} {currentMoves[i+1]}")

            # clear unecessary text
            for i in range((COUNT+1)//2, len(movesTextList)):
                movesTextList[i].setText("")


            # get evaluation in pawns
            eval = EVAL[0]

            if eval == 100 or eval == -100:
                eval = "Mate"

            # set eval text
            evalScore.setText(f"{eval}")



            pygame_widgets.update(pygame.event.get())
            pygame.display.update()
            pygame.time.Clock().tick(FPS)
            #undo key
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.gameStateManager.set_state("search")
                pygame.time.wait(80) #waits so that the key is unpressed



class Customise:

    def __init__(self, display, gameStateManager):
        self.display = display
        self.gameStateManager = gameStateManager

    def run(self):
        global SWITCHED

        # background colour
        self.display.fill((71, 154, 154)) #479A9A

        # background drawings
        pygame.draw.rect(self.display, pygame.Color("crimson"), (30,30,740,540))
        pygame.draw.rect(self.display, (51,7,5) , (50,50,340,500))
        pygame.draw.rect(self.display, (51,7,5) , (410,50,340,500))

        # customisation buttons 

        # get the number of games played
        with open("san_moves.csv", "r", newline='') as csvfile:
            csvreader = csv.reader(csvfile)
            numGames = 0
            # iterate through each record and count them
            for record in csvreader:
                numGames += 1

        # board buttons

        # normal board button
        normalBoardButton = Button(self.display, #surface placed on
            430, # x-position
            70, # y-position
            300, # Width
            70, # Height
            text="Normal Board [No games]", 
            fontSize=15, 
            margin=20,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_colour(0, numGames, 'normal'))

        # red board button
        redBoardButton = Button(self.display, #surface placed on
            430, # x-position
            148, # y-position
            300, # Width
            70, # Height
            text="Red Board [1 games]", 
            fontSize=15, 
            margin=20,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_colour(1, numGames, 'red'))

        # yellow board button
        yellowBoardButton = Button(self.display, #surface placed on
            430, # x-position
            226, # y-position
            300, # Width
            70, # Height
            text="Yellow Board [2 games]", 
            fontSize=15, 
            margin=20,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_colour(2, numGames, 'yellow'))

        # green board button
        greenBoardButton = Button(self.display, #surface placed on
            430, # x-position
            304, # y-position
            300, # Width
            70, # Height
            text="Green Board [3 games]", 
            fontSize=15, 
            margin=20,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_colour(3, numGames, 'green'))

        # blue board button
        blueBoardButton = Button(self.display, #surface placed on
            430, # x-position
            382, # y-position
            300, # Width
            70, # Height
            text="Blue Board [5 games]", 
            fontSize=15, 
            margin=20,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_colour(5, numGames, 'blue'))

        # indigo board button
        indigoBoardButton = Button(self.display, #surface placed on
            430, # x-position
            460, # y-position
            300, # Width
            70, # Height
            text="Indigo Board [9 games]", 
            fontSize=15, 
            margin=20,
            inactiveColour=pygame.Color("darkred"), # colour when not hovered over
            hoverColour=(31,7,5), # colour when hovered over
            pressedColour=(0,0,0), # colour when pressed
            onClick=lambda: set_colour(9, numGames, 'indigo'))

        SWITCHED = False
        while not SWITCHED:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            pygame_widgets.update(pygame.event.get())
            pygame.display.update()
            pygame.time.Clock().tick(FPS)
            #undo key
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                self.gameStateManager.set_state("mainMenu")
                pygame.time.wait(80) #waits so that the key is unpressed


#Game state manager class, which manages the game states
class GameStateManager:
    def __init__(self, currentState):
        self.currentState = currentState

    def get_state(self):
        return self.currentState

    def set_state(self, newState):
        global SWITCHED
        self.currentState = newState
        SWITCHED = True
        print(f"Switched to {newState}")



game = Game()
game.run()
