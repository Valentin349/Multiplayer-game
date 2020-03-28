from game import Game
import pygame as pg

game = Game()

game.new()

def gameloop():
    #Game loop, used to run the game scene
    while not game.gameEnd:
        #locks frame rate at a constant 60, used to send updates to server at 60 frames per second
        dt = game.clock.tick(60)
        if not game.paused:
            #only accepts inputs if the game is not in a paused state
            game.updateInputs(round(dt))
        game.events()
        if game.net.ip is not None:
            #sends data only if the player didn't disconnect
            data = game.dataSend(game.player1.data)
        if game.net.ip is not None:
            #checks again if the player disconnected
            game.id = data["id"]
            #check if player paused
            game.PauseMenu()
            if data["winner"] is not None:
                if data["winner"] == game.id:
                    #player won game ends
                    game.won = True
                game.EndScreen()
            #end of frame, updates the game with any changes
            game.updateGameState(data)

            if data["gameEnd"]:
                #resets the ip
                game.net.ip = None
        else:
            game.disconnect()
            game.updateGameState()

        game.draw()


        game.SCREEN.blit(game.SURFACE, (0, 0))


        pg.display.flip()

#main Loop
while game.running:
    game.StartScreen()
    if not game.running:
        break
    gameloop()

pg.quit()
