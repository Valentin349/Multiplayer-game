import pygame as pg
import random
from Settings import *
from PowerUps import *
vec = pg.math.Vector2

class PhysicsEngine:

    def __init__(self):
        self.pos = vec(random.randrange(0, 300), random.randrange(0, 300))
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)

        self.dashTime = 0

    def MovementUpdate(self, data, dt):
        # resets acceleration
        self.acc = vec(0, 0)

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
        cooldown = 2
        pressedTime = pg.time.get_ticks()/1000

        if pressedTime > self.dashTime:
            self.vel *= 3.5
            self.dashTime = pressedTime + cooldown


    def collision(self, target):
        collided = False

        dx = self.pos.x - target.pos.x
        dy = self.pos.y - target.pos.y
        distance = (dx*dx + dy*dy)**0.5
        if distance <= 50:
            collided = True

        if collided and self.vel.magnitude() > target.vel.magnitude():
            print("collision")

            posDiff = target.pos - self.pos
            velDiff = target.vel - self.vel
            impact = posDiff.dot(velDiff)

            posUnitVec = posDiff / posDiff.magnitude_squared()
            impulse = impact * posUnitVec

            target.vel += (target.vel - impulse)*3.5
            self.vel -= (self.vel - impulse)*0.5
