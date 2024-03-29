import pygame as pg

from Settings import *
from Player import Player
from Objects import *

from Network import Network
from ServerSide.Server import Server

class Game:
    def __init__(self):
        #pygame initial data
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
        self.won = False

        self.id = None
        self.idCounter = 1

        self.net = Network()
        self.server = None
        self.ip = None

    def new(self):
        # load objects and players
        # all groups defined
        self.players = pg.sprite.Group()
        self.objs = pg.sprite.Group()
        self.obstacles = pg.sprite.Group()
        self.buttons = pg.sprite.Group()

        #objects and hud instances
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
        self.disconnectButton = Button(640, 300, 650, 200, 3, False, "Lost Connection")
        self.loseButton = Button(640, 300, 350, 200, 3, False, "YOU LOSE")
        self.winButton = Button(640, 300, 350, 200, 3, False, "YOU WIN")
        self.exitButton = Button(640, 450, 150, 80, 3, True, "QUIT")
        self.backButton = Button(640, 300, 150, 80, 3, True, "BACK")
        self.waitingButton = Button(640, 350, 950, 500, 3, False, "Waiting  for  Player")

        #add objects to groups
        self.objs.add(self.abilityBlock, self.HpBar1, self.HpBar2, self.hud)
        self.players.add(self.player1, self.player2)

        #player id
        for player in self.players:
            player.data["player"] = self.idCounter
            self.idCounter += 1

        #add objects from the map
        for tileObject in self.map.tmxData.objects:
            if tileObject.name == "wall":
                self.obstacles.add(Wall(tileObject.x*3.64, tileObject.y*3, tileObject.width*3.64, tileObject.height*3))

    def updateGameState(self, dataRecv=None):
        #update the game state based on data received from server

        # checks if buttons are clicked and does respective outputs
        for button in self.buttons:
            # checks to see if got out of pause menu
            if button == self.backButton:
                if button.clicked:
                    self.paused = False
            elif button == self.exitButton:
                #check if left game
                if button.clicked:
                    button.clicked = False
                    #check to see if host or player is leaving
                    if self.server is not None:
                        self.server.kill()
                        self.server = None
                    else:
                        self.net.leaveRequest()

                    # resets game data
                    self.net.exit()
                    self.buttons.empty()
                    self.inGame = False
                    self.gameEnd = True
                    self.paused = False
            elif button == self.waitingButton:
                if dataRecv is not None and dataRecv["gameStarted"]:
                    self.buttons.remove(self.waitingButton)

        self.buttons.update()

        #check if there is data received
        if dataRecv is not None:
            if self.abilityBlock not in self.objs and dataRecv["abilityBox"] is not None:
                self.objs.add(self.abilityBlock)

            #updates objects on the map
            if self.abilityObject1 not in self.objs and dataRecv["abilityObject1"] is not None:
                self.objs.add(self.abilityObject1)
            if self.abilityObject2 not in self.objs and dataRecv["abilityObject2"] is not None:
                self.objs.add(self.abilityObject2)

            self.players.update(dataRecv)

            #updates hud
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
        #draw map
        self.SURFACE.blit(self.map.image, self.map.rect)

        #draw objects
        for objects in self.objs:
            self.SURFACE.blit(objects.image, objects.rect)

        #draw players
        for players in self.players:
            self.SURFACE.blit(players.image, players.rect)

        self.buttons.draw(self.SURFACE)

    def dataSend(self, data):
        #send data to server and wait response
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
            #send ability used message to hud function
            self.hud.cooldownStart("pickup", pg.time.get_ticks() / 1000)
            mousePos = pg.mouse.get_pos()
            self.player1.data["inputs"]["mousePressed"] = 1
            self.player1.data["inputs"]["mouseX"] = mousePos[0]
            self.player1.data["inputs"]["mouseY"] = mousePos[1]

        #keyboard input
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
        #menu buttons
        hostButton = Button(640, 400, 150, 80, 3, True, "HOST")
        joinButton = Button(640, 500, 150, 80, 3, True, "JOIN")
        exitButton = Button(640, 600, 150, 80, 3, True, "QUIT")
        backButton = Button(440, 500, 150, 80, 3, True, "BACK")
        sideButton1 = Button(490, 250, 80, 80, 28, True)
        sideButton2 = Button(790, 250, 80, 80, 29, True)

        self.won = False

        self.serverButton = None
        refreshButton = Button(840, 500, 150, 80, 3, True, "REFRESH")

        self.buttons.add(hostButton, joinButton, exitButton, sideButton1, sideButton2)

        #load character sprites
        playerSpriteSheet = SpriteSheet("inca_back2.png")
        playerSprites = playerSpriteSheet.load_grid_images(2,5)

        # index of the character model in sprite list
        readIndex = 0
        menu = "main"
        while not self.inGame:
            self.SURFACE.fill(BLACK)
            self.buttons.update()
            self.events()
            for button in self.buttons:
                #left button for character slide
                if button == sideButton1:
                    if button.clicked:
                        readIndex -= 1
                        if readIndex < 0:
                            # negative numbers are subtracted from the end of the list
                            # gives impression of looping
                            readIndex = len(playerSprites) + readIndex

                # right button for the character slide
                elif button == sideButton2:
                    if button.clicked:
                        readIndex += 1
                        if readIndex >= len(playerSprites):
                            # whole length is subtracted from current position making it seem that it loops
                            readIndex -= len(playerSprites)

                #exit button
                elif button == exitButton:
                    if button.clicked:
                        self.running = False
                        self.inGame = True

                #host button
                elif button == hostButton:
                    if button.clicked:
                        #changes game starting data and saves character model
                        self.inGame = True
                        self.gameEnd = False
                        self.player1.data["skin"] = readIndex
                        self.server = Server(self.obstacles)
                        self.net.ip = self.server.IP
                        self.buttons.empty()
                        self.buttons.add(self.waitingButton)

                #server search button
                elif button == joinButton:
                    if button.clicked:
                        self.ServerBrowser()
                        self.buttons.add(refreshButton, backButton)
                        menu = "browser"

                #searches for servers again
                elif button == refreshButton:
                    if button.clicked:
                        self.ServerBrowser()
                        self.buttons.add(refreshButton, backButton)

                #the ip button when clicked joins the server
                elif button == self.serverButton:
                    if button.clicked:
                        self.net.ip = self.ip
                        self.player1.data["skin"] = readIndex
                        self.inGame = True
                        self.gameEnd = False
                        self.buttons.empty()

                #back button to go back to main menu
                elif button == backButton:
                    if button.clicked:
                        self.buttons.empty()
                        self.buttons.add(hostButton, joinButton, exitButton, sideButton1, sideButton2)
                        menu = "main"

                #updates screen
                self.SURFACE.blit(button.image, button.rect)

            #checks if in main menu or server browser
            if menu == "main":
                self.SURFACE.blit(pg.transform.scale(playerSprites[readIndex], (100, 100)), (590,215))

            self.SCREEN.blit(self.SURFACE, (0, 0))

            pg.display.flip()

    def EndScreen(self):
        #adds win or lose screen
        if len(self.buttons) == 0:
            if self.won:
                self.buttons.add(self.winButton, self.exitButton)
            else:
                self.buttons.add(self.loseButton, self.exitButton)

    def PauseMenu(self):
        #checks if paused and if so gets out of menu
        if self.paused:
            if len(self.buttons) == 0:
                self.buttons.add(self.backgroundButton, self.exitButton, self.backButton)
                for button in self.buttons:
                    button.image.set_alpha(190)
        else:
            #if not paused goes to the pause menu
            if self.buttons.has(self.backgroundButton, self.exitButton, self.backButton):
                self.buttons.remove(self.backgroundButton, self.exitButton, self.backButton)

    def disconnect(self):
        #adds buttons to leave the server once game finished
        if len(self.buttons) == 0:
            self.buttons.add(self.disconnectButton, self.exitButton)

    def ServerBrowser(self):
        #refreshes screen
        self.SURFACE.fill(BLACK)
        #text box
        searchBox = Button(640, 200, 250, 100, 3, False, "SEARCHING...")
        self.buttons.empty()
        self.buttons.add(searchBox)

        #draws new buttons
        self.buttons.draw(self.SURFACE)
        self.SCREEN.blit(self.SURFACE, (0, 0))

        pg.display.flip()

        #searches for server
        self.ip = self.net.searchNetwork()
        if self.ip is not None:
            #server found , display the server and allow to join
            self.serverButton = Button(640, 200, 550, 150, 3, True, self.ip)
            self.buttons.add(self.serverButton)
        else:
            #no server found
            NoServers = Button(640, 200, 550, 100, 3, False, "NO SERVERS FOUND ON LOCAL NETWORK")
            self.buttons.add(NoServers)

    def events(self):
        # checks for main game events
        for event in pg.event.get():
            #quit button is pressed
            if event.type == pg.QUIT:
                self.running = False
                self.inGame = True
                self.gameEnd = True

            #mouse button is pressed
            if event.type == pg.MOUSEBUTTONDOWN:
                #checks if the mouse was pressed on a button
                for button in self.buttons:
                    if event.button == 1 and button.rect.collidepoint(event.pos):
                        button.click()

            #escape button is pressed
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_ESCAPE and self.inGame:
                    if self.paused:
                        self.paused = False
                    else:
                        self.paused = True