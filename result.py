import pygame
import pygame_widgets
from pygame_widgets.button import Button
from pygame_widgets.textbox import TextBox

class SearchResult:
    def __init__(self, display, x, y, width, height, text1, text2, text3, gameID, command=None):
        self.display = display
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text1 = text1
        self.text2 = text2
        self.text3 = text3
        self.gameID = gameID
        self.command = command

        #first texbox to hold the date the game was played on
        self.textbox1 = TextBox(self.display,
                               self.x,
                               self.y,
                               self.width/5,
                               self.height,
                               fontSize=15,
                               colour=pygame.Color("darkred"),
                               borderThickness=1)
        self.textbox1.disable()
        self.textbox1.setText(self.text1)

        # second textbox to hold the length of the game played
        self.textbox2 = TextBox(self.display,
                               self.x + self.width/5,
                               self.y,
                               self.width/5,
                               self.height,
                               fontSize=15,
                               colour=pygame.Color("darkred"),
                               borderThickness=1)
        self.textbox2.disable()
        self.textbox2.setText(self.text2)

        # third textbox to hold the first couple moves of the game played
        self.textbox3 = TextBox(self.display,
                               self.x + (2*self.width/5),
                               self.y,
                               7*self.width/15,
                               self.height,
                               fontSize=15,
                               colour=pygame.Color("darkred"),
                               borderThickness=1)
        self.textbox3.disable()
        self.textbox3.setText(self.text3)

        #button to choose the game
        self.button = Button(self.display,
                             self.x + (13*self.width/15),
                             self.y,
                             2*self.width/15,
                             self.height,
                             text="→",
                             fontSize=15,
                             margin=10,
                             inactiveColour=pygame.Color("darkred"), # colour when not hovered over
                             hoverColour=(100,0,0), # colour when hovered over
                             pressedColour=(0,0,0), # colour when pressed
                             onClick=self.command)
