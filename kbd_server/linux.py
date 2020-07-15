# "Twitch Hacks Online"
# 2020 - Frank Godo

import socket
import keyboard

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('0.0.0.0', 1337))
s.listen(1)


def accept_connections():
    conn, addr = s.accept()
    conn.sendall("Connected to keyboard server\n")
    while True:
        data = conn.recv(1024)
        try:
            if data == "":
                break
            elif data[0] == "0":
                conn.sendall("Server shutting down...\n")
                break
            elif data[0] == "1":
                cleaned = data[1:].strip()
                print("Received key commands", cleaned)
                if cleaned == 'win':
                    cleaned = 125
                keyboard.send(cleaned)
            elif data[0] == "2":
                cleaned = data[1:]
                print("Received command:", cleaned)
                keyboard.write("\n" + cleaned + "\n")
            else:
                print("Could not enterpret:", data)
        except:
            print("Could not enterpret:", data)
    conn.close()


while True:
    try:
        accept_connections()
    except socket.error:
        pass
