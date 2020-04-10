import pygame as pg
import random
from Settings import *
vec = pg.math.Vector2

class PhysicsEngine:

    def __init__(self, spawnX, spawnY):
        #basic physics variables for rigid bodies
        self.pos = vec(spawnX, spawnY)
        self.vel = vec(0, 0)
        self.acc = vec(0, 0)
        self.maxVel = 1.5

        self.size = 50
        self.mass = 1

        self.lives = 3
        self.hp = 100

        self.nextDashTime = 0
        self.ability = None
        self.abilityActive = False
        
        self.skinId = 0

    def update(self, data, dt, skinID, obstacles):
        # resets acceleration
        self.acc = vec(0, 0)
        
        self.skinId = skinID

        #if mouse input use ability if the player has one
        if data["mousePressed"] and self.ability is not None:
            if (not self.abilityActive or self.ability.charges > 0) and self.ability.cooldown():
                self.ability.do(self, vec(data["mouseX"], data["mouseY"]))
                print(data["mouseX"], data["mouseY"])
                self.abilityActive = True

        #abiliy updates
        if self.abilityActive:
            self.ability.update()
            #cooldown check
            if (pg.time.get_ticks() / 1000) > self.ability.timeUsed + self.ability.activeTime:
                # if ability is active and it has decayed remove it from player
                self.ability.destroy(self)
                self.ability = None
                self.abilityActive = False

        #updates lives based on hp
        if self.hp <= 0:
            self.hp = 100
            self.lives -= 1

        #adds directional acceleration
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

        # applies friction
        self.acc += self.vel * FRICTION

        # creates a rect for the player for collision check
        playerRect = pg.Rect(self.pos.x, self.pos.y, self.size, self.size)
        for obstacle in obstacles:
            if playerRect.colliderect(obstacle):
                if self.vel.magnitude() > 0.6:
                    self.hp -= (self.vel.magnitude() - 0.6) * 100
                #check if the wall is horizontal or vertical to know which way to reflect the velocity
                if obstacle.right - obstacle.left > obstacle.bottom - obstacle.top:
                    self.vel.y *= -1
                else:
                    self.vel.x *= -1
                self.acc *= 0

        # accelerates
        self.vel += self.acc
        if self.vel.magnitude() > self.maxVel:
            self.vel = self.vel.normalize() * self.maxVel

        #updates position
        self.pos += (self.vel + 0.5 * self.acc) * dt

    def dash(self):
        #dash ability
        coolDown = 2
        timeUsed = pg.time.get_ticks() / 1000
        #checks cooldown
        if timeUsed > self.nextDashTime:
            self.vel *= 3.75
            self.nextDashTime = timeUsed + coolDown

    def collision(self, target):
        playerCollision = False

        #distance between player and target
        diff = self.pos - target.pos
        distance = diff.magnitude()


        if target is not None:
            #check if the collision is with a pick up of a physics object
            if self.__class__.__name__ == target.__class__.__name__:
                # checks if collision with ability object needs to be done
                if self.ability is not None:
                    #error handling
                    if self.ability.objectPos is not None:
                        targetRect = pg.Rect(target.pos.x, target.pos.y, target.size, target.size)
                        if targetRect.colliderect(self.ability.objectRect):
                            posDiff = target.pos - self.ability.objectPos
                            velDiff = target.vel - (self.ability.objectDirection * self.ability.objectVel*2)
                            impact = posDiff.dot(velDiff)

                            #direction in which the impulse is acting
                            posUnitVec = posDiff / posDiff.magnitude_squared()
                            #size of the impulse
                            impulse = impact * posUnitVec
                            #impulse is added to both objects
                            target.vel += target.vel - impulse
                            self.ability.objectDirection -= target.vel - impulse

                # checks if there is a collision with normal size players, large size players or normal and large
                if self.size == target.size:
                    if distance <= self.size:
                        playerCollision = True
                elif distance <= 60:
                    playerCollision = True

                # error handling so that there isn't multiple collisions in 1 frame
                if playerCollision and self.vel.magnitude() > target.vel.magnitude():

                    posDiff = target.pos - self.pos
                    velDiff = target.vel - self.vel
                    impact = posDiff.dot(velDiff)

                    # direction in which the impulse is acting
                    posUnitVec = posDiff / posDiff.magnitude_squared()
                    # size of the impulse
                    impulse = impact * posUnitVec

                    # impulse is added to both objects with mass included
                    target.vel += (target.vel - impulse)*((2*self.mass)/target.mass + self.mass)
                    self.vel -= (self.vel - impulse)*((2*target.mass)/target.mass + self.mass)*0.6

            else:
                # collision is with non physics object
                if distance <= 50 and self.ability is None:
                    self.ability = target
                    return True
        else:
            # no collisions
            return False
