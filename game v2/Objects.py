import pygame as pg
import pytmx
from Settings import *

class SpriteSheet:
    def __init__(self, file):
        self.sheet = pg.image.load(file).convert()

    def loadSprite(self, rectangle, colourkey = None):
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        if colourkey is not None:
            if colourkey is -1:
                colourkey = image.get_at((0, 0))
            image.set_colorkey(colourkey, pg.RLEACCEL)
        return image

    def loadMultipleSprites(self, rects, colorkey=None):
        return [self.loadSprite(rect, colorkey) for rect in rects]


class Wall(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.rect = pg.Rect(x, y, w, h)
        self.image = pg.Surface((w, h))
        self.rect.x = x
        self.rect.y = y

class TiledMap:
    def __init__(self, filename):
        tm = pytmx.load_pygame(filename, pixelalpha=True)
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxData = tm
        self.image = self.makeMap()
        self.rect = self.image.get_rect()

        self.image = pg.transform.scale(self.image, (WIDTH, HEIGHT))

    def render(self, surface):
        ti = self.tmxData.get_tile_image_by_gid
        for layer in self.tmxData.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxData.tilewidth,
                                            y * self.tmxData.tileheight))

    def makeMap(self):
        tempSurface = pg.Surface((self.width, self.height))
        self.render(tempSurface)
        return tempSurface


class AbilityBlock(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pg.Surface((w, h))
        sprites = SpriteSheet("Dungeon Tileset.png")
        self.sprites = sprites.loadMultipleSprites(((32, 96, 16, 16), (48, 96, 16, 16), (64, 96, 16, 16)), TrueBLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, data):
        if data["abilityBox"] is None:
            self.kill()
        else:
            self.rect.x = data["abilityBox"]["x"]
            self.rect.y = data["abilityBox"]["y"]

            if data["abilityBox"]["Type"] == "Utility":
                self.image = pg.transform.scale(self.sprites[0], (50, 50))
            elif data["abilityBox"]["Type"] == "Defence":
                self.image = pg.transform.scale(self.sprites[1], (50, 50))
            else:
                self.image = pg.transform.scale(self.sprites[2], (50, 50))

class AbilityObject(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pg.Surface((w, h))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, data):
        if data is None:
            self.kill()
        else:
            self.rect.x = data["x"]
            self.rect.y = data["y"]

            if data["Type"] == "Bullet":
                self.image = pg.transform.scale(self.image, (20, 20))

class HealthBar(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pg.Surface((w, h))
        sprites = SpriteSheet("heart_animated_2.png")
        self.sprites = sprites.loadMultipleSprites(((0, 0, 51, 17), (0, 17, 51, 17), (0, 34, 51, 17),
                                                   (0, 51, 51, 17), (0, 68, 51, 17), (0, 85, 51, 17)), TrueBLACK)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.hearts = []
        for sprite in self.sprites:
            self.hearts.append(pg.transform.scale(sprite, (120, 40)))

    def update(self, data):
        print(data["lives"], data["hp"])
        if data["lives"] == 3 and data["hp"] > 50:
            self.image = self.hearts[0]
        elif data["lives"] == 3 and data["hp"] <= 50:
            self.image = self.hearts[1]
        elif data["lives"] == 2 and data["hp"] > 50:
            self.image = self.hearts[2]
        elif data["lives"] == 2 and data["hp"] <= 50:
            self.image = self.hearts[3]
        elif data["lives"] == 1 and data["hp"] > 50:
            self.image = self.hearts[4]
        elif data["lives"] == 1 and data["hp"] <= 50:
            self.image = self.hearts[5]

