import pygame as pg
from time import time

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

        self.t2 = 0

    def new(self):
        # load objects and players
        self.players = pg.sprite.Group()
        self.objs = pg.sprite.Group()

        self.platform = Platform(0, 0, 800, 600)
        self.abilityBlock = AbilityBlock(0, 0, 50, 50)
        self.player1 = Player(50, 50)
        self.player2 = Player(50, 50)

        self.objs.add(self.platform, self.abilityBlock)
        self.players.add(self.player1, self.player2)

        for player in self.players:
            player.data["player"] = self.idCounter
            self.idCounter += 1

    def updateGameState(self, dataRecv):
        for player in self.players:
            player.update(dataRecv)

        if self.abilityBlock not in self.objs and dataRecv["ability"] is not None:
            self.objs.add(self.abilityBlock)

        self.objs.update(dataRecv)

    def draw(self):
        self.SURFACE.fill(BLACK)

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
