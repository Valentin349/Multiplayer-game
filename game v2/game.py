import pygame as pg

from Settings import *
from Player import Player
from Objects import *

from Network import Network

class Game:
    def __init__(self, IP, PORT):
        pg.init()
        self.SCREEN = pg.display.set_mode((WIDTH, HEIGHT))
        self.SURFACE = pg.Surface((WIDTH, HEIGHT))
        pg.display.set_caption("client")

        self.clock = pg.time.Clock()
        self.running = True

        self.net = Network(IP, PORT)

        self.idCounter = 1

    def new(self):
        # load objects and players
        self.players = pg.sprite.Group()
        self.objs = pg.sprite.Group()

        self.platform = Platform(0, 0, 800, 600)
        self.map = TiledMap("Map1.tmx")
        self.abilityBlock = AbilityBlock(0, 0, 50, 50)
        self.abilityObject1 = AbilityObject(0, 0, 20, 20)
        self.abilityObject2 = AbilityObject(0, 0, 20, 20)
        self.player1 = Player(50, 50)
        self.player2 = Player(50, 50)

        self.objs.add(self.abilityBlock)
        self.players.add(self.player1, self.player2)

        for player in self.players:
            player.data["player"] = self.idCounter
            self.idCounter += 1

    def updateGameState(self, dataRecv):

        if self.abilityBlock not in self.objs and dataRecv["abilityBox"] is not None:
            self.objs.add(self.abilityBlock)

        if self.abilityObject1 not in self.objs and dataRecv["abilityObject1"] is not None:
            self.objs.add(self.abilityObject1)
        if self.abilityObject2 not in self.objs and dataRecv["abilityObject2"] is not None:
            self.objs.add(self.abilityObject2)

        for player in self.players:
            player.update(dataRecv)

        for obj in self.objs:
            if obj not in [self.abilityObject1, self.abilityObject2]:
                obj.update(dataRecv)
            elif obj == self.abilityObject1:
                obj.update(dataRecv["abilityObject1"])
            elif obj == self.abilityObject2:
                obj.update(dataRecv["abilityObject2"])

    def draw(self):
        self.SURFACE.blit(self.map.image, self.map.rect)

        for objects in self.objs:
            self.SURFACE.blit(objects.image, objects.rect)

        for players in self.players:
            self.SURFACE.blit(players.image, players.pos)

    def dataSend(self, data):
        dataRecv = self.net.send(data)
        return dataRecv

    def updateInputs(self, dt):
        # resets inputs
        self.player1.data["inputs"]["l"] = 0
        self.player1.data["inputs"]["r"] = 0
        self.player1.data["inputs"]["u"] = 0
        self.player1.data["inputs"]["d"] = 0
        self.player1.data["inputs"]["space"] = 0
        self.player1.data["inputs"]["mousePressed"] = 0

        pressedKey = pg.key.get_pressed()

        if pg.mouse.get_pressed()[0]:
            mousePos = pg.mouse.get_pos()
            self.player1.data["inputs"]["mousePressed"] = 1
            self.player1.data["inputs"]["mouseX"] = mousePos[0]
            self.player1.data["inputs"]["mouseY"] = mousePos[1]

        if pressedKey[pg.K_w]:
            self.player1.data["inputs"]["u"] = 1
        if pressedKey[pg.K_a]:
            self.player1.data["inputs"]["l"] = 1
        if pressedKey[pg.K_d]:
            self.player1.data["inputs"]["r"] = 1
        if pressedKey[pg.K_s]:
            self.player1.data["inputs"]["d"] = 1
        if pressedKey[pg.K_SPACE]:
            self.player1.data["inputs"]["space"] = 1


        self.player1.data["dt"] = dt

    def interpolation(self, data, player):
        pass

    def Endscreen(self):
        pass

    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
