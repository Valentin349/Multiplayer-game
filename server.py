import socket
import threading
from setting import *
import package


class Server:
    # initial dict to save starting settings
    key = {
        "x": 400,
        "y": 400,

        "velX": 0,
        "velY": 0,

        "accX": 0,
        "accY": 0,

        "player": 0,
        "lifes": 3,
        "colour": BLUE
    }

    key_2 = {
        "x": 600,
        "y": 600,

        "velX": 0,
        "velY": 0,

        "accX": 0,
        "accY": 0,

        "player": 1,
        "lifes": 3,
        "colour": WHITE

    }

    keys_players = [key, key_2]
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 5555


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
                    if player == 1:
                        reply = self.keys_players[0]
                    else:
                        reply = self.keys_players[1]


                    data_s = package.pack(reply)
                    conn.send(data_s)
            except socket.error as error:
                print(error)
                break

        print("lost connection")
        conn.close()

    def collision(self,player):
        collided = False
        if (self.keys_players[player]["x"] < self.keys_players[1-player]["x"] + 25 and
            self.keys_players[player]["x"] + 25 > self.keys_players[1-player]["x"] and
            self.keys_players[player]["y"] < self.keys_players[1-player]["y"] + 25 and
            self.keys_players[player]["y"] + 25 > self.keys_players[1-player]["x"]):
            collided = True

        posDiff = [self.keys_players[1-player]["x"] - self.keys_players[player]["x"], self.keys_players[1-player]["y"] - self.keys_players[player]["y"]]
        velDiff = [self.keys_players[1-player]["velX"] - self.keys_players[player]["velX"], self.keys_players[1-player]["velY"] - self.keys_players[player]["velY"]]
        impact = posDiff[0]*velDiff[0] + posDiff[1]*velDiff[1]

        posUnitX = posDiff[0] / (posDiff[0]**2 + posDiff[1]**2)
        posUnitY = posDiff[1] / (posDiff[0] ** 2 + posDiff[1] ** 2)
        impulseX = impact*posUnitX
        impulseY = impact*posUnitY

        if collided:
            print("collision")
            self.keys_players[1-player]["velX"] += self.keys_players[1-player]["velX"] - impulseX
            self.keys_players[1-player]["velY"] += self.keys_players[1-player]["velY"] - impulseY

            #self.keys_players[1-player]["x"] += self.keys_players[1-player]["velX"] + 0.5 * \
                                                #self.keys_players[1-player]["accX"]
            #self.keys_players[1-player]["y"] += self.keys_players[1-player]["velY"] + 0.5 * \
                                                #self.keys_players[1-player]["accY"]


s = Server()
