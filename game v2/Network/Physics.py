import pygame as pg
import random
import PowerUps
from Settings import *
vec = pg.math.Vector2

class PhysicsEngine:

    def __init__(self):
        self.pos = vec(random.randrange(0, 300), random.randrange(0, 300))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.sizeDouble = False
        self.mass = 1

        self.nextDashTime = 0
        self.ability = None

    def update(self, data, dt):
        # resets acceleration
        self.acc = vec(0, 0)

        if data["mousePressed"] and self.ability is not None:
            print(data["mouseX"], data["mouseY"])
            self.ability.do(self, vec(data["mouseX"], data["mouseY"]))
            self.ability = None

        if data["u"]:
            self.acc.y -= ACCELERATION
        if data["d"]:
            self.acc.y += ACCELERATION
        if data["r"]:
            self.acc.x += ACCELERATION
        if data["l"]:
            self.acc.x -= ACCELERATION
        if data["space"]:
            self.dash()
        if self.acc.x != 0 and self.acc.y != 0:
            self.acc.x *= 0.7071
            self.acc.y *= 0.7071

        # applies friction
        self.acc += self.vel * FRICTION
        # accelerates
        self.vel += self.acc
        self.pos += (self.vel + 0.5 * self.acc) * dt

    def dash(self):
        coolDown = 2
        timeUsed = pg.time.get_ticks() / 1000
        if timeUsed > self.nextDashTime:
            self.vel *= 3.5
            self.nextDashTime = timeUsed + coolDown
            print("dash")


    def collision(self, target):
        collided = False

        dx = self.pos.x - target.pos.x
        dy = self.pos.y - target.pos.y
        distance = (dx*dx + dy*dy)**0.5
        if distance <= 50:
            collided = True

        if target is not None:
            if self.__class__.__name__ == target.__class__.__name__:
                if collided and self.vel.magnitude() > target.vel.magnitude():
                    print("collision")

                    posDiff = target.pos - self.pos
                    velDiff = target.vel - self.vel
                    impact = posDiff.dot(velDiff)

                    posUnitVec = posDiff / posDiff.magnitude_squared()
                    impulse = impact * posUnitVec

                    target.vel += (target.vel - impulse)*((2*self.mass)/target.mass + self.mass)
                    self.vel -= (self.vel - impulse)*((2*target.mass)/target.mass + self.mass)*0.6
            else:
                if collided:
                    self.ability = target
                    return True
        else:
            return False
