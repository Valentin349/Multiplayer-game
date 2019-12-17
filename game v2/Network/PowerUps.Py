import random
import pygame as pg
vec = pg.math.Vector2

class PowerUps:
    def __init__(self, x, y, abilityType):
        self.pos = vec(x, y)
        self.abilityType = abilityType

        self.cooldownTime = 0
    def cooldown(self):
        pass


class Blink(PowerUps):
    def __init__(self):
        super().__init__(random.randrange(100, 500), random.randrange(100, 500), "utility")

    def do(self, player, target):
        player.pos = target


class Growth(PowerUps):
    def __init__(self):
        super().__init__(random.randrange(100, 500), random.randrange(100, 500), "Defence")
        self.cooldownTime = 10

    def do(self, player, target):
        player.mass = 5
        player.sizeDouble = True

        player.acc *= 0.5
