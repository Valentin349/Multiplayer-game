import pygame as pg
from time import time
from math import l

from setting import *
from Player import Player
from Objects import *

from Network import Network

class Game:
    def __init__(self):
        # initialise game window
        pg.init()
        self.SCREEN = pg.display.set_mode((WIDTH, HEIGHT))
        self.SURFACE = pg.Surface((WIDTH, HEIGHT))
        pg.display.set_caption("client")
        self.clock = pg.time.Clock()
        self.running = True

        self.player1 = None
        self.player2 = None

    def new(self):
        # load objects and players
        self.players = pg.sprite.Group()
        self.objs = pg.sprite.Group()

        self.platform = Platform(0, 0, 800, 600)
        self.player1 = Player(50, 50)
        self.player2 = Player(50, 50)

        self.objs.add(self.platform)
        self.players.add(self.player1, self.player2)

    def update(self, dt):
        for player in self.players:
            player.update(dt)

        self.objs.update()

    def draw(self):
        self.SURFACE.fill(BLACK)

        for objects in self.objs:
            self.SURFACE.blit(objects.image, objects.rect)

        for players in self.players:
            self.SURFACE.blit(players.image, players.rect)



    def StartScreen(self):

        font = pg.font.Font(None, 30)
        IP = ""
        while self.running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.KEYDOWN:
                    if event.unicode.isdigit() or event.unicode == u"\u002e":
                        IP += str(event.unicode)
                    elif event.key == pg.K_BACKSPACE:
                        IP = IP[:-1]

            getPressed = pg.key.get_pressed()
            if getPressed[pg.K_RETURN]:
                return IP

            self.SCREEN.fill(BLACK)
            block = font.render(IP, True, WHITE)
            rect = block.get_rect()
            rect.center = self.SCREEN.get_rect().center
            self.SCREEN.blit(block, rect)
            pg.display.flip()

    def EndScreen(self):
        pass

    def interpolate(self, dt, timestamp):
        past = 1000/dt
        now = time()
        renderTime = now - past

        if renderTime <= timestamp:
            total = timestamp - now
            portion = renderTime - now

            ratio = portion / total
            



def main():
    game = Game()

    #IP = game.StartScreen()
    IP = "10.192.41.214"
    PORT = 5555



    n = Network(IP, PORT)

    game.new()

    # sync server data to client

    startKey = n.getKey()

    game.player1.data = startKey
    game.player1.dictSync(startKey)


    while game.running:

        dt = game.clock.tick(FPS)/1000
        for event in pg.event.get():
            if event.type == pg.QUIT:
                game.running = False

        # Movement
        game.player1.pressedKey = pg.key.get_pressed()


        # receive data from player 2
        p2key = n.send(game.player1.data)

        timestamp = p2key["ts"]

        game.player2.data = p2key[1-startKey["player"]]
        game.player2.dictSync(p2key[1-startKey["player"]])

        game.player1.data = p2key[startKey["player"]]
        game.player1.dictSync(p2key[startKey["player"]])



        game.update(dt)
        game.draw()

        game.SCREEN.blit(game.SURFACE,(0,0))

        pg.display.flip()

main()
pg.quit()
