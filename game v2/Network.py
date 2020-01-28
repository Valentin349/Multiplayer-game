import socket
import Package


class Network:
    def __init__(self):
        self.PORT = 5555
        self.ip = None
        self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def send(self, data):
        addr = (self.ip, self.PORT)
        try:
            dataSent = Package.pack(data)
            self.client.sendto(dataSent, addr)
            
            data, server = self.client.recvfrom(2048)
            dataRecieved = Package.unpack(data)
            return dataRecieved
        except socket.error as error:
            print(str(error))

    def exit(self):
        self.ip = None

    def searchNetwork(self):
        port = 5544
        result = None
        for ending in range(0, 20):
            addr = socket.gethostbyname(socket.gethostname())[:-2] + str(ending)
            print(addr)
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.settimeout(0.1)
            result = conn.connect_ex((addr, port))
            conn.close()

            if result == 0:
                socket.setdefaulttimeout(None)
                return addr
        if result != 0:
            return None
