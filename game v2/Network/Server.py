import socket
import random
import pygame as pg

from threading import Thread
from Physics import *
from PowerUps import *
from Settings import *
import Package

class Server(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 5555

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
        self.powerUps = [Blink(), Growth(), Gun()]
        self.ability = None
        self.abilityCreateTime = 0


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

                if "objects" in dataRecieved:
                    if len(self.obstacles) == 0:
                        for obstacle in dataRecieved["objects"]:
                            wall = pg.Rect(obstacle[0], obstacle[1], obstacle[2], obstacle[3])
                            self.obstacles.append(wall)
                    dataSend = Package.pack("")
                    self.sock.sendto(dataSend, addr)
                    continue

                self.createPowerUp()

                if self.playerIdList[0] == addr:
                    self.P1physics.update(dataRecieved["inputs"], dataRecieved["dt"])
                    self.P1physics.collision(self.P2physics, self.obstacles)
                    if self.ability is not None:
                        if self.P1physics.collision(self.ability, self.obstacles):
                            self.ability = None
                else:
                    self.P2physics.update(dataRecieved["inputs"], dataRecieved["dt"])
                    self.P2physics.collision(self.P1physics, self.obstacles)
                    if self.ability is not None:
                        if self.P2physics.collision(self.ability, self.obstacles):
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
            box = {"x": self.ability.pos.x,
                   "y": self.ability.pos.y,
                   "Type": self.ability.abilityType,
                   }
        else:
            box = None

        if self.P1physics.ability is not None:
            if self.P1physics.ability.objectPos is not None:
                abilityObjectP1 = {"x": self.P1physics.ability.objectPos.x,
                                   "y": self.P1physics.ability.objectPos.y,
                                   "Type": self.P1physics.ability.objectType
                                   }
            else:
                abilityObjectP1 = None
        else:
            abilityObjectP1 = None

        if self.P2physics.ability is not None:
            if self.P2physics.ability.objectPos is not None:
                abilityObjectP2 = {"x": self.P2physics.ability.objectPos.x,
                                   "y": self.P2physics.ability.objectPos.y,
                                   "Type": self.P2physics.ability.objectType
                                   }
            else:
                abilityObjectP2 = None
        else:
            abilityObjectP2 = None

        if self.P1physics.lives <= 0 or self.P2physics.lives <= 0:
            gameEnd = True
        else:
            gameEnd = False

        reply = {"1": {"x": self.P1physics.pos.x,
                       "y": self.P1physics.pos.y,
                       "size": self.P1physics.size,
                       "lives": self.P1physics.lives,
                       "hp": self.P1physics.hp
                       },

                 "2": {"x": self.P2physics.pos.x,
                       "y": self.P2physics.pos.y,
                       "size": self.P2physics.size,
                       "lives": self.P2physics.lives,
                       "hp": self.P2physics.hp
                       },

                 "abilityBox": box,

                 "abilityObject1": abilityObjectP1,
                 "abilityObject2": abilityObjectP2,

                 "gameEnd": gameEnd

                 }

        return reply

class TcpServer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 5544

        try:
            self.sock.bind((self.IP, self.PORT))
        except socket.error as error:
            print(str(error))

        self.sock.listen()
        print("Tcp Socket is listening")

    def handle(self):
        while 1:
            conn, address = self.sock.accept()
            print(address, "has connected")
            data = conn.recv(2048)
            conn.send(data)


tcpServer = TcpServer()
mainServer = Server()

