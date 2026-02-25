import pygame
import chess

class Piece:
    def __init__(self, x, y, colour, board):
        self.x = x
        self.y = y
        self.pos = (x, y)
        self.board = board
        self.colour = colour
        self.hasMoved = False

    # method to get the moves of the piece
    # eliminates squares that aren't empty and can't be captured
    def get_moves(self, board):
        moves = []
        # for every square that the piece could travel to according to is movement
        for direction in self.get_possible_moves(board):
            for square in direction:
                # if there is a piece of the same colour on the square
                if square.occupyingPiece != None:
                    if square.occupyingPiece.colour == self.colour:
                        break
                    else:
                        # if there is a piece of the opposite colour on the square
                        moves.append(square)
                        break
                # if there is no piece on the square
                else:
                    moves.append(square)
    
        return moves


    # method to get the moves of the piece
    # eliminates squares that when moved to result in check
    def get_valid_moves(self, board):
        validMoves = []
        # for every square that the piece could travel to according to is movement
        # excluding squares filled by the same colour pieces
        for square in self.get_moves(board):
            if not board.in_check(self.colour, boardChange=[self.pos, square.pos]):
                validMoves.append(square)
    
        return validMoves


    # method to move the piece to a specified square.
    # also output the move's notation in san and uci
    def move(self, board, square, force=False, undo=False):
        
        # undo a move
        if undo:
            # update the chessBoard attribute
            board.chessBoard.pop()
            # get a 2D array from the chessBoard attribute
            boardString = str(board.chessBoard)
            row8 = boardString[0:16].split()
            row7 = boardString[16:32].split()
            row6 = boardString[32:48].split()
            row5 = boardString[48:64].split()
            row4 = boardString[64:80].split()
            row3 = boardString[80:96].split()
            row2 = boardString[96:112].split()
            row1 = boardString[112:128].split()

            row8 = list(map(lambda x: x.replace(".", ""), row8))
            row7 = list(map(lambda x: x.replace(".", ""), row7))
            row6 = list(map(lambda x: x.replace(".", ""), row6))
            row5 = list(map(lambda x: x.replace(".", ""), row5))
            row4 = list(map(lambda x: x.replace(".", ""), row4))
            row3 = list(map(lambda x: x.replace(".", ""), row3))
            row2 = list(map(lambda x: x.replace(".", ""), row2))
            row1 = list(map(lambda x: x.replace(".", ""), row1))

            board.boardArray = [row8, row7, row6, row5, row4, row3, row2, row1]
            board.occupy_squares()

            # removes moves from the moves lists
            board.sanMoves.pop()
            board.uciMoves.pop()

            return True
            
        # remove highlight
        for highlightedSquare in board.squares:
            highlightedSquare.highlight = False
    
        # if the move is valid, or the paramter force is true
        # force is used to ignore valid moves, specifically for castling
        if square in self.get_valid_moves(board) or force:
            # move notation
            uciMove = ""
            sanMove = ""
            
            # update the square's attributes
            oldSquare = board.get_square_from_pos(self.pos)
            self.pos = square.pos
            self.x = square.x
            self.y = square.y
            # change the occupying piece
            oldSquare.occupyingPiece = None
            newSquareOldPiece = square.occupyingPiece
            square.occupyingPiece = self
            # remove piece selection and set hasMoved to true
            board.selectedPiece = None
            self.hasMoved = True
            
            # add to uci notation
            uciMove += oldSquare.get_coordinate()
            uciMove += square.get_coordinate()
    
            # add to san notation
            # if the piece moved is a pawn add the file it moved from to the move notation
            # otherwise add the otation of the piece itself.
            sanMove += self.notation
            # if the piece captured another piece and is a pawn
            sanMove += oldSquare.get_coordinate()[0] if (newSquareOldPiece != None and 
                                                         self.notation == "") else ""
            # if the piece captured another piece
            sanMove += "x" if newSquareOldPiece != None else ""
            # add coordinate of new square
            sanMove += square.get_coordinate()
    
            # pawn promotion
            if self.notation == "":
                # if the pawn has reached the end of the board (last or first rank)
                if self.y == 0 or self.y == 7:
                    from pieces.queen import Queen
                    # replace occupying piece
                    square.occupyingPiece = Queen(self.x, self.y, self.colour, board)
                    # finish notation
                    sanMove += "=Q"
                    uciMove += "q"
    
            # castling
            if self.notation == "K":
                # if long castle
                if oldSquare.x - self.x == 2:
                    # rook at the same rank as king
                    rook = board.get_piece_from_pos((0, self.y))
                    # force the move, ignore is the move is valid for the rook or not.
                    # move rook to the d-file
                    rook.move(board, board.get_square_from_pos((3, self.y)), force=True)
    
                    # update san
                    sanMove = "O-O-O"
                # if short castle
                elif oldSquare.x - self.x == -2:
                    # rook at the same rank as king
                    rook = board.get_piece_from_pos((7, self.y))
                    # force the move, ignore is the move is valid for the rook or not.
                    # move rook to the f-file
                    rook.move(board, board.get_square_from_pos((5, self.y)), force=True)
    
                    # update san
                    sanMove = "O-O"
    

            # for all moves except rook's movement when castling
            if force == False:
                board.uciMoves.append(uciMove)
                board.sanMoves.append(sanMove)
                # update the board.chessBoard
                board.chessBoard.push(chess.Move.from_uci(uciMove))
            
            # return True if the move was successful
            return True, 
            
        else:
            board.selectedPiece = None
            return False


    # method that returns the attacking squares of a piece
    def attacking_squares(self, board):
        # in all cases except the pawn
        return self.get_moves(board)
