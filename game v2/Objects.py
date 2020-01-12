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

    def load_grid_images(self, num_rows, num_cols, x_margin=0, x_padding=0,
                         y_margin=0, y_padding=0):
        """Load a grid of images.
        x_margin is space between top of sheet and top of first row.
        x_padding is space between rows.
        Assumes symmetrical padding on left and right.
        Same reasoning for y.
        Calls self.images_at() to get list of images.
        """
        sheet_rect = self.sheet.get_rect()
        sheet_width, sheet_height = sheet_rect.size

        # To calculate the size of each sprite, subtract the two margins,
        #   and the padding between each row, then divide by num_cols.
        # Same reasoning for y.
        x_sprite_size = (sheet_width - 2 * x_margin
                         - (num_cols - 1) * x_padding) / num_cols
        y_sprite_size = (sheet_height - 2 * y_margin
                         - (num_rows - 1) * y_padding) / num_rows

        sprite_rects = []
        for row_num in range(num_rows):
            for col_num in range(num_cols):
                # Position of sprite rect is margin + one sprite size
                #   and one padding size for each row. Same for y.
                x = x_margin + col_num * (x_sprite_size + x_padding)
                y = y_margin + row_num * (y_sprite_size + y_padding)
                sprite_rect = (x, y, x_sprite_size, y_sprite_size)
                sprite_rects.append(sprite_rect)

        grid_images = self.loadMultipleSprites(sprite_rects)
        print(f"Loaded {len(grid_images)} grid images.")

        return grid_images


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


class AbilityHud(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)

        sprites = SpriteSheet("tortell-andy-spell-icons.jpg")
        self.sprites = sprites.load_grid_images(8, 14, 56, 16, 56, 16)

        self.cd1Start = False
        self.cd2Start = False
        self.cd1TimeStart = 0
        self.cd2TimeStart = 0

        self.x = x
        self.y = y
        self.image = pg.Surface((w, h))
        self.image.fill((0, 177, 64))
        self.image.set_colorkey((0, 177, 64))

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.abilityName = None

    def update(self, data):
        abilityData = {"Blink": [47, 0], "Gun": [59, 10], "Growth": [43,6]} # sprite num, active time
        self.abilityName = data[str(data["id"])]["ability"]

        self.image.fill((0, 177, 64))

        if self.abilityName is not None:
            self.image.blit(pg.transform.scale(self.sprites[abilityData[self.abilityName][0]], (50, 50)), (0, 0))
            if self.cd2Start:
                self.cooldownBar(pg.transform.scale(self.sprites[abilityData[self.abilityName][0]], (50, 50))
                                                    ,abilityData[self.abilityName][1]+self.cd2TimeStart
                                                    , self.cd2TimeStart
                                                    ,2)
        else:
            self.cd2TimeStart = 0
            self.cd2Start = False

        self.image.blit(pg.transform.scale(self.sprites[36], (50, 50)), (60, 0))
        if self.cd1Start:
            self.cooldownBar(pg.transform.scale(self.sprites[36], (50, 50))
                             , 2 + self.cd1TimeStart, self.cd1TimeStart, 1)

    def cooldownBar(self, surface, cdTime, start, id):
        if pg.time.get_ticks() / 1000 < cdTime:
            timeDiff = int(((cdTime - pg.time.get_ticks() / 1000) / (cdTime - start)) *50)
            cdBar = pg.transform.scale(surface.copy(), (50,timeDiff))
            cdBar.fill(BLACK)
            cdBar.set_alpha(150)

            pos = (0,0)
            if id == 1:
                pos = (60, 0)
            self.image.blit(cdBar, pos)
        else:
            if id == 1:
                self.cd1Start = False
            elif id == 2:
                self.cd2Start = False

    def cooldownStart(self, ability, time):
        if ability == "side" and not self.cd1Start:
            self.cd1Start = True
            self.cd1TimeStart = time
        elif ability == "pickup" and not self.cd2Start and self.abilityName is not None:
            self.cd2Start = True
            self.cd2TimeStart = time



