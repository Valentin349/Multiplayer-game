import socket
import random
import pygame as pg

import threading
from ServerSide.Physics import *
from ServerSide.PowerUps import *
from ServerSide.Settings import *
import Package

class TcpServer:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 5544

        try:
            self.sock.bind((self.IP, self.PORT))
        except socket.error as error:
            print(str(error))

        self.sock.listen(1)
        print("Tcp Socket is listening")

class Server:
    def __init__(self, obstacles):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 5555
        self.sock.settimeout(5)

        self.tcp = TcpServer()

        self.gameStarted = False
        self.gameEnd = False

        try:
            self.sock.bind((self.IP, self.PORT))
        except socket.error as error:
            print(str(error))

        print("binding successful")

        self.clock = pg.time.Clock()

        self.P1physics = PhysicsEngine(615, 200)
        self.P2physics = PhysicsEngine(615, 520)

        self.playerIdList = []

        self.obstacles = []
        for obstacle in obstacles:
            self.obstacles.append(obstacle.rect)

        self.powerUps = [Blink(), Growth(), Gun()]
        self.ability = None
        self.abilityCreateTime = 0

        thread = threading.Thread(target=self.handle)
        thread.daemon = True
        thread.start()

    def handle(self):
        while 1:
            self.clock.tick(124)
            try:
                try:
                    dataRecieved, addr = self.sock.recvfrom(2048)
                    if addr not in self.playerIdList:
                        self.playerIdList.append(addr)
                        if len(self.playerIdList) == 2:
                            self.gameStarted = True
                except:
                    break

                dataRecieved = Package.unpack(dataRecieved)
                if dataRecieved == "ExitRequest":
                    self.gameEnd = True

                self.createPowerUp()
                if self.gameStarted and not self.gameEnd:
                    if self.playerIdList[0] == addr:
                        self.P1physics.update(dataRecieved["inputs"], dataRecieved["dt"], dataRecieved["skin"])
                        self.P1physics.collision(self.P2physics, self.obstacles)
                        if self.ability is not None:
                            if self.P1physics.collision(self.ability, self.obstacles):
                                self.ability = None
                    else:
                        self.P2physics.update(dataRecieved["inputs"], dataRecieved["dt"], dataRecieved["skin"])
                        self.P2physics.collision(self.P1physics, self.obstacles)
                        if self.ability is not None:
                            if self.P2physics.collision(self.ability, self.obstacles):
                                self.ability = None

                reply = self.reply(addr)
                dataSend = Package.pack(reply)
                self.sock.sendto(dataSend, addr)
            except socket.error as error:
                print(str(error))
                break

    def createPowerUp(self):
        cooldown = 10
        createTime = pg.time.get_ticks() / 1000

        if createTime > self.abilityCreateTime and self.ability is None:
            self.ability = random.choice(self.powerUps)
            self.abilityCreateTime = createTime + cooldown

    def reply(self, addr):
        if self.ability is not None:
            box = {"x": self.ability.pos.x,
                   "y": self.ability.pos.y,
                   "Type": self.ability.abilityType,
                   }
        else:
            box = None

        if self.P1physics.ability is not None:
            abilityNameP1 = self.P1physics.ability.name
            if self.P1physics.ability.objectPos is not None:
                abilityObjectP1 = {"x": self.P1physics.ability.objectPos.x,
                                   "y": self.P1physics.ability.objectPos.y,
                                   "Type": self.P1physics.ability.objectType
                                   }
            else:
                abilityObjectP1 = None
        else:
            abilityObjectP1 = None
            abilityNameP1 = None


        if self.P2physics.ability is not None:
            abilityNameP2 = self.P2physics.ability.name
            if self.P2physics.ability.objectPos is not None:
                abilityObjectP2 = {"x": self.P2physics.ability.objectPos.x,
                                   "y": self.P2physics.ability.objectPos.y,
                                   "Type": self.P2physics.ability.objectType,
                                   }
            else:
                abilityObjectP2 = None
        else:
            abilityObjectP2 = None
            abilityNameP2 = None

        if self.P1physics.lives <= 0 or self.P2physics.lives <= 0:
            if self.P1physics.lives < self.P2physics.lives:
                winner = 2
            else:
                winner = 1
        else:
            winner = None

        reply = {"id": self.playerIdList.index(addr)+1,

                 "1": {"x": self.P1physics.pos.x,
                       "y": self.P1physics.pos.y,
                       "size": self.P1physics.size,
                       "skin": self.P1physics.skinId,
                       "lives": self.P1physics.lives,
                       "hp": self.P1physics.hp,
                       "ability": abilityNameP1
                       },

                 "2": {"x": self.P2physics.pos.x,
                       "y": self.P2physics.pos.y,
                       "size": self.P2physics.size,
                       "skin": self.P2physics.skinId,
                       "lives": self.P2physics.lives,
                       "hp": self.P2physics.hp,
                       "ability": abilityNameP2
                       },

                 "abilityBox": box,

                 "abilityObject1": abilityObjectP1,
                 "abilityObject2": abilityObjectP2,

                 "winner": winner,
                 "gameEnd": self.gameEnd
                 }
        return reply

    def kill(self):
        self.sock.close()
        self.tcp.sock.close()

