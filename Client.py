import pygame as pg
import socket

from setting import *
from Menu import Button
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


    def update(self):
        for player in self.players:
            player.update()
            self.collision(player)

        self.objs.update()


    def draw(self):
        self.SURFACE.fill(BLACK)

        for objects in self.objs:
            self.SURFACE.blit(objects.image, objects.rect)

        for players in self.players:
            self.SURFACE.blit(players.image, players.rect)


    def collision(self, player):
        """
        :param player:  player object from sprite group
        :return: null
        """
        collided = pg.sprite.spritecollide(player, self.objs, False)

        if collided:
            pass
            #player.teleport()


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
                print(IP)
                return IP

            self.SCREEN.fill(BLACK)
            block = font.render(IP, True, WHITE)
            rect = block.get_rect()
            rect.center = self.SCREEN.get_rect().center
            self.SCREEN.blit(block, rect)
            pg.display.flip()

    def EndScreen(self):
        pass



def main():
    game = Game()

    IP = game.StartScreen()
    PORT = 5555

    n = Network(IP, PORT)

    game.new()

    # Networking

    startKey = n.getKey()

    game.player1.data = startKey
    game.player1.dict_socket(startKey)

    p2key = n.send(game.player1.data)
    game.player1.dict_socket(p2key)

    while game.running:

        for event in pg.event.get():
            if event.type == pg.QUIT:
                game.running = False

        # Movement
        game.player1.pressedKey = pg.key.get_pressed()


        # receive data from player 2

        p2key = n.send(game.player1.data)

        game.player2.pos.x = p2key["x"]
        game.player2.pos.y = p2key["y"]
        game.player2.image.fill(p2key["colour"])


        game.update()
        game.draw()

        game.SCREEN.blit(game.SURFACE,(0,0))

        pg.display.flip()

main()
pg.quit()
