from math import sin

from PyQt6.QtCore import QRectF
from PyQt6.QtSvg import QSvgRenderer


class Human:
    def __init__(self, x, y, speed, is_going):
        self.x = x
        self.y = y
        self.speed = speed
        self.state = 'queue'
        self.up = 0
        self.is_going = is_going
        self.standing_renderer = QSvgRenderer('man.svg')
        self.walking_renderer = QSvgRenderer('going_man.svg')

    def move(self):
        if self.state in ['queue', 'exit']:
            self.y = 345 - abs(sin(self.x / 10)) * 15
        if self.state == 'queue':
            self.y = 765 - abs(sin(self.x / 10)) * 15
            self.x += self.speed
        elif self.state == 'escalator':
            self.x += self.speed * 1.2 if self.is_going else self.speed
            self.y = int(325 + (900 - self.x) * 0.53) - (
                abs(sin(self.x / 10)) * 15 if self.is_going else 0)
        elif self.state == 'exit':
            self.x += self.speed
        elif self.state == 'out':
            self.x = -50
            self.y = 765

    def draw(self, painter):
        ((self.walking_renderer if self.is_going else self.standing_renderer)
         .render(painter, QRectF(self.x, self.y - 65, 70, 100)))

    def look(self):
        if self.x > 1400:
            self.state = 'out'
        elif self.x > 873:  # у выхода
            self.state = 'exit'
        elif self.x < 100:  # у входа на эскалатор
            self.state = 'queue'
        else:  # на эскалаторе
            self.state = 'escalator'
