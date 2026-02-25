import pygame
from piece import Piece


# unique rook class
class Rook(Piece):
    def __init__(self, x, y, colour, board):
        super().__init__(x, y, colour, board)
        imgPath = 'images/' + colour + '_rook.png'
        self.img = pygame.image.load(imgPath)
        # transform image to fit squares
        self.img = pygame.transform.scale(self.img, (board.sqWidth-25, board.sqHeight-10))
        # rook's notation
        self.notation = "R"


    # method to get the possible moves of the rook based on movement rules
    def get_possible_moves(self, board):
        possibleMoves = []
        # all the possible moves of the rook from its position (0, 0)
        vectorMoves = []

        # north moves, where vector is like (0, -k)
        nVectors = []
        for i in range(1, 8):
            # if the move is within the board
            if self.y - i >= 0:
                nVectors.append((0, -i))

        # west moves, where vector is like (-k, 0)
        wVectors = []
        for i in range(1, 8):
            # if the move is within the board
            if self.x - i >= 0:
                wVectors.append((-i, 0))

        # south moves, where vector is like (0, k)
        sVectors = []
        for i in range(1, 8):
            # if the move is within the board
            if self.y + i <= 7:
                sVectors.append((0, i))

        # east moves, where vector is like (k, 0)
        eVectors = []
        for i in range(1, 8):
            # if the move is within the board
            if self.x + i <= 7:
                eVectors.append((i, 0))

        vectorMoves = [nVectors, wVectors, sVectors, eVectors]
        
        # for each movement vector
        for direction in vectorMoves:
            # list for a direction of the bishop
            directionMoves = []
            for vector in direction:
                newPos = (self.x + vector[0], self.y + vector[1])
                directionMoves.append(board.get_square_from_pos(newPos))
            # add direction list of moves to possibleMoves
            possibleMoves.append(directionMoves)

        return possibleMoves
