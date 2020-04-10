import pygame as pg
import pytmx
from Settings import *
from os import path

class SpriteSheet:
    def __init__(self, file):
        #load image from directory
        mainFolder = path.dirname(__file__)
        assetsFolder = path.join(mainFolder, "Assets")
        self.sheet = pg.image.load(path.join(assetsFolder, file)).convert()

    def loadSprite(self, rectangle, colourkey = None):
        #loads individual sprite in one rect
        rect = pg.Rect(rectangle)
        image = pg.Surface(rect.size).convert()
        image.blit(self.sheet, (0, 0), rect)
        #checks for transparent colours
        if colourkey is not None:
            if colourkey is -1:
                colourkey = image.get_at((0, 0))
            image.set_colorkey(colourkey, pg.RLEACCEL)
        return image

    def loadMultipleSprites(self, rects, colorkey=None):
        #loads multiple sprites and puts them in a list
        return [self.loadSprite(rect, colorkey) for rect in rects]

    def load_grid_images(self, num_rows, num_cols, x_margin=0, x_padding=0,
                         y_margin=0, y_padding=0, colourkey=None):
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

        grid_images = self.loadMultipleSprites(sprite_rects, colourkey)
        print(f"Loaded {len(grid_images)} grid images.")

        return grid_images


class Wall(pg.sprite.Sprite):
    #basic wall class, used to define wall objects from the map
    def __init__(self, x, y, w, h):
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.rect = pg.Rect(x, y, w, h)
        self.image = pg.Surface((w, h))
        self.rect.x = x
        self.rect.y = y


class TiledMap:
    """class is used to load a tile map from a tmx file"""
    def __init__(self, filename):
        #loads the file from directory
        mainFolder = path.dirname(__file__)
        mapFolder = path.join(mainFolder, "Maps")
        tm = pytmx.load_pygame(path.join(mapFolder, filename), pixelalpha=True)
        #define key data used to define a image
        self.width = tm.width * tm.tilewidth
        self.height = tm.height * tm.tileheight
        self.tmxData = tm
        self.image = self.makeMap()
        self.rect = self.image.get_rect()

        #scales to map to the screen
        self.image = pg.transform.scale(self.image, (WIDTH, HEIGHT))

    def render(self, surface):
        #renders the map to the screen
        ti = self.tmxData.get_tile_image_by_gid
        #loads the map by layers
        for layer in self.tmxData.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid, in layer:
                    tile = ti(gid)
                    if tile:
                        surface.blit(tile, (x * self.tmxData.tilewidth,
                                            y * self.tmxData.tileheight))

    def makeMap(self):
        #puts the map on the screen
        tempSurface = pg.Surface((self.width, self.height))
        self.render(tempSurface)
        return tempSurface


class AbilityBlock(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        #load key data for a pick up
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pg.Surface((w, h))

        sprites = SpriteSheet("Dungeon Tileset.png")
        self.sprites = sprites.loadMultipleSprites(((32, 96, 16, 16), (48, 96, 16, 16), (64, 96, 16, 16)), TrueBLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)

    def update(self, data):
        #checks if there are any pickups on the map
        if data["abilityBox"] is None:
            self.kill()
        else:
            # coords of the pickup
            self.rect.x = data["abilityBox"]["x"]
            self.rect.y = data["abilityBox"]["y"]

            #type of pick up and updates a different sprite
            if data["abilityBox"]["Type"] == "Utility":
                self.image = pg.transform.scale(self.sprites[0], (50, 50))
            elif data["abilityBox"]["Type"] == "Defence":
                self.image = pg.transform.scale(self.sprites[1], (50, 50))
            else:
                self.image = pg.transform.scale(self.sprites[2], (50, 50))


class AbilityObject(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        #keyp data needed to display objects created by abilites
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

            #if the data is bullet scale to a smaller image
            if data["Type"] == "Bullet":
                self.image = pg.transform.scale(self.image, (20, 20))


class HealthBar(pg.sprite.Sprite):
    def __init__(self, x, y, w, h):
        #key data to display the health bar on the screen
        pg.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.image = pg.Surface((w, h))
        #loads the heart sprites
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
        #depending on how much hp and lives there is it changes the sprites
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

        #data used for the cooldowns
        self.cd1Start = False
        self.cd2Start = False
        self.cd1TimeStart = 0
        self.cd2TimeStart = 0

        #data used to display the image on the screen
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
        #saves data as a dictionary to know what sprite to use
        abilityData = {"Blink": [47, 0], "Gun": [59, 10], "Growth": [43,6]} # sprite num, active time
        self.abilityName = data[str(data["id"])]["ability"]

        self.image.fill((0, 177, 64))

        #checks if there is a ability to display
        if self.abilityName is not None:
            self.image.blit(pg.transform.scale(self.sprites[abilityData[self.abilityName][0]], (50, 50)), (0, 0))
            if self.cd2Start:
                #adds cooldown bar for pick up
                self.cooldownBar(pg.transform.scale(self.sprites[abilityData[self.abilityName][0]], (50, 50))
                                                    ,abilityData[self.abilityName][1]+self.cd2TimeStart
                                                    , self.cd2TimeStart
                                                    ,2)
        else:
            #starts the default cooldown time
            self.cd2TimeStart = 0
            self.cd2Start = False

        self.image.blit(pg.transform.scale(self.sprites[36], (50, 50)), (60, 0))
        if self.cd1Start:
            #adds cooldown bar for dash ability
            self.cooldownBar(pg.transform.scale(self.sprites[36], (50, 50))
                             , 2 + self.cd1TimeStart, self.cd1TimeStart, 1)

    def cooldownBar(self, surface, cdTime, start, id):
        #checks the cooldown
        if pg.time.get_ticks() / 1000 < cdTime:
            #time diff is the percentage of the whole bar based on the time remaining of the cooldown
            timeDiff = int(((cdTime - pg.time.get_ticks() / 1000) / (cdTime - start)) *50)
            cdBar = pg.transform.scale(surface.copy(), (50,timeDiff))
            cdBar.fill(BLACK)
            cdBar.set_alpha(150)

            #displayes the cooldown bar at a certain position
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
        #used to sync the cooldown from the server and the bar
        #gets the input from the main game
        if ability == "side" and not self.cd1Start:
            self.cd1Start = True
            self.cd1TimeStart = time
        elif ability == "pickup" and not self.cd2Start and self.abilityName is not None:
            self.cd2Start = True
            self.cd2TimeStart = time


class Button(pg.sprite.Sprite):
    def __init__(self, x, y, w, h, style, growth=False, text=None):
        pg.sprite.Sprite.__init__(self)

        #loads sprite for the button
        sprites = SpriteSheet("UIpackSheet_transparent.png")
        self.sprites = sprites.load_grid_images(3, 12, 1, 4, 1, 4, TrueBLACK)

        #normal sized button
        self.imageNormal = pg.transform.scale(self.sprites[style], (w, h))
        self.image = self.imageNormal

        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.centerEnlarged = (x - 3, y - 3)
        self.centerNormal = (x, y)

        self.textSurface = None

        #loads font from directory
        mainFolder = path.dirname(__file__)
        assetsFolder = path.join(mainFolder, "Assets")
        font = pg.font.Font(path.join(assetsFolder, "Pixeled.ttf"), 10)
        #adds text if any was given
        if text is not None:
            self.textSurface = font.render(text, True, BLACK)
            self.textSurface = pg.transform.scale(self.textSurface, (int(w/2), int(h/2)))
            self.textRect = self.textSurface.get_rect()
            self.textRect.center = (w/2,h/2)
            self.imageNormal.blit(self.textSurface, self.textRect)

        #enlarged button
        self.imageLarge = pg.transform.scale(self.imageNormal, (w + 6, h + 6))

        self.growth = growth

        self.clicked = False

    def update(self):
        #update the button if needs to be enlarged
        if self.growth:
            mousePos = pg.mouse.get_pos()
            #checks if the mouse is on the button
            if self.rect.collidepoint(mousePos):
                self.image = self.imageLarge
                self.rect.center = self.centerEnlarged
            else:
                self.image = self.imageNormal
                self.rect.center = self.centerNormal

        #makes the button not clicked at the beginning of a frame
        self.clicked = False

    def click(self):
        #makes the button clicked, input is from the server
        self.clicked = True

