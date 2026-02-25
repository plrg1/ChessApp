from typing import Callable
import pygame
import pygame_widgets
from pygame_widgets.progressbar import ProgressBar

class VerticalBar(ProgressBar):
    # __init__ method is the same, so no need to redefine it

    # rewrite draw method
    def draw(self):
        """ Display to surface """
        self.percent = min(max(self.progress(), 0), 1)

        if not self._hidden:
            if self.curved:
                if self.percent == 0:
                    pygame.draw.circle(self.win, self.incompletedColour,
                                       (self._x, self._y + self._height // 2), self.radius)
                    pygame.draw.circle(self.win, self.incompletedColour,
                                       (self._x + self._width, self._y + self._height // 2),
                                       self.radius)
                elif self.percent == 1:
                    pygame.draw.circle(self.win, self.completedColour,
                                       (self._x, self._y + self._height // 2), self.radius)
                    pygame.draw.circle(self.win, self.completedColour,
                                       (self._x + self._width, self._y + self._height // 2),
                                       self.radius)
                else:
                    pygame.draw.circle(self.win, self.completedColour, 
                                       (self._x, self._y + self._height // 2),
                                       self.radius)
                    pygame.draw.circle(self.win, self.incompletedColour,
                                       (self._x + self._width, self._y + self._height // 2),
                                       self.radius)

            # edited part
            # replace self.width with self.height
            pygame.draw.rect(self.win, 
                             self.completedColour,
                             (self._x, 
                              self._y, 
                              self._width, 
                              int(self._height * self.percent)))

            pygame.draw.rect(self.win, 
                             self.incompletedColour,
                             (self._x , 
                              self._y + int(self._height * self.percent), 
                              self._width, 
                              int(self._height * (1 - self.percent))))
