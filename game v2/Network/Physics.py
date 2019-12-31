import pygame as pg
import random
from Settings import *
vec = pg.math.Vector2

class PhysicsEngine:

    def __init__(self, spawnX, spawnY):
        self.pos = vec(spawnX, spawnY)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.maxVel = 1

        self.size = 50
        self.mass = 1

        self.nextDashTime = 0
        self.ability = None
        self.abilityActive = False

    def update(self, data, dt):
        # resets acceleration
        self.acc = vec(0, 0)

        if data["mousePressed"] and self.ability is not None:
            if (not self.abilityActive or self.ability.charges > 0) and self.ability.cooldown():
                self.ability.do(self, vec(data["mouseX"], data["mouseY"]))
                print(data["mouseX"], data["mouseY"])
                self.abilityActive = True

        if self.abilityActive:
            self.ability.update()
            if (pg.time.get_ticks() / 1000) > self.ability.timeUsed + self.ability.activeTime:
                self.ability.destroy(self)
                self.ability = None
                self.abilityActive = False

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
        if self.vel.magnitude() > self.maxVel:
            self.vel = self.vel.normalize() * self.maxVel

        self.pos += (self.vel + 0.5 * self.acc) * dt

    def dash(self):
        coolDown = 2
        timeUsed = pg.time.get_ticks() / 1000
        if timeUsed > self.nextDashTime:
            self.vel *= 3.5
            self.nextDashTime = timeUsed + coolDown

    def collision(self, target, objects):
        collided = False

        diff = self.pos - target.pos
        distance = diff.magnitude()

        playerRect = pg.Rect(self.pos.x, self.pos.y, self.size, self.size)
        if target is not None:
            if self.__class__.__name__ == target.__class__.__name__:

                for obstacle in objects:
                    if playerRect.colliderect(obstacle):
                        self.vel *= -1.5

                if self.ability is not None:
                    if self.ability.objectPos is not None:
                        targetRect = pg.Rect(target.pos.x, target.pos.y, target.size, target.size)
                        if targetRect.colliderect(self.ability.objectRect):
                            posDiff = target.pos - self.ability.objectPos
                            velDiff = target.vel - (self.ability.objectDirection * self.ability.objectVel)
                            impact = posDiff.dot(velDiff)

                            posUnitVec = posDiff / posDiff.magnitude_squared()
                            impulse = impact * posUnitVec
                            target.vel += target.vel - impulse

                if self.size == target.size:
                    if distance <= self.size:
                        collided = True
                elif distance <= 60:
                    collided = True

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
                if distance <= 50 and self.ability is None:
                    self.ability = target
                    return True
        else:
            return False
