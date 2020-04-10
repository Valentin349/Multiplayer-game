import json

# functions for simplicity when using the json library
def unpack(data):
    return json.loads(data)


def pack(data):
    data = json.dumps(data)
    return bytes(data, "utf-8")