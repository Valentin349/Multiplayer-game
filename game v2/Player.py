import pygame as pg
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, width, height):
        pg.sprite.Sprite.__init__(self)

        self.data = {
            "player": 0,
            "Colour": 0,
            "inputs": {"l": 0,
                       "r": 0,
                       "u": 0,
                       "d": 0,
                       "space": 0
                       }
        }

        self.width = width
        self.height = height

        self.colour = self.data["Colour"]
        self.image = pg.Surface((width, height))

        self.rect = self.image.get_rect()
        self.rect.center = (0, 0)

        self.lastPos = vec(0, 0)
        self.pos = vec(0, 0)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

    def update(self, dataRecv):
        self.lastPos = self.pos

        self.pos.x = dataRecv[str(self.data["player"])]["x"]
        self.pos.y = dataRecv[str(self.data["player"])]["y"]

        self.rect.center = self.pos