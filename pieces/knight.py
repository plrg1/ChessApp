import pygame
from piece import Piece


# unique knight class
class Knight(Piece):
    def __init__(self, x, y, colour, board):
        super().__init__(x, y, colour, board)
        imgPath = 'images/' + colour + '_knight.png'
        self.img = pygame.image.load(imgPath)
        # transform image to fit squares
        self.img = pygame.transform.scale(self.img, (board.sqWidth-25, board.sqHeight-10))
        # knight's notation
        self.notation = "N"


    # method to get the possible moves of the knight based on movement rules
    def get_possible_moves(self, board):
        possibleMoves = []
        # all the possible moves of the knight from its position (0, 0)
        vectorMoves = [(1, 2),
                      (1, -2),
                      (-1, 2),
                      (-1, -2),
                      (2, 1),
                      (2, -1),
                      (-2, 1),
                      (-2, -1)]

        # for each movement vector
        for vector in vectorMoves:
            newPos = (self.x + vector[0], self.y + vector[1])
            # does the knight fit within the chess board
            if newPos[0] >= 0 and newPos[0] <= 7 and newPos[1] >= 0 and newPos[1] <= 7:
                possibleMoves.append([board.get_square_from_pos(newPos)])

        return possibleMoves
