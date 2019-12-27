import random
import pygame as pg
vec = pg.math.Vector2

class PowerUps:
    def __init__(self, x, y, abilityType):
        self.pos = vec(x, y)
        self.abilityType = abilityType

        self.coolDownTime = 0
        self.nextUseTime = 0
        self.charges = 0

        self.activeTime = 0
        self.timeUsed = 0

        self.objectDirection = vec(0, 0)
        self.objectPos = None
        self.objectVel = None
        self.objectType = None
        self.objectRect = None

    def cooldown(self):
        timeUsed = pg.time.get_ticks() / 1000
        if timeUsed > self.nextUseTime:
            self.nextUseTime = timeUsed + self.coolDownTime
            return True
        else:
            return False

    def destroy(self, player):
        pass

    def update(self):
        pass


class Blink(PowerUps):
    def __init__(self):
        super().__init__(random.randrange(100, 500), random.randrange(100, 500), "Utility")

    def do(self, player, target):
        self.pos = vec(random.randrange(100, 500), random.randrange(100, 500))

        player.pos = target


class Growth(PowerUps):
    def __init__(self):
        super().__init__(random.randrange(100, 500), random.randrange(100, 500), "Defence")
        self.activeTime = 6

    def do(self, player, target):
        self.pos = vec(random.randrange(100, 500), random.randrange(100, 500))

        player.mass = 3
        player.size = 70
        player.maxVel = 0.15

        self.timeUsed = pg.time.get_ticks() / 1000

    def destroy(self, player):
        player.mass = 1
        player.size = 50
        player.maxVel = 1


class Gun(PowerUps):
    def __init__(self):
        super().__init__(random.randrange(100, 500), random.randrange(100, 500), "Attack")
        self.activeTime = 4
        self.charges = 3
        self.coolDownTime = 0.5

        self.objectType = "Bullet"
        self.objectVel = 17

    def do(self, player, target):
        self.pos = vec(random.randrange(100, 500), random.randrange(100, 500))

        self.charges -= 1

        self.objectDirection = (target - player.pos).normalize()
        self.objectPos = player.pos + self.objectDirection

        self.timeUsed = pg.time.get_ticks() / 1000

    def update(self):
        self.objectPos += self.objectDirection * self.objectVel
        self.objectRect = pg.Rect(self.objectPos.x, self.objectPos.y, 10, 10)

    def destroy(self, player):
        self.objectPos = None
        self.objectRect = None
