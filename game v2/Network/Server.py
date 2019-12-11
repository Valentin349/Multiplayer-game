import socket
from Keys import *
from Physics import *
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

        self.powerUps = [blink()]
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
                    self.P1physics.MovementUpdate(dataRecieved["inputs"], dataRecieved["dt"])
                    self.P1physics.collision(self.P2physics)
                else:
                    self.P2physics.MovementUpdate(dataRecieved["inputs"], dataRecieved["dt"])
                    self.P2physics.collision(self.P1physics)

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
            abilityX = self.ability.x
            abilityY = self.ability.y
        else:
            abilityX = None
            abilityY = None

        reply = {"1": {"x": self.P1physics.pos.x,
                       "y": self.P1physics.pos.y,
                       },

                 "2": {"x": self.P2physics.pos.x,
                       "y": self.P2physics.pos.y,
                       },

                 "ability": {"x": abilityX,
                             "y": abilityY
                             },

                 "time": time(),

                 }

        return reply

s = Server()
