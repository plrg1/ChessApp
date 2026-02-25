import pygame

class Square:
    def __init__(self, x, y, width, height, colourDict, colourKey, padding=20):
        # basic parameters specifying size and position
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        # true position on screen
        self.trueX = (x * width) + padding
        self.trueY = (y * height) + padding
        
        # colour parameters
        self.colourDict = colourDict
        self.colourKey = colourKey
        
        # additional attributes
        self.pos = (x,y) # x,y coordinate position in terms of integers
        self.colour = "light" if (x+y) % 2 == 0 else "dark" # square's colour
        # Square's colour hex value
        self.drawColour = self.colourDict[self.colourKey][0] if self.colour == "light" else self.colourDict[self.colourKey][1]
        # Square's colour hex value when highlighted
        self.highlightColour = self.colourDict[self.colourKey][2] if self.colour == "light" else self.colourDict[self.colourKey][3]
        # piece occupying the square
        self.occupyingPiece = None 
        # whether the square is highlighted
        self.highlight = False 
        # square's coordinate in terms of letters and numbers
        self.coordinate = self.get_coordinate() 
        
        # pygame rect object
        self.rect = pygame.Rect(self.trueX, self.trueY, self.width, self.height)


    def get_coordinate(self):
        # returns the square's coordinate in terms of letters and numbers
        cols = "abcdefgh"
        return cols[self.x] + str(8-self.y) 

    def draw(self, display):
        # draws the square on the screen
        if self.highlight: #if highlighted
            pygame.draw.rect(display, self.highlightColour, self.rect)
        else:
            pygame.draw.rect(display, self.drawColour, self.rect)

        #draws the piece occupying the square
        if self.occupyingPiece != None:
            # create a surface the same size as the piece's sprite
            centerRect = self.occupyingPiece.img.get_rect()
            # center this new surface onto the square
            centerRect.center = self.rect.center
            # blit the piece onto the square
            display.blit(self.occupyingPiece.img, centerRect.topleft)
