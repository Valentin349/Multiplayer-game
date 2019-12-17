import socket
import random
from Keys import *
from Physics import *
from PowerUps import *
import pygame as pg
from time import time
from Settings import *
import Package

class Server:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 5555

        self.clock = pg.time.Clock()

        self.P1physics = PhysicsEngine()
        self.P2physics = PhysicsEngine()

        self.playerIdList = []

        self.powerUps = [Blink(), Growth()]
        self.ability = None
        self.abilityCreateTime = 0

        try:
            self.sock.bind((self.IP, self.PORT))
        except socket.error as error:
            print(str(error))

        print("binding successfull")
        self.handle()

    def handle(self):
        while 1:
            self.clock.tick(124)
            try:
                try:
                    dataRecieved, addr = self.sock.recvfrom(2048)
                    if addr not in self.playerIdList:
                        self.playerIdList.append(addr)
                except:
                    break

                dataRecieved = Package.unpack(dataRecieved)

                self.createPowerUp()

                if self.playerIdList[0] == addr:
                    self.P1physics.update(dataRecieved["inputs"], dataRecieved["dt"])
                    self.P1physics.collision(self.P2physics)
                    if self.ability is not None:
                        if self.P1physics.collision(self.ability):
                            self.ability = None
                else:
                    self.P2physics.update(dataRecieved["inputs"], dataRecieved["dt"])
                    self.P2physics.collision(self.P1physics)
                    if self.ability is not None:
                        if self.P2physics.collision(self.ability):
                            self.ability = None

                reply = self.reply()

                if not dataRecieved:
                    # if no data is received assume disconnected
                    print("Disconnected")
                    break
                else:
                    # deal with response
                    dataSend = Package.pack(reply)
                    self.sock.sendto(dataSend, addr)
            except socket.error as error:
                print(error)
                break

    def createPowerUp(self):
        cooldown = 10
        createTime = pg.time.get_ticks() / 1000

        if createTime > self.abilityCreateTime and self.ability is None:
            self.ability = random.choice(self.powerUps)
            self.abilityCreateTime = createTime + cooldown

    def reply(self):
        if self.ability is not None:
            ability = {"x": self.ability.pos.x,
                       "y": self.ability.pos.y,
                       "Type": self.ability.abilityType
                       }
        else:
            ability = None

        reply = {"1": {"x": self.P1physics.pos.x,
                       "y": self.P1physics.pos.y,
                       "sizeUp": self.P1physics.sizeDouble
                       },

                 "2": {"x": self.P2physics.pos.x,
                       "y": self.P2physics.pos.y,
                       "sizeUp": self.P2physics.sizeDouble
                       },

                 "ability": ability,

                 "time": time(),

                 }

        return reply

s = Server()
