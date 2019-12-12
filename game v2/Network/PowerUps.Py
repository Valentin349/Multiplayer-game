import random
import pygame as pg
vec = pg.math.Vector2

class PowerUps:
    def __init__(self, x, y, abilityType):
        self.pos = vec(x, y)
        self.abilityType = abilityType

    def cooldown(self):
        pass

class Blink(PowerUps):
    def __init__(self):
        super().__init__(random.randrange(100, 500), random.randrange(100, 500), "utility")

    def do(self, player, target):
        player.pos = target
