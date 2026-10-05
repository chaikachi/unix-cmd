import os
import socket

def welcome_to_input():
    username = os.getlogin()
    hostname = socket.gethostname()
    return f"{username}@{hostname}:~$"
    
while True:
    inputt = input(welcome_to_input())
    parser = inputt.strip().split()
    if not parser:
        continue
    commnd = parser[0]
    if len(parser) > 1:
        arg = parser[1:]
    else:
        arg = ""
    if commnd == "exit":
        if arg:
            print("Command doesn't receive arguments")
        else:
            break
    elif commnd == "ls":
        print(f"[This is ls] Arguments: {arg}")
    elif commnd == "cd":
        if not arg:
            print("Wrong arguments")
        else:
            print(f"[This is cd] Arguments: {arg}")
    else:
        print(f"Wrong command {commnd}")
