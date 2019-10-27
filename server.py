import socket
import threading
from setting import *
import package
import pygame as pg

vec = pg.math.Vector2
class Server:
    # initial dict to save starting settings
    key = {"1": {
        "x": 400,
        "y": 400,

        "velX": 0,
        "velY": 0,

        "accX": 0,
        "accY": 0,

        "player": 0,
        "lifes": 3,
        "colour": BLUE
    },

        "2": {
            "x": 600,
            "y": 600,

            "velX": 0,
            "velY": 0,

            "accX": 0,
            "accY": 0,

            "player": 1,
            "lifes": 3,
            "colour": WHITE

        }}

    keys_players = [key["1"], key["2"]]

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 5555

        self.clock = pg.time.Clock()

        try:
            self.sock.bind((self.IP, self.PORT))
        except socket.error as error:
            print(str(error))

        print("binding successfull")
        self.connect()

    def connect(self):
        self.sock.listen(5)

        currentPlayer = 0
        while 1:
            # accept connections from clients
            conn, addr = self.sock.accept()
            print(addr, "has connected")

            # set up a thread
            threading._start_new_thread(self.threadedClient, (conn, currentPlayer))
            currentPlayer += 1

    def threadedClient(self, conn, player):
        data_s = package.pack(self.keys_players[player])
        conn.send(data_s)
        reply = ""
        while 1:
            try:
                try:
                    data_c = package.unpack(conn.recv(2048))
                except:
                    break

                self.keys_players[player] = data_c
                self.collision(player)

                if not data_c:
                    # if no data is received assume disconnected
                    print("Disconnected")
                    break
                else:
                    reply = self.keys_players

                    self.clock.tick(124)
                    data_s = package.pack(reply)
                    conn.send(data_s)
            except socket.error as error:
                print(error)
                break

        print("lost connection")
        conn.close()

    def collision(self,player):
        collided = False
        playerPos = vec(self.keys_players[player]["x"], self.keys_players[player]["y"])
        playerVel = vec(self.keys_players[player]["velX"], self.keys_players[player]["velY"])
        opponentPos = vec(self.keys_players[1-player]["x"], self.keys_players[1-player]["y"])
        opponentVel = vec(self.keys_players[1-player]["velX"], self.keys_players[1-player]["velY"])

        dx = self.keys_players[player]["x"] - self.keys_players[1 - player]["x"]
        dy = self.keys_players[player]["y"] - self.keys_players[1 - player]["y"]
        distance = (dx*dx + dy*dy)**0.5
        if distance <= 50:
            collided = True


        if collided and playerVel.magnitude() > opponentVel.magnitude():
            print("collision")
            print(self.keys_players[1-player]["velX"],self.keys_players[1-player]["velY"])

            posDiff = opponentPos - playerPos
            velDiff = opponentVel - playerVel
            impact = posDiff.dot(velDiff)

            posUnitVec = posDiff / posDiff.magnitude_squared()
            impulse = impact * posUnitVec

            opponentVel += (opponentVel - impulse)*3.5
            playerVel -= (playerVel - impulse)*0.34
            self.keys_players[1 - player]["velX"] = opponentVel.x
            self.keys_players[1 - player]["velY"] = opponentVel.y

            self.keys_players[player]["velX"] = playerVel.x
            self.keys_players[player]["velY"] = playerVel.y


s = Server()
