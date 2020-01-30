import pygame as pg
from Objects import *
vec = pg.math.Vector2


class Player(pg.sprite.Sprite):
    def __init__(self, width, height):
        pg.sprite.Sprite.__init__(self)

        self.data = {
            "player": 0,
            "dt": 0,
            "skin": 0,
            "inputs": {"l": 0,
                       "r": 0,
                       "u": 0,
                       "d": 0,
                       "space": 0,

                       "mousePressed": 0,
                       "mouseX": 0,
                       "mouseY": 0,
                       }
        }

        self.width = width
        self.height = height

        self.hp = 0
        self.lives = 0

        playerSpriteSheet = SpriteSheet("inca_back2.png")
        self.playerSprites = playerSpriteSheet.load_grid_images(2, 5)
        self.skinID = 0
        self.normalImage = pg.transform.scale(self.playerSprites[self.skinID], (50,50))
        self.largeImage = pg.transform.scale(self.playerSprites[self.skinID], (70, 70))
        self.image = self.normalImage

        self.rect = self.image.get_rect()
        self.largeRect = self.rect.inflate(2,2)

        self.pos = vec(0, 0)



    def update(self, dataRecv):
        self.lives = dataRecv[str(self.data["player"])]["lives"]
        self.hp = dataRecv[str(self.data["player"])]["hp"]

        self.pos.x = dataRecv[str(self.data["player"])]["x"]
        self.pos.y = dataRecv[str(self.data["player"])]["y"]

        if self.skinID != dataRecv[str(self.data["player"])]["skin"]:
            self.skinID = dataRecv[str(self.data["player"])]["skin"]
            self.normalImage = pg.transform.scale(self.playerSprites[self.skinID], (50, 50))
            self.largeImage = pg.transform.scale(self.playerSprites[self.skinID], (70, 70))
            self.image = self.normalImage
        self.skinUpdate = False

        size = dataRecv[str(self.data["player"])]["size"]
        if size == 50:
            self.image = self.normalImage
            self.rect = self.pos
        else:
            self.image = self.largeImage
            self.rect.x = self.pos.x - 10
            self.rect.y = self.pos.y - 10




