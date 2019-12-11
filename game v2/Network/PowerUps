import Random

class PowerUps:
    def __init__(self,x, y, atribute):
        self.x = x
        self.y = y
        self.atribute = atribute

    def cooldown(self):
        pass

class Blink(PowerUps):
    def __init__(self):
        super.__init__(self, random.randrange(0.350), random.randrange(0.350), "utility")

    def do(self, target):
        player.pos = target
