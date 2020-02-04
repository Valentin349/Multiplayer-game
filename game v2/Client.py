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
        if game.net.ip is not None:
            data = game.dataSend(game.player1.data)
        if game.net.ip is not None:
            game.id = data["id"]
            game.PauseMenu()
            if data["winner"] is not None:
                if data["winner"] == game.id:
                    game.won = True
                game.EndScreen()
            game.updateGameState(data)

            if data["gameEnd"]:
                game.net.ip = None
        else:
            game.disconnect()
            game.updateGameState()

        game.draw()


        game.SCREEN.blit(game.SURFACE, (0, 0))


        pg.display.flip()

while game.running:
    game.StartScreen()
    if not game.running:
        break
    gameloop()

pg.quit()
