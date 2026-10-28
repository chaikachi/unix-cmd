import os
import socket
import sys
import json
import base64

vfs_data = {}
start_len = 3

def load_vfs(json_path):
    if not os.path.exists(json_path):
        print(f"Loading error VFS: File '{json_path}' not found.")
        return False
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            global vfs_data
            vfs_data = json.load(f)
            for path, info in vfs_data.items():
                if info.get("type") == "file" and "content" in info:
                    encoded_text = info["content"]
                    try:
                        b_text=encoded_text.encode('utf-8')
                        info["content"] = base64.b64decode(b_text).decode('utf-8')
                    except Exception:
                        pass
        return True
    except json.JSONDecodeError:
        print("Loading error VFS: wrong format JSON.")
        return False

def welcome_to_input():
    username = os.getlogin()
    hostname = socket.gethostname()
    return f"{username}@{hostname}:~$"

def command_exit(arg):
    if arg:
        print("Command doesn't receive arguments")
        return True
    else:
        return False

def command_vfs_save(arg):
    if not arg:
        print("Wrong arguments")
    try:
        export_data = {}
        for path, info in vfs_data.items():
            item_copy = info.copy()
            if item_copy.get("type") == "file" and "content" in item_copy:
                file_text = item_copy["content"]
                b_text=file_text.encode('utf-8')
                item_copy["content"] = base64.b64encode(b_text).decode('utf-8')
            export_data[path] = item_copy
        with open(arg, "w", encoding="utf-8") as f:
            json.dump(vfs_data, f, indent=2, ensure_ascii=False)
        print(f"Successfully save into '{arg}'")
    except Exception as e:
        print(f"Saving error VFS: {e}")
    return True

def command_ls(arg):
    if not arg:
        print(f"[ls] Arguments: none")
    else:
        print(f"[ls] Arguments: {arg}")
    return True
    
def command_cd(arg):
	if not arg:
		print("[cd] Wrong arguments")
	else:
		print(f"[cd] Arguments: {arg}")
	return True

def commands(commnd,arg):
    if commnd == "exit":
        return command_exit(arg)
    elif commnd == "ls":
        return command_ls(arg)
    elif commnd == "cd":
        return command_cd(arg)
    elif commnd == "vfs-save":
        return command_vfs_save(arg)
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
    if len(sys.argv) < start_len:
        return
    vfs = sys.argv[1]
    invite = sys.argv[2]
    if len(sys.argv) > start_len:
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

if __name__ == "__main__":
    start()
