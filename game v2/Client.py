from game import Game
import pygame as pg

game = Game()
game.new()
game.StartScreen()
game.sendStartingData()
while game.running:
    dt = game.clock.tick(60)
    game.updateInputs(round(dt))
    game.events()
    data = game.dataSend(game.player1.data)
    game.id = data["id"]
    if data["gameEnd"]:
        game.running = False
    game.PauseMenu()
    game.updateGameState(data)
    game.draw()

    game.SCREEN.blit(game.SURFACE, (0, 0))

    pg.display.flip()

pg.quit()
