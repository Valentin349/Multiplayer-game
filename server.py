import socket
import threading
from setting import *
import package


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = socket.gethostbyname(socket.gethostname())
PORT = 5555

# try to bind a socket to the ip and port
try:
    sock.bind((IP,PORT))
except socket.error as error:
    print(str(error))

print("binding successfull")
# allow number of conns
sock.listen(5)

# intial dict to save starting settings
key = {
    "x": 400,
    "y": 400,
    "velx": 0,
    "vely": 0,

    "player": 0,
    "lifes": 3,
    "colour": BLUE
}

key_2 = {
    "x": 600,
    "y": 600,
    "velx": 0,
    "vely": 0,


    "player": 1,
    "lifes": 3,
    "colour": WHITE

}

keys_players = [key, key_2]

def threaded_client(conn, player):

    data_s = package.pack(keys_players[player])
    conn.send(data_s)
    reply = ""
    while 1:
        try:
            try:
                data_c = package.unpack(conn.recv(2048))
            except:
                break

            keys_players[player] = data_c

            if not data_c:
                # if no data is received assume disconnected
                print("Disconnected")
                break
            else:
                if player == 1:
                    reply = keys_players[0]
                else:
                    reply = keys_players[1]

                data_s = package.pack(reply)
                conn.send(data_s)
        except socket.error as error:
            print(error)
            break

    print("lost connection")
    conn.close()

currentPlayer = 0
while 1:
    # accept connections from clients
    conn, addr = sock.accept()
    print(addr, "has connected")

    # set up a thread
    threading._start_new_thread(threaded_client, (conn, currentPlayer))
    currentPlayer += 1


