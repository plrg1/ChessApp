import pygame
from piece import Piece


# unique pawn class
class Pawn(Piece):
    def __init__(self, x, y, colour, board):
        super().__init__(x, y, colour, board)
        imgPath = 'images/' + colour + '_pawn.png'
        self.img = pygame.image.load(imgPath)
        # transform image to fit squares
        self.img = pygame.transform.scale(self.img, (board.sqWidth-30, board.sqHeight-20))
        # san notation
        self.notation = ''


    # method to get the forward moves of the piece, if such a square exists
    def get_possible_moves(self, board):
        # list of square objects to move to
        possibleMoves = []
        # list of position vectors that the pawn can move to from its position at (0,0)
        vectorMoves = []
    
        # moving forward
        if self.colour == 'white':
            vectorMoves.append((0, -1))
            if not self.hasMoved:
                vectorMoves.append((0, -2))
        elif self.colour == "black":
            vectorMoves.append((0, 1))
            if not self.hasMoved:
                vectorMoves.append((0, 2))
    
        for vector in vectorMoves:
            newPos = (self.x + vector[0], self.y + vector[1])
            if newPos[0] >= 0 and newPos[0] <= 7 and newPos[1] >= 0 and newPos[1] <= 7:
                possibleMoves.append(board.get_square_from_pos(newPos))
    
        return possibleMoves
                

    # method to get all the moves of the pawn, including captures, disregarding illegality due to check
    def get_moves(self, board):
        moves = []
        # check all forward moves
        for square in self.get_possible_moves(board):
            if square.occupyingPiece == None:
                moves.append(square)
            else:
                break
    
        # diagonal moves
        # white pawn
        if self.colour == "white":
            # right diagonal
            if self.x + 1 <= 7 and self.y - 1 >= 0:
                square = board.get_square_from_pos((self.x + 1, self.y - 1))
    
                # if the right diagonal square contains an enemy piece
                if square.occupyingPiece != None:
                    if square.occupyingPiece.colour != self.colour:
                        moves.append(square)
            # left diagonal
            if self.x - 1 >= 0 and self.y - 1 >= 0:
                square = board.get_square_from_pos((self.x - 1, self.y - 1))
    
                # if the left diagonal square contains an enemy piece
                if square.occupyingPiece != None:
                    if square.occupyingPiece.colour != self.colour:
                        moves.append(square)
    
        # black pawn
        if self.colour == "black":
            # right diagonal
            if self.x - 1 >= 0 and self.y + 1 <= 7:
                square = board.get_square_from_pos((self.x - 1, self.y + 1))
    
                # if the right diagonal square contains an enemy piece
                if square.occupyingPiece != None:
                    if square.occupyingPiece.colour != self.colour:
                        moves.append(square)
            # left diagonal
            if self.x + 1 <= 7 and self.y + 1 <= 7:
                square = board.get_square_from_pos((self.x + 1, self.y + 1))
    
                # if the left diagonal square contains an enemy piece
                if square.occupyingPiece != None:
                    if square.occupyingPiece.colour != self.colour:
                        moves.append(square)
    
        return moves


    # method to return only attacking squares of the pawn
    def attacking_squares(self, board):
        attackingSquares = []
        for move in self.get_moves(board):
            # if the final square of the move is on a different file to the pawn
            if move.x != self.x:
                attackingSquares.append(move)
        return attackingSquares
