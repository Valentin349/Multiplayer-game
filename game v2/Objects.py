import pygame as pg
import pytmx
from Settings import *

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
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, data):
        if data["abilityBox"] is None:
            self.kill()
        else:
            self.rect.x = data["abilityBox"]["x"]
            self.rect.y = data["abilityBox"]["y"]

            if data["abilityBox"]["Type"] == "Utility":
                self.image.fill(GREEN)
            elif data["abilityBox"]["Type"] == "Defence":
                self.image.fill(BLUE)
            else:
                self.image.fill(RED)

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
                self.image = pg.transform.smoothscale(self.image, (20, 20))
