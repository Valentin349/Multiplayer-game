import pygame as pg
import json
from setting import *
vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, width, height):
        pg.sprite.Sprite.__init__(self)

        self.data = {
            "x": 200,
            "y": 200,

            "player": None,
            "lifes": 0,
            "colour": None
        }
        self.width = width
        self.height = height
        self.colour = self.data["colour"]
        self.image = pg.Surface((width,height))
        self.rect = self.image.get_rect()
        self.rect.center = (self.data["x"], self.data["y"])
        self.pressedKey = pg.key.get_pressed()
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def update(self):
        # resets acceleration
        self.acc = vec(0,0)


        if self.pressedKey[pg.K_UP]:
            self.acc.y -= ACCELERATION
        if self.pressedKey[pg.K_DOWN]:
            self.acc.y += ACCELERATION
        if self.pressedKey[pg.K_RIGHT]:
            self.acc.x += ACCELERATION
        if self.pressedKey[pg.K_LEFT]:
            self.acc.x -= ACCELERATION
        if self.acc.x != 0 and self.acc.y != 0:
            self.acc.x *= 0.7071
            self.acc.y *= 0.7071

        # applies friction
        self.acc += self.vel * FRICTION
        # accelerates
        self.vel += self.acc
        self.pos += self.vel + 0.5 * self.acc

        # updates position and dict position
        self.rect.center = self.pos

        self.data["x"] = self.pos.x
        self.data["y"] = self.pos.y
        print(self.data)

    def dict_socket(self, data):
        self.pos.x = self.data["x"]
        self.pos.y = self.data["y"]

        self.colour = self.data["colour"]
        self.image.fill(self.colour)

    def teleport(self):
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vel = vec(0,0)