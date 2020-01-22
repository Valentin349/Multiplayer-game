import pygame as pg

from Settings import *
from Player import Player
from Objects import *

from Network import Network

class Game:
    def __init__(self):
        pg.init()
        self.SCREEN = pg.display.set_mode((WIDTH, HEIGHT))
        self.SURFACE = pg.Surface((WIDTH, HEIGHT))
        pg.display.set_caption("client")
        pg.mouse.set_cursor(*pg.cursors.broken_x)

        self.clock = pg.time.Clock()
        self.running = True
        self.inGame = False
        self.gameEnd = False
        self.paused = False

        self.id = None
        self.idCounter = 1

        self.net = Network()
        self.ip = None

    def new(self):
        # load objects and players
        self.players = pg.sprite.Group()
        self.objs = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.buttons = pg.sprite.Group()

        self.map = TiledMap("Map1.tmx")
        self.abilityBlock = AbilityBlock(0, 0, 50, 50)
        self.abilityObject1 = AbilityObject(0, 0, 20, 20)
        self.abilityObject2 = AbilityObject(0, 0, 20, 20)
        self.player1 = Player(50, 50)
        self.player2 = Player(50, 50)
        self.HpBar1 = HealthBar(1150,10,120,40)
        self.HpBar2 = HealthBar(1150, 50, 120, 40)
        self.hud = AbilityHud(615,650,110,50)

        #Buttons
        self.backgroundButton = Button(640, 350, 350, 400, 3, False)
        self.exitButton = Button(640, 300, 150, 80, 3, True, "QUIT")
        self.backButton = Button(640, 400, 150, 80, 3, True, "BACK")


        self.objs.add(self.abilityBlock, self.HpBar1, self.HpBar2, self.hud)
        self.players.add(self.player1, self.player2)

        for player in self.players:
            player.data["player"] = self.idCounter
            self.idCounter += 1

        for tileObject in self.map.tmxData.objects:
            if tileObject.name == "wall":
                self.obstacles.add(Wall(tileObject.x*3.64, tileObject.y*3, tileObject.width*3.64, tileObject.height*3))

    def updateGameState(self, dataRecv):

        for button in self.buttons:
            if button == self.backButton:
                if button.clicked:
                    self.paused = False
            elif button == self.exitButton:
                if button.clicked:
                    # leave server
                    pass

        if self.abilityBlock not in self.objs and dataRecv["abilityBox"] is not None:
            self.objs.add(self.abilityBlock)

        if self.abilityObject1 not in self.objs and dataRecv["abilityObject1"] is not None:
            self.objs.add(self.abilityObject1)
        if self.abilityObject2 not in self.objs and dataRecv["abilityObject2"] is not None:
            self.objs.add(self.abilityObject2)

        self.players.update(dataRecv)
        self.buttons.update()

        for obj in self.objs:
            if obj not in [self.abilityObject1, self.abilityObject2, self.HpBar1, self.HpBar2]:
                obj.update(dataRecv)
            elif obj == self.abilityObject1:
                obj.update(dataRecv["abilityObject1"])
            elif obj == self.abilityObject2:
                obj.update(dataRecv["abilityObject2"])
            elif obj == self.HpBar1:
                obj.update(dataRecv["1"])
            elif obj == self.HpBar2:
                obj.update(dataRecv["2"])



    def draw(self):
        self.SURFACE.blit(self.map.image, self.map.rect)

        for objects in self.objs:
            self.SURFACE.blit(objects.image, objects.rect)

        for players in self.players:
            self.SURFACE.blit(players.image, players.rect)

        self.buttons.draw(self.SURFACE)

    def dataSend(self, data):
        dataRecv = self.net.send(data)
        return dataRecv

    def sendStartingData(self):
        data = {"objects": []}
        for obsticle in self.obstacles:
            data["objects"].append([obsticle.rect.x, obsticle.rect.y, obsticle.rect.width, obsticle.rect.height])
        self.net.send(data)

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
            self.hud.cooldownStart("pickup", pg.time.get_ticks() / 1000)
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
            self.hud.cooldownStart("side", pg.time.get_ticks() / 1000)

        self.player1.data["dt"] = dt

    def StartScreen(self):
        hostButton = Button(640, 400, 150, 80, 3, True, "HOST")
        joinButton = Button(640, 500, 150, 80, 3, True, "JOIN")
        exitButton = Button(640, 600, 150, 80, 3, True, "QUIT")
        backButton = Button(440, 500, 150, 80, 3, True, "BACK")
        sideButton1 = Button(490, 250, 80, 80, 28, True)
        sideButton2 = Button(790, 250, 80, 80, 29, True)

        self.serverButton = None
        refreshButton = Button(840, 500, 150, 80, 3, True, "REFRESH")

        self.buttons.add(hostButton, joinButton, exitButton, sideButton1, sideButton2)

        playerSpriteSheet = SpriteSheet("inca_back2.png")
        playerSprites = playerSpriteSheet.load_grid_images(2,5)

        readIndex = 0
        menu = "main"
        while not self.inGame:
            self.SURFACE.fill(BLACK)
            self.buttons.update()
            self.events()
            for button in self.buttons:
                if button == sideButton1:
                    if button.clicked:
                        readIndex -= 1
                        if readIndex < 0:
                            readIndex = len(playerSprites) + readIndex

                elif button == sideButton2:
                    if button.clicked:
                        readIndex += 1
                        if readIndex >= len(playerSprites):
                            readIndex -= len(playerSprites)
                elif button == exitButton:
                    if button.clicked:
                        self.running = False
                        self.inGame = True

                elif button == joinButton:
                    if button.clicked:
                        self.ServerBrowser()
                        self.buttons.add(refreshButton, backButton)
                        menu = "browser"

                elif button == refreshButton:
                    if button.clicked:
                        self.ServerBrowser()
                        self.buttons.add(refreshButton, backButton)

                elif button == self.serverButton:
                    if button.clicked:
                        self.net.ip = self.ip
                        self.inGame = True
                        self.buttons.empty()

                elif button == backButton:
                    if button.clicked:
                        self.buttons.empty()
                        self.buttons.add(hostButton, joinButton, exitButton, sideButton1, sideButton2)
                        menu = "main"

                self.SURFACE.blit(button.image, button.rect)

            if menu == "main":
                self.SURFACE.blit(pg.transform.scale(playerSprites[readIndex], (100, 100)), (590,215))

            self.SCREEN.blit(self.SURFACE, (0, 0))

            pg.display.flip()

    def EndScreen(self):
        pass

    def PauseMenu(self):
        if self.paused:
            if len(self.buttons) == 0:
                self.buttons.add(self.backgroundButton, self.exitButton, self.backButton)
        else:
            self.buttons.empty()
    def ServerBrowser(self):
        self.SURFACE.fill(BLACK)
        searchBox = Button(640, 200, 250, 100, 3, False, "SEARCHING...")
        self.buttons.empty()
        self.buttons.add(searchBox)

        self.buttons.draw(self.SURFACE)
        self.SCREEN.blit(self.SURFACE, (0, 0))

        pg.display.flip()

        self.ip = self.net.searchNetwork()
        if self.ip is not None:
            self.serverButton = Button(640, 200, 550, 150, 3, True, self.ip)
            self.buttons.add(self.serverButton)
        else:
            NoServers = Button(640, 200, 550, 100, 3, False, "NO SERVERS FOUND ON LOCAL NETWORK")
            self.buttons.add(NoServers)


    def events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.running = False
                self.inGame = True

            if event.type == pg.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    if event.button == 1 and button.rect.collidepoint(event.pos):
                        button.click()

            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE:
                    if self.paused:
                        self.paused = False
                    else:
                        self.paused = True