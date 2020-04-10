import socket
import random
import pygame as pg

import threading
from ServerSide.Physics import *
from ServerSide.PowerUps import *
from Settings import *
import Package

class TcpServer:
    def __init__(self):
        #tcp server to listen for connections trying to join main server
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 5544

        #bind ip and port
        try:
            self.sock.bind((self.IP, self.PORT))
        except socket.error as error:
            print(str(error))

        self.sock.listen()
        print("Tcp Socket is listening")

class Server:
    def __init__(self, obstacles):

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 5555
        self.sock.settimeout(5)

        #start the tcp server
        self.tcp = TcpServer()

        self.gameStarted = False
        self.gameEnd = False

        try:
            self.sock.bind((self.IP, self.PORT))
        except socket.error as error:
            print(str(error))

        print("binding successful")

        self.clock = pg.time.Clock()

        #players rigid bodies
        self.P1physics = PhysicsEngine(615, 200)
        self.P2physics = PhysicsEngine(615, 520)

        self.playerIdList = []

        #adds obstacles from client
        self.obstacles = []
        for obstacle in obstacles:
            self.obstacles.append(obstacle.rect)

        self.powerUps = [Blink(), Growth(), Gun()]
        self.ability = None
        self.abilityCreateTime = 0

        #start the handle method on a different thread
        thread = threading.Thread(target=self.handle)
        thread.daemon = True
        thread.start()

    def handle(self):
        while 1:
            #limits server at 124 frames per second
            self.clock.tick(124)
            try:
                try:
                    #try to get data from a client
                    dataRecieved, addr = self.sock.recvfrom(2048)
                    if addr not in self.playerIdList:
                        #adds address to player list
                        self.playerIdList.append(addr)
                        #if 2 players start the game and stop broadcasting
                        if len(self.playerIdList) == 2:
                            self.gameStarted = True
                            self.killTcp()

                except:
                    break
                #upack the data
                dataRecieved = Package.unpack(dataRecieved)
                if dataRecieved == "ExitRequest":
                    self.gameEnd = True

                #create a pickup on the map
                self.createPowerUp()
                if self.gameStarted and not self.gameEnd:
                    if self.playerIdList[0] == addr:
                        #physcis update
                        self.P1physics.update(dataRecieved["inputs"], dataRecieved["dt"], dataRecieved["skin"]
                                              , self.obstacles)
                        self.P1physics.collision(self.P2physics)
                        #collision update
                        if self.ability is not None:
                            if self.P1physics.collision(self.ability):
                                self.ability = None
                    else:
                        # physics update
                        self.P2physics.update(dataRecieved["inputs"], dataRecieved["dt"], dataRecieved["skin"]
                                              , self.obstacles)
                        self.P2physics.collision(self.P1physics)
                        # collision update
                        if self.ability is not None:
                            if self.P2physics.collision(self.ability):
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

        #if 10 seconds passed create a new ability on the screen
        #random pick the ability type
        if createTime > self.abilityCreateTime and self.ability is None:
            self.ability = random.choice(self.powerUps)
            self.abilityCreateTime = createTime + cooldown

    def reply(self, addr):
        #creates dictionary to pack into a json file and send
        #data pickup
        if self.ability is not None:
            box = {"x": self.ability.pos.x,
                   "y": self.ability.pos.y,
                   "Type": self.ability.abilityType,
                   }
        else:
            box = None

        #data about player 1 ability
        if self.P1physics.ability is not None:
            abilityNameP1 = self.P1physics.ability.name
            if self.P1physics.ability.objectPos is not None:
                #ability object data
                abilityObjectP1 = {"x": self.P1physics.ability.objectPos.x,
                                   "y": self.P1physics.ability.objectPos.y,
                                   "Type": self.P1physics.ability.objectType
                                   }
            else:
                abilityObjectP1 = None
        else:
            abilityObjectP1 = None
            abilityNameP1 = None

        #data about player 2 ability
        if self.P2physics.ability is not None:
            abilityNameP2 = self.P2physics.ability.name
            if self.P2physics.ability.objectPos is not None:
                # ability object data
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

        #finaly dictionary
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
                 "gameStarted":self.gameStarted,
                 "gameEnd": self.gameEnd
                 }
        return reply

    def kill(self):
        #close listen server and main server
        self.sock.close()
        self.tcp.sock.close()

    def killTcp(self):
        #close listening server
        self.tcp.sock.close()
