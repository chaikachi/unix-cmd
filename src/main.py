import os
import socket
import sys
import json

vfs_data = {}
cur_path="/"

def welcome_to_input():
    username = os.getlogin()
    hostname = socket.gethostname()
    return f"{username}@{hostname}:~$"

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

def abs_path(path_str):
    if not path_str:
        return ""
    if path_str.startswith("/"):
        t_path = path_str
    else:
        if cur_path == "/":
            t_path = "/" + path_str
        else:
            t_path = f"{cur_path}/{path_str}"
    return t_path.replace("//", "/")

def file_path(filepath):
    parts = filepath.strip("/").split("/")
    file_name = parts[-1]
    p_dir = "/" + "/".join(parts[:-1])
    p_dir = p_dir.replace("//", "/")
    return p_dir, file_name

def move_file(filepath,commnd):
    p_dir, file_name = file_path(filepath)
    if p_dir in vfs_data:
        if commnd == "cp":
            content = vfs_data[p_dir].setdefault("content", [])
            if file_name not in content:
                content.append(file_name)
        else:
            content = vfs_data[p_dir].get("content", [])
            if file_name in content:
                content.remove(file_name)

def command_cp(arg):
    parts = arg.split()
    if len(parts) < 2:
        print("Wrong arguments")
        return True
    src_path = abs_path(parts[0])
    dst_path = abs_path(parts[1])
    
    if src_path not in vfs_data:
        print(f"File or directory not found")
        return True
    vfs_data[dst_path] = dict(vfs_data[src_path])
    move_file(dst_path,"cp")
    return True

def command_mv(arg):
    parts = arg.split()
    if len(parts) < 2:
        print("Wrong arguments")
        return True
    src_path = abs_path(parts[0])
    dst_path = abs_path(parts[1])
    
    if src_path not in vfs_data:
        print(f"File or directory not found")
        return True
    vfs_data[dst_path] = dict(vfs_data[src_path])
    move_file(dst_path,"cp")
    
    del vfs_data[src_path]
    move_file(src_path,"mv")
    return True

def command_vfs_save(arg):
    if not arg:
        print("Wrong arguments")
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
    elif arg:
        t_path=abs_path(arg)
        if t_path in vfs_data:
            if vfs_data[t_path]["type"] == "dir":
                print(" ".join(vfs_data[t_path].get("content",[])))
            else:
                print(arg)
        else:
            print("File or directory not found")
    return True
            
def command_cd(arg):
    global cur_path
    if not arg or arg == "~":
        cur_path="/"
    elif arg == "..":
        if cur_path != "/":
            path_parts=cur_path.strip("/").split("/")
            path_parts.pop()
            if not path_parts:
                cur_path = "/"
            else:
                cur_path="/" + "/".join(path_parts)
        return True
    t_path=abs_path(arg)
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
    elif commnd == "cp": return command_cp(arg)
    elif commnd == "mv": return command_mv(arg)
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
            arg = ""
            if commnd in ["ls","cd", "cp", "mv"]:
                arg = " ".join(parser[1:])
            else:
                arg = parser[1:]
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
    print(f"VFS: {vfs}\nREPL: {invite}\nStarter script path: {script}")
    interactive_invite=welcome_to_input()
    if not load_vfs(vfs):
        return
    if script and not run_start_script(script, invite):
        return
    while True:
        inputt = input(interactive_invite+" ")
        parser = inputt.strip().split()
        if not parser:
            continue
        commnd = parser[0]
        arg = ""
        if commnd in ["ls","cd", "mv", "cp"]:
            arg = " ".join(parser[1:])
        else:
            arg = parser[1:]
        if not commands(commnd, arg):
            break
        
if __name__ == "__main__":
    start()
