import pygame
from piece import Piece


# unique bishop class
class Bishop(Piece):
    def __init__(self, x, y, colour, board):
        super().__init__(x, y, colour, board)
        imgPath = 'images/' + colour + '_bishop.png'
        self.img = pygame.image.load(imgPath)
        # transform image to fit squares
        self.img = pygame.transform.scale(self.img, (board.sqWidth-25, board.sqHeight-10))
        # bishop's notation
        self.notation = "B"


    # method to get the possible moves of the bishop based on movement rules
    def get_possible_moves(self, board):
        possibleMoves = []
        # all the possible moves of the bishop from its position (0, 0)
        vectorMoves = []

        # north east moves, where vector is like (k, -m)
        neVectors = []
        for i in range(1, 8):
            # if the move is within the board
            if self.x + i <= 7 and self.y - i >= 0:
                neVectors.append((i, -i))
        
        # south east moves, where vector is like (k, m)
        seVectors = []
        for i in range(1, 8):
            # if the move is within the board
            if self.x + i <= 7 and self.y + i <= 7:
                seVectors.append((i, i))
        
        # south west moves, where vector is like (-k, m)
        swVectors = []
        for i in range(1, 8):
            # if the move is within the board
            if self.x - i >= 0 and self.y + i <= 7:
                swVectors.append((-i, i))
        
        # north west moves, where vector is like (-k, -m)
        nwVectors = []
        for i in range(1, 8):
            # if the move is within the board
            if self.x - i >= 0 and self.y - i >= 0:
                nwVectors.append((-i, -i))
        
        
        vectorMoves = [neVectors, seVectors, swVectors, nwVectors]
        
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
