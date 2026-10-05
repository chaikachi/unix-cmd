import os
import socket
import sys

def welcome_to_input():
    username = os.getlogin()
    hostname = socket.gethostname()
    return f"{username}@{hostname}:~$"

def commands(commnd,arg):
    if commnd == "exit":
        if arg:
            print("Command doesn't receive arguments")
            return True
        else:
            return False
    elif commnd == "ls":
        if not arg:
            print(f"[ls] Arguments: none")
        else:
            print(f"[ls] Arguments: {arg}")
        return True
    elif commnd == "cd":
        if not arg:
            print("[cd] Wrong arguments")
        else:
            print(f"[cd] Arguments: {arg}")
        return True
    else:
        print(f"Wrong command {commnd}")
        return True

def run_start_script(script_path,invite):
    if not os.path.exists(script_path):
        print(f"File '{script_path}' not found")
        return True
    with open(script_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            print(f"{invite} {line}")
            parser = line.strip().split()
            commnd = parser[0]
            if len(parser) > 1:
                arg = parser[1:]
            else:
                arg = ""
            commands(commnd, arg)

def start():
    if len(sys.argv) < 3:
        return
    vfs = sys.argv[1]
    invite = sys.argv[2]
    if len(sys.argv)>3:
        script = sys.argv[3]
    else:
        script = ""
    print(f"VFS: {vfs}")
    print(f"REPL: {invite}")
    print(f"Путь к стартовому скрипту: {script}")
    interactive_invite = welcome_to_input()
    if not run_start_script(script, invite):
        return   
    while True:
        inputt = input(interactive_invite+" ")
        parser = inputt.strip().split()
        if not parser:
            continue
        commnd = parser[0]
        if len(parser) > 1:
            arg = parser[1:]
        else:
            arg = ""
        if not commands(commnd, arg):
            break
        
if __name__=="__main__":
    start()
