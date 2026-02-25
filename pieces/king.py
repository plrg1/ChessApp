import pygame
from piece import Piece


# unique king class
class King(Piece):
    def __init__(self, x, y, colour, board):
        super().__init__(x, y, colour, board)
        imgPath = 'images/' + colour + '_king.png'
        self.img = pygame.image.load(imgPath)
        # transform image to fit squares
        self.img = pygame.transform.scale(self.img, (board.sqWidth-25, board.sqHeight-10))
        # king's notation
        self.notation = "K"


    # method to get the possible moves of the king based on movement rules
    def get_possible_moves(self, board):
        possibleMoves = []
        # all the possible moves of the king from its position (0, 0)
        vectorMoves = [(1, 0),
                      (1, 1),
                      (0, 1),
                      (-1, 1),
                      (-1, 0),
                      (-1, -1),
                      (0, -1),
                      (1, -1)]
    
        # for each movement vector
        for vector in vectorMoves:
            newPos = (self.x + vector[0], self.y + vector[1])
            # does the king fit within the chess board
            if newPos[0] >= 0 and newPos[0] <= 7 and newPos[1] >= 0 and newPos[1] <= 7:
                possibleMoves.append([board.get_square_from_pos(newPos)])
    
        return possibleMoves


    # method to check if the king can castle kingside
    def can_castle_kingside(self, board):
        # if the king is not in check
        if not board.in_check(self.colour):
            # if the king has not moved yet
            if not self.hasMoved:


                # for the white king
                if self.colour == "white":
                    kingsideRook = board.get_piece_from_pos((7, 7))
                    # if the rook has not moved yet
                    if kingsideRook != None:
                        if not kingsideRook.hasMoved:
                            piecesBetween = [board.get_piece_from_pos((i,7)) for i in range(5,7)]
                            # if the squares in between are empty
                            if piecesBetween == [None,None]:
                                # finding enemy pieces
                                enemyPieces = []
                                for x in range(0,8):
                                    for y in range(0,8):
                                        if board.get_piece_from_pos((x,y)) != None:
                                            if board.get_piece_from_pos((x,y)).colour != self.colour:
                                                enemyPieces.append(board.get_piece_from_pos((x,y)))
                                # if an enemy piece attacks any of the squares ...
                                # between the king and the rook
                                square1 = board.get_square_from_pos((5,7))
                                square2 = board.get_square_from_pos((6,7))
                                for enemy in enemyPieces:
                                    if (square1 in enemy.attacking_squares(board) or                                                                    square2 in enemy.attacking_squares(board)
                                    ):
                                        return False

                                return True
                            # squares in between are not empty
                            else:
                                return False
                        # rook has moved, another piece is there
                        else:
                            return False
                    # no piece where rook should be
                    else:
                        return False


                # for the black king
                if self.colour == "black":
                    kingsideRook = board.get_piece_from_pos((7, 0))
                    # if the rook has not moved yet
                    if kingsideRook != None:
                        if not kingsideRook.hasMoved:
                            piecesBetween = [board.get_piece_from_pos((i,0)) for i in range(5,7)]
                            # if the squares in between are empty
                            if piecesBetween == [None,None]:
                                # finding enemy pieces
                                enemyPieces = []
                                for x in range(0,8):
                                    for y in range(0,8):
                                        if board.get_piece_from_pos((x,y)) != None:
                                            if board.get_piece_from_pos((x,y)).colour != self.colour:
                                                enemyPieces.append(board.get_piece_from_pos((x,y)))
                                # if an enemy piece attacks any of the squares ...
                                # between the king and the rook
                                square1 = board.get_square_from_pos((5,0))
                                square2 = board.get_square_from_pos((6,0))
                                for enemy in enemyPieces:
                                    if (square1 in enemy.attacking_squares(board) or                                                                    square2 in enemy.attacking_squares(board)
                                    ):
                                        return False

                                return True
                            # squares in between are not empty
                            else:
                                return False
                        # rook has moved, another piece is there
                        else:
                            return False
                    # no piece where rook should be
                    else:
                        return False


            # the king has moved
            else:
                return False

        # the king is in check
        else:
            return False


    # method to check if the king can castle queenside
    def can_castle_queenside(self, board):
        # if the king is not in check
        if not board.in_check(self.colour):
            # if the king has not moved yet
            if not self.hasMoved:


                # for the white king
                if self.colour == "white":
                    queensideRook = board.get_piece_from_pos((0, 7))
                    # if the rook has not moved yet
                    if queensideRook != None:
                        if not queensideRook.hasMoved:
                            piecesBetween = [board.get_piece_from_pos((i,7)) for i in range(1,4)]
                            # if the squares in between are empty
                            if piecesBetween == [None,None,None]:
                                # finding enemy pieces
                                enemyPieces = []
                                for x in range(0,8):
                                    for y in range(0,8):
                                        if board.get_piece_from_pos((x,y)) != None:
                                            if board.get_piece_from_pos((x,y)).colour != self.colour:
                                                enemyPieces.append(board.get_piece_from_pos((x,y)))
                                # if an enemy piece attacks any of the squares ...
                                # between the king and the rook
                                square1 = board.get_square_from_pos((1,7))
                                square2 = board.get_square_from_pos((2,7))
                                square3 = board.get_square_from_pos((3,7))
                                for enemy in enemyPieces:
                                    if (square1 in enemy.attacking_squares(board) or                                                                    square2 in enemy.attacking_squares(board) or                                                                    square3 in enemy.attacking_squares(board)
                                    ):
                                        return False

                                return True
                            # squares in between are not empty
                            else:
                                return False
                        # rook has moved, another piece is there
                        else:
                            return False
                    # no piece where rook should be
                    else:
                        return False


                # for the black king
                if self.colour == "black":
                    queensideRook = board.get_piece_from_pos((7, 0))
                    # if the rook has not moved yet
                    if queensideRook != None:
                        if not queensideRook.hasMoved:
                            piecesBetween = [board.get_piece_from_pos((i,0)) for i in range(1,4)]
                            # if the squares in between are empty
                            if piecesBetween == [None,None,None]:
                                # finding enemy pieces
                                enemyPieces = []
                                for x in range(0,8):
                                    for y in range(0,8):
                                        if board.get_piece_from_pos((x,y)) != None:
                                            if board.get_piece_from_pos((x,y)).colour != self.colour:
                                                enemyPieces.append(board.get_piece_from_pos((x,y)))
                                # if an enemy piece attacks any of the squares ...
                                # between the king and the rook
                                square1 = board.get_square_from_pos((1,0))
                                square2 = board.get_square_from_pos((2,0))
                                square3 = board.get_square_from_pos((3,0))
                                for enemy in enemyPieces:
                                    if (square1 in enemy.attacking_squares(board) or                                                                    square2 in enemy.attacking_squares(board) or                                                                    square3 in enemy.attacking_squares(board)
                                    ):
                                        return False

                                return True
                            # squares in between are not empty
                            else:
                                return False
                        # rook has moved, another piece is there
                        else:
                            return False
                    # no piece where rook should be
                    else:
                        return False


            # the king has moved
            else:
                return False

        # the king is in check
        else:
            return False


    # get_valid_moves method with castling added
    def get_valid_moves(self, board):
        validMoves = []
        # for every square that the king could travel to according to is movement
        # excluding squares filled by the same colour pieces
        for square in self.get_moves(board):
            if not board.in_check(self.colour, boardChange=[self.pos, square.pos]):
                validMoves.append(square)

        # kingside castling
        if self.can_castle_kingside(board):
            validMoves.append(board.get_square_from_pos((self.x + 2,self.y)))

        # queenside castling
        if self.can_castle_queenside(board):
            validMoves.append(board.get_square_from_pos((self.x - 2,self.y)))
            
        return validMoves
