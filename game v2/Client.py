from game import Game
import pygame as pg


IP = "192.168.0.36"
PORT = 5555

game = Game(IP, PORT)
game.new()
while game.running:
    game.updateInputs()
    print(game.player1.data["inputs"])
    data = game.dataSend(game.player1.data)
    game.updateGameState(data)
    game.draw()
    game.events()

    game.SCREEN.blit(game.SURFACE, (0, 0))

    pg.display.flip()

pg.quit()