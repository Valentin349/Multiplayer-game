from game import Game
import pygame as pg

game = Game()

game.new()

def gameloop():
    while not game.gameEnd:
        dt = game.clock.tick(60)
        if not game.paused:
            game.updateInputs(round(dt))
        game.events()
        data = game.dataSend(game.player1.data)
        game.id = data["id"]
        if data["gameEnd"]:
            game.gameEnd = True
        game.PauseMenu()
        game.updateGameState(data)
        game.draw()

        game.SCREEN.blit(game.SURFACE, (0, 0))

        pg.display.flip()

while game.running:
    game.StartScreen()
    if not game.running:
        break
    gameloop()

pg.quit()
