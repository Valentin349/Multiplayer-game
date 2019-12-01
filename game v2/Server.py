import socket
from Keys import *
from Physics import *
import pygame as pg
from time import time
from Settings import *
from Package import Package

class Server:

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.IP = socket.gethostbyname(socket.gethostname())
        self.PORT = 5555

        self.clock = pg.time.Clock()

        self.P1physics = PhysicsEngine()
        self.P2physics = PhysicsEngine()

        try:
            self.sock.bind((self.IP, self.PORT))
        except socket.error as error:
            print(str(error))

        print("binding successfull")
        self.handle()

    def handle(self):
        while 1:
            try:
                try:
                    dataRecieved, addr = self.sock.recvfrom(2048)
                except:
                    break

                dt = self.clock.tick(20)
                dataRecieved = Package.unpack(dataRecieved)
                if dataRecieved["player"] == 1:
                    self.P1physics.movementUpdate(dataRecieved["inputs"],dt)
                    self.P1physics.collision(self.P2physics)
                else:
                    self.P2physics.movementUpdate(dataRecieved["inputs"],dt)

                reply = self.reply()

                if not dataRecieved:
                    # if no data is received assume disconnected
                    print("Disconnected")
                    break
                else:
                    # deal with response
                    dataSend = Package.pack(reply)
                    self.sock.sendto(dataSend, addr)
            except socket.error as error:
                print(error)
                break

    def reply(self):

        reply = {"1": {"x": self.P1physics.pos.x,
                       "y": self.P1physics.pos.y,
                       "time": time()
                       },

                 "2": {"x": self.P2physics.pos.x,
                       "y": self.P2physics.pos.y,
                       "time": time()
                       }
                 }

        return reply

s = Server()