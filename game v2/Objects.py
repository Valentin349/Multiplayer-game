import pygame as pg
from Settings import *

class Platform(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pg.Surface((w, h))
        self.image.fill(PURPLE)
        self.rect = self.image.get_rect()
        self.rect.center = (WIDTH / 2, HEIGHT / 2)


class AbilityBlock(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pg.Surface((w, h))
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, data):
        if data["abilityBox"] is None:
            self.kill()
        else:
            self.rect.center = (data["abilityBox"]["x"], data["abilityBox"]["y"])

            if data["abilityBox"]["Type"] == "Utility":
                self.image.fill(GREEN)
            elif data["abilityBox"]["Type"] == "Defence":
                self.image.fill(BLUE)
            else:
                self.image.fill(RED)
