import os
import socket
import sys
import json

vfs_data = {}
cur_path="/"

def load_vfs(json_path):
    if not os.path.exists(json_path):
        print(f"Loading error VFS: File '{json_path}' not found.")
        return False
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            global vfs_data
            vfs_data = json.load(f)
        return True
    except json.JSONDecodeError:
        print("Loading error VFS: wrong format JSON.")
        return False

def welcome_to_input():
    username = os.getlogin()
    hostname = socket.gethostname()
    return f"{username}@{hostname}:~$"

def command_vfs_save(arg):
    if not arg:
        print("Wrong arguments")
        return True
    try:
        with open(arg[0], "w", encoding="utf-8") as f:
            json.dump(vfs_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully save into '{arg[0]}'")
    except Exception as e:
        print(f"Saving error VFS: {e}")
    return True
        
def command_ls(arg):
    global cur_path
    if not arg:
        if cur_path in vfs_data and vfs_data[cur_path]["type"]=="dir":
            print(" ".join(vfs_data[cur_path]["content"]))
        return True
    elif arg:
        if arg.startswith("/"):
            t_path = arg
        else:
            if cur_path == "/":
                t_path = "/" + arg
            else:
                t_path=f"{cur_path}/{arg}"
        t_path=t_path.replace("//","/")
        if t_path in vfs_data:
            if vfs_data[t_path]["type"]=="dir":
                print(" ".join(vfs_data[t_path].get("content",[])))
            else:
                print(arg)
        else:
            print("File or directory not found")
    return True
            
def command_cd(arg):
    global cur_path
    if not arg or arg == "~":
        cur_path = "/"
        return True
    elif arg == "..":
        if cur_path != "/":
            path_parts = cur_path.strip("/").split("/")
            path_parts.pop()
            if not path_parts:
                cur_path = "/"
            else:
                cur_path = "/" + "/".join(path_parts)
        return True
    elif arg.startswith("/"):
        t_path = arg
    else:
        if cur_path == "/":
            t_path = "/" + arg
        else:
            t_path = f"{cur_path}/{arg}"
    t_path = t_path.replace("//","/")
    if t_path in vfs_data:
        if vfs_data[t_path]["type"] == "dir":
            cur_path = t_path
        else:
            print("{arg} is not directory")
    else:
        print(f"Wrong directory {arg}")
    return True
            
def commands(commnd,arg):
    if commnd == "exit":
        if arg:
            print("Command doesn't receive arguments")
            return True
        else:
            return False
    elif commnd == "ls": return command_ls(arg)
    elif commnd == "cd": return command_cd(arg)
    elif commnd == "vfs-save": return command_vfs_save(arg)
    elif commnd == "rev":
        if not arg:
            print("Waiting for arguments...")
            arg = str(input())
        print("".join(arg)[::-1])
        return True
    elif commnd == "who":
        print(f"{os.getlogin()} {socket.gethostname()}")
        return True
    elif commnd == "whoami":
        if arg:
            print("Command doesn't receive arguments")
        else:
            print(os.getlogin())
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
            if commnd in ["ls","cd"]:
                if len(parser) > 1:
                    arg=" ".join(parser[1:])
                else:
                    arg = ""
            else:
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
    print(f"Starter script path: {script}")
    if not load_vfs(vfs):
        return
    if script:
        if not run_start_script(script, invite):
            return
    interactive_invite = welcome_to_input()
    while True:
        inputt = input(interactive_invite + " ")
        parser = inputt.strip().split()
        if not parser:
            continue
        commnd = parser[0]
        if commnd in ["ls","cd"]:
            if len(parser) > 1:
                arg = " ".join(parser[1:])
            else:
                arg = ""
        else:
            if len(parser) > 1:
                arg = parser[1:]
            else:
                arg = ""
        if not commands(commnd, arg):
            break
          
if __name__=="__main__":
    start()
