import pygame
import chess

from square import Square

from pieces.pawn import Pawn
from pieces.king import King
from pieces.bishop import Bishop
from pieces.knight import Knight
from pieces.rook import Rook
from pieces.queen import Queen


class Board:
    def __init__(self, width, height, colourDict, colourKey, sanMoves, uciMoves):
        #dimensions of the chess board
        self.width = width
        self.height = height
        # square dimensions are the board's dimensions divided by 8
        # floor division is used here to prevent floats
        self.sqWidth = width // 8
        self.sqHeight = height // 8
        
        # colour attributes
        self.colourDict = colourDict
        self.colourKey = colourKey

        # moves notation lists
        self.sanMoves = sanMoves
        self.uciMoves = uciMoves

        # chess game attributes
        self.selectedPiece = None
        self.turn = "white"
        # an array stores the state of the game in terms of piece notation
        # e.g. "p" = black pawn and "P" = white pawn
        # this array can be fed into the AI algorithm, to determine the best move
        # inital setup for the chess board is as follows:
        self.boardArray = [
            ['r', 'n', 'b', 'q', 'k', 'b', 'n', 'r'],
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['', '', '', '', '', '', '', ''],
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'],
            ['R', 'N', 'B', 'Q', 'K', 'B', 'N', 'R']
        ]
        # list of Square objects
        self.squares = self.create_squares()
        self.occupy_squares()
        # stalemate flag
        self.isStalemate = False

        # chess.Board object
        self.chessBoard = chess.Board()

    
    # creates a list of Square objects
    def create_squares(self):
        squareList = []
        for y in range(8):
            for x in range(8):
                squareList.append(
                    Square(x, y, self.sqWidth, self.sqHeight, self.colourDict, self.colourKey))
        return squareList

    
    # gets the square object from a position vector
    def get_square_from_pos(self, pos):
        for square in self.squares:
            # if the position vector matches the square's grid coordinates
            if square.pos == pos:
                return square

    
    # gets the piece object from a position vector
    def get_piece_from_pos(self, pos):
        return self.get_square_from_pos(pos).occupyingPiece

    
    # gets the position tuple from a chess coordinate e.g. (5,5) from e4
    def get_pos_from_coord(self, coordinate):
        cols = "abcdefgh"
        # x coordinate is the index of the letter in the cols list
        # y coordinate is the differnce between the 8 and the number in the coordinate
        return (cols.index(coordinate[0]), 8 - int(coordinate[1]))

        
    # occupies the squares on the board with pieces
    def occupy_squares(self):
        # each iteration looks at the y coordinate and each row as a list
        for y, row in enumerate(self.boardArray):
            # each iteration looks at the x coordinate and each element in the row
            for x, piece in enumerate(row):
                if piece != "":
                    
                    # square object at this position
                    square = self.get_square_from_pos((x, y))
    
                    # if the piece is black or white
                    if piece.isupper():
                        pieceColour = "white"
                    else:
                        pieceColour = "black"
    
                    # Checking occupying piece for what type it is
                    # if the piece is a pawn
                    if piece.upper() == "P":
                        square.occupyingPiece = Pawn(x, y, pieceColour, self)
    
                    # if the piece is a Knight
                    elif piece.upper() == "N":
                        square.occupyingPiece = Knight(x, y, pieceColour, self)
    
                    # if the piece is a Bishop
                    elif piece.upper() == "B":
                        square.occupyingPiece = Bishop(x, y, pieceColour, self)
    
                    # if the piece is a Rook
                    elif piece.upper() == "R":
                        square.occupyingPiece = Rook(x, y, pieceColour, self)
    
                    # if the piece is a Queen
                    elif piece.upper() == "Q":
                        square.occupyingPiece = Queen(x, y, pieceColour, self)
    
                    # if the piece is a King
                    elif piece.upper() == "K":
                        square.occupyingPiece = King(x, y, pieceColour, self)
    
                # No piece here
                elif piece == "": 
                    # square object at this position
                    square = self.get_square_from_pos((x, y))
                    
                    square.occupyingPiece = None

    # handles the mouse click
    def handle_click(self, mouseX, mouseY):
        # find the integer coordinates of the chessboard from mouse coordinates
        #subtract padding then floor divide by square width
        x = (mouseX - 20) // self.sqWidth
        y = (mouseY - 20) // self.sqHeight
        pos = (x, y)
        clickedSquare = self.get_square_from_pos(pos)
    
        # if there is no selected piece currently
        if self.selectedPiece == None:
            # does the clicked square contain a piece?
            if clickedSquare.occupyingPiece != None:
                # does this piece belong to the current player?
                if clickedSquare.occupyingPiece.colour == self.turn:
                    # make this piece the selected piece
                    self.selectedPiece = clickedSquare.occupyingPiece
    
        # does .move() return True?
        # can the selected piece move to the clicked square legally?
        elif self.selectedPiece.move(self, clickedSquare):
            self.turn = "white" if self.turn == "black" else "black"
            self.selectedPiece = None
    
        # is there a piece on the clicked square?
        elif clickedSquare.occupyingPiece != None:
            # does this piece belong to the current player?
            if clickedSquare.occupyingPiece.colour == self.turn:
                # make this piece the selected piece
                self.selectedPiece = clickedSquare.occupyingPiece

    # determines if a player is in check
    # the parameter colour describes the player supposedly in check
    def in_check(self, colour, boardChange=None): # boardChange is like [(x1,y1), (x2,y2)]
        output = False
        kingPos = None
        # piece that moves according to boardChange
        movingPiece = None
        # squares at the positions given in boardChange
        oldSquare = None
        newSquare = None
        # piece originally on the new square
        newSquareOriginalPiece = None

        if boardChange != None:
            # find the old square
            oldSquare = self.get_square_from_pos(boardChange[0])
            # sets the moving piece to the piece currently on the old square
            movingPiece = oldSquare.occupyingPiece
            # chnages the old square's occupying piece to None
            oldSquare.occupyingPiece = None

            # find the new square
            newSquare = self.get_square_from_pos(boardChange[1])
            # sets the newSquareOriginalPiece
            newSquareOriginalPiece = newSquare.occupyingPiece
            # changes the new square's occupying piece to the moving piece
            newSquare.occupyingPiece = movingPiece
            movingPiece.x = boardChange[1][0]
            movingPiece.y = boardChange[1][1]


        # creates a list of all the pieces on the board
        pieces = []
        for i in self.squares:
            if i.occupyingPiece != None:
                pieces.append(i.occupyingPiece)

        # finds the king
        # if a board change is given
        if boardChange != None:
            # if the moving piece is a king
            if movingPiece.notation == "K":
                kingPos = newSquare.pos

        # if the moving piece is not the king, so it has not been found
        # or if there was no board change to begin with
        if kingPos == None:
            for piece in pieces:
                if piece.notation == "K" and piece.colour == colour:
                    kingPos = piece.pos

        # finds the squares being attacked
        for piece in pieces:
            # if the piece is the opposite colour
            if piece.colour != colour:
                # for each square being attacked
                for square in piece.attacking_squares(self):
                    # if the attacked square has the king on it
                    if square.pos == kingPos:
                        output = True

        # reset the value of the old and new squares
        if boardChange != None:
            oldSquare.occupyingPiece = movingPiece
            movingPiece.x = boardChange[0][0]
            movingPiece.y = boardChange[0][1]
            newSquare.occupyingPiece = newSquareOriginalPiece

        return output
        

    # function to determine if a player is in checkmate,
    # also determines if a player is in stalemate, and updates the global variable associated with it
    # the parameter colour describes the player supposedly in checkmate
    def is_checkmate(self, colour):
        output = False
        legalMoves = False
        check = False
        # creates a list of all the pieces on the board of the same colour
        pieces = []
        for i in self.squares:
            if i.occupyingPiece != None and i.occupyingPiece.colour == colour:
                pieces.append(i.occupyingPiece)
    
        # for every piece of the same colour
        for piece in pieces:
            # if a legal moves was already found
            if legalMoves:
                break
            # if a piece does have some valid moves
            elif piece.get_valid_moves(self) != []:
                legalMoves = True
                break
    
        # if there is check on the board right now
        if self.in_check(colour):
            check = True
    
        # if check is true and legalMoves is false
        # this means that the player is in checkmate
        if (not legalMoves) and check:
            output = True
    
        # if the player is in stalemate
        if (not legalMoves) and (not check):
            self.isStalemate = True
    
        return output


    # method to draw the whole board
    def draw_board(self, screen):
        # determines squares to highlight
        if self.selectedPiece != None:
            # highlight the selected piece
            self.get_square_from_pos(self.selectedPiece.pos).highlight = True
            for square in self.selectedPiece.get_valid_moves(self):
                # highlight the squares the selected piece can move to 
                square.highlight = True
    
        # draws the squares
        for square in self.squares:
            square.draw(screen)


    # method to get piece values
    def get_piece_value(self, piece, x, y, endgame):
        # if there is no piece
        if piece == None:
            return 0

        # piece square tables

        # piece square table for pawns
        whitePawnValues = [[0,  0,  0,  0,  0,  0,  0,  0],
                           [50, 50, 50, 50, 50, 50, 50, 50],
                           [10, 10, 20, 30, 30, 20, 10, 10],
                           [5,  5, 10, 25, 25, 10,  5,  5],
                           [0,  0,  0, 20, 20,  0,  0,  0],
                           [5, -5,-10,  0,  0,-10, -5,  5],
                           [5, 10, 10,-20,-20, 10, 10,  5],
                           [0,  0,  0,  0,  0,  0,  0,  0]]

        blackPawnValues = list(reversed(whitePawnValues))
        
        # piece square table for knights
        whiteKnightValues = [[-50,-40,-30,-30,-30,-30,-40,-50],
                             [-40,-20,  0,  0,  0,  0,-20,-40],
                             [-30,  0, 10, 15, 15, 10,  0,-30],
                             [-30,  5, 15, 20, 20, 15,  5,-30],
                             [-30,  0, 15, 20, 20, 15,  0,-30],
                             [-30,  5, 10, 15, 15, 10,  5,-30],
                             [-40,-20,  0,  5,  5,  0,-20,-40],
                             [-50,-40,-30,-30,-30,-30,-40,-50]]

        blackKnightValues = list(reversed(whiteKnightValues))

        # piece square table for bishops
        whiteBishopValues = [[-20,-10,-10,-10,-10,-10,-10,-20],
                             [-10,  0,  0,  0,  0,  0,  0,-10],
                             [-10,  0,  5, 10, 10,  5,  0,-10],
                             [-10,  5,  5, 10, 10,  5,  5,-10],
                             [-10,  0, 10, 10, 10, 10,  0,-10],
                             [-10, 10, 10, 10, 10, 10, 10,-10],
                             [-10,  5,  0,  0,  0,  0,  5,-10],
                             [-20,-10,-10,-10,-10,-10,-10,-20]]

        blackBishopValues = list(reversed(whiteBishopValues))

        # piece square table for rooks
        whiteRookValues = [[0,  0,  0,  0,  0,  0,  0,  0],
                             [5, 10, 10, 10, 10, 10, 10,  5],
                            [-5,  0,  0,  0,  0,  0,  0, -5],
                            [-5,  0,  0,  0,  0,  0,  0, -5],
                            [-5,  0,  0,  0,  0,  0,  0, -5],
                            [-5,  0,  0,  0,  0,  0,  0, -5],
                            [-5,  0,  0,  0,  0,  0,  0, -5],
                             [0,  0,  0,  5,  5,  0,  0,  0]]

        blackRookValues = list(reversed(whiteRookValues))

        # piece square table for queens
        whiteQueenValues = [[-20,-10,-10, -5, -5,-10,-10,-20],
                            [-10,  0,  0,  0,  0,  0,  0,-10],
                            [-10,  0,  5,  5,  5,  5,  0,-10],
                             [-5,  0,  5,  5,  5,  5,  0, -5],
                              [0,  0,  5,  5,  5,  5,  0, -5],
                            [-10,  5,  5,  5,  5,  5,  0,-10],
                            [-10,  0,  5,  0,  0,  0,  0,-10],
                            [-20,-10,-10, -5, -5,-10,-10,-20]]

        blackQueenValues = list(reversed(whiteQueenValues))

        # piece square table for kings middle game
        whiteKingValuesMiddleGame = [[-30,-40,-40,-50,-50,-40,-40,-30],
                                     [-30,-40,-40,-50,-50,-40,-40,-30],
                                     [-30,-40,-40,-50,-50,-40,-40,-30],
                                     [-30,-40,-40,-50,-50,-40,-40,-30],
                                     [-20,-30,-30,-40,-40,-30,-30,-20],
                                     [-10,-20,-20,-20,-20,-20,-20,-10],
                                      [20, 20,  0,  0,  0,  0, 20, 20],
                                      [20, 30, 300,  0,  0, 10, 300, 20]]

        blackKingValuesMiddleGame = list(reversed(whiteKingValuesMiddleGame))

        # piece square table for kings end game
        whiteKingValuesEndGame = [[-50,-40,-30,-20,-20,-30,-40,-50],
                                  [-30,-20,-10,  0,  0,-10,-20,-30],
                                  [-30,-10, 20, 30, 30, 20,-10,-30],
                                  [-30,-10, 30, 40, 40, 30,-10,-30],
                                  [-30,-10, 30, 40, 40, 30,-10,-30],
                                  [-30,-10, 20, 30, 30, 20,-10,-30],
                                  [-30,-30,  0,  0,  0,  0,-30,-30],
                                  [-50,-30,-30,-30,-30,-30,-30,-50]]

        blackKingValuesEndGame = list(reversed(whiteKingValuesEndGame))

        # calculate piece value
        pieceValue = 0

        # if it is a white chess piece
        if piece.color == chess.WHITE:
            if piece.piece_type == chess.PAWN:
                pieceValue += 100 + whitePawnValues[y][x]

            elif piece.piece_type == chess.KNIGHT:
                pieceValue += 320 + whiteKnightValues[y][x]

            elif piece.piece_type == chess.BISHOP:
                pieceValue += 330 + whiteBishopValues[y][x]

            elif piece.piece_type == chess.ROOK:
                pieceValue += 500 + whiteRookValues[y][x]

            elif piece.piece_type == chess.QUEEN:
                pieceValue += 900 + whiteQueenValues[y][x]

            elif piece.piece_type == chess.KING:
                if endgame:
                    pieceValue += 10000 + whiteKingValuesEndGame[y][x]
                else:
                    pieceValue += 10000 + whiteKingValuesMiddleGame[y][x]

        # if it is a black chess piece
        elif piece.color == chess.BLACK:
            if piece.piece_type == chess.PAWN:
                pieceValue += -100 - blackPawnValues[y][x]

            elif piece.piece_type == chess.KNIGHT:
                pieceValue += -320 - blackKnightValues[y][x]

            elif piece.piece_type == chess.BISHOP:
                pieceValue += -330 - blackBishopValues[y][x]

            elif piece.piece_type == chess.ROOK:
                pieceValue += -500 - blackRookValues[y][x]

            elif piece.piece_type == chess.QUEEN:
                pieceValue += -900 - blackQueenValues[y][x]

            elif piece.piece_type == chess.KING:
                if endgame:
                    pieceValue += -10000 - blackKingValuesEndGame[y][x]
                else:
                    pieceValue += -10000 - blackKingValuesMiddleGame[y][x]

        return pieceValue


    
    # method to get evaluation of the board
    def get_evaluation(self, board):
        # check if it is endgame or middle game
        whiteQueenAlive = False
        blackQueenAlive = False
    
        for i in self.squares:
            if i.occupyingPiece != None:
                if i.occupyingPiece.notation == "Q":
                    if i.occupyingPiece.colour == "white":
                        whiteQueenAlive = True
                    elif i.occupyingPiece.colour == "black":
                        blackQueenAlive = True
    
        # endgame is reached once there are no queens of either type left
        endgame = False if (whiteQueenAlive and blackQueenAlive) else True
    
        # evaluation of the board, this will be returned to the main program
        eval = 0

        # if the board in in checkmate
        if board.is_checkmate():
            if self.turn == "white":
                eval = -10000
                return eval
            else:
                eval = 10000
                return eval

        # if the board is in stalemate
        if board.is_stalemate():
            eval = 0
            return eval
            
    
        # iterating through every piece
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                # exit this iteration and move onto next square
                continue
            else:
                eval += self.get_piece_value(piece,
                                            # x position on the board
                                            self.get_pos_from_coord(chess.square_name(square))[0],
                                            # y position on the board
                                            self.get_pos_from_coord(chess.square_name(square))[1],
                                            endgame)
    
        return eval
                                        
                
    # method to get the best move for the computer
    def minimax(self, board, depth, isMaximizingPlayer, alpha, beta):
        # if the node is a leaf node, or the game is over
        if depth == 0 or board.is_game_over():
            return self.get_evaluation(board), None

        legalMoves = list(board.legal_moves)
        # if it is the maximising player's turn (white)
        if isMaximizingPlayer:
            # numerical value at node
            maxVal = float("-inf")
            # chess.Move at node
            bestMove = None
            # for every legal move
            for move in legalMoves:
                # get value of the child node
                board.push(move)
                self.turn = "white" if self.turn == "black" else "black"
                val = self.minimax(board, depth - 1, False, alpha, beta)
                try:
                    val = val[0]
                except:
                    pass
                board.pop()
                self.turn = "white" if self.turn == "black" else "black"

                # if the value of the child node is greater than the current max value
                # update maxVal and bestMove
                if val > maxVal:
                    maxVal = val
                    bestMove = move

                # alpha-beta pruning, break if beta <= alpha
                alpha = max(alpha, maxVal)
                if beta <= alpha:
                    break
            # return numerical value and chess.Move object
            return maxVal, bestMove

        # if it is the minimising player's turn (black)
        else:
            # numerical value at node
            minVal = float("inf")
            # chess.Move at node
            bestMove = None
            # for every legal move
            for move in legalMoves:
                # get value of the child node
                board.push(move)
                self.turn = "white" if self.turn == "black" else "black"
                val = self.minimax(board, depth - 1, True, alpha, beta)
                try:
                    val = val[0]
                except:
                    pass
                board.pop()
                self.turn = "white" if self.turn == "black" else "black"

                # if the value of the child node is greater than the current max value
                # update maxVal and bestMove
                if val < minVal:
                    minVal = val
                    bestMove = move

                # alpha-beta pruning, break if beta <= alpha
                beta = min(beta, minVal)
                if beta <= alpha:
                    break
            # return numerical value and chess.Move object
            return minVal, bestMove
            

    # method to make move for the AI
    def make_AI_move(self, board, depth):
        # get the best move
        aiMove = self.minimax(board, 
                              depth, 
                              True if self.turn == "white" else False, 
                              float("-inf"), 
                              float("inf"))[1]

        # get a uci notation of the move
        uciMove = aiMove.uci()
        print(f"this is uci {uciMove}")

        # identify the starting and ending squares
        startPos = self.get_pos_from_coord(uciMove[:2])
        endPos = self.get_pos_from_coord(uciMove[2:4])
        # get the piece that is moving
        piece = self.get_piece_from_pos(startPos)
        # get the square it is moving to
        endSquare = self.get_square_from_pos(endPos)

        # move the piece
        piece.move(self, endSquare)

        # change the turn of the board
        self.turn = "black" if self.turn == "white" else "white"
