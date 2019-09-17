import pygame as pg
from setting import *
vec = pg.math.Vector2

class Player(pg.sprite.Sprite):
    def __init__(self, width, height):
        pg.sprite.Sprite.__init__(self)

        self.data = {
            "x": 200,
            "y": 200,
            "velx": 0,
            "vely": 0,

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
        self.pos = vec(0, 0)
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

        # updates position and dict position (needed to send across server)
        self.rect.center = self.pos

        self.data["x"] = self.pos.x
        self.data["y"] = self.pos.y
        self.data["velx"] = self.vel.x
        self.data["vely"] = self.vel.y
        print(self.data)

    def dictSync(self, data):
        """
        syncs with server , needed to get correct initial pos and colour
        :return:
        """
        self.pos.x = data["x"]
        self.pos.y = data["y"]

        self.colour = data["colour"]
        self.image.fill(self.colour)

    def teleport(self):
        self.pos = vec(WIDTH / 2, HEIGHT / 2)
        self.vel = vec(0,0)
