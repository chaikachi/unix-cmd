import os
import socket
import sys
import json
import base64

vfs_data = {}
cur_path = "/"
start_len = 3
mvcp_len = 2
byte = 1024

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

def child_path(t_path, flag_a, flag_l, flag_h):
    child_files = vfs_data[t_path].get("content",[])
    all_files = []
    for name in child_files:
        if t_path == "/":
            path = f"/{name}"
        else:
            path = f"{cur_path}/{name}"
        path_info = vfs_data.get(path,{}).copy()
        path_info["name"] = name
        all_files.append(path_info)
    return command_ls_l(command_ls_a(all_files, flag_a), flag_l, flag_h)
                
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
    if len(parts) < mvcp_len:
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
    if len(parts) < mvcp_len:
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

def command_ls_h(size, flag_h):
    if not flag_h:
        return f"{size}"
    else:
        sizes=["B","KB","MB","GB","TB"]
        count=0
        while size >= byte:
            count += 1
            size /= byte
        if count==0:
            return f"{size}B"
        else:
            return f"{size:.1f}{sizes[count]}"

def command_ls_a(all_files, flag_a):
    if flag_a:
        show_files=all_files
    else:
        show_files=[f for f in all_files if not f["name"].startswith('.')]
    return show_files

def command_ls_l(show_files,flag_l, flag_h):
    for files in show_files:
        if flag_l:
            size = command_ls_h(files.get("size",0),flag_h)
            rights = files.get('rights')
            date = files.get('date', "Oct 10")
            name = files.get('name', "name")
            links = files.get('links', "-")
            admin = files.get('admin', "admin")
            group = files.get('group', "group")
            print(f"{rights} {links} {admin} {group} {size} {date} {name}")
        else:
            print(files.get("name"))
    return True

def command_ls(arg, flag_a, flag_h, flag_l):
    global cur_path
    if not arg:
        if cur_path in vfs_data and vfs_data[cur_path]["type"] == "dir":
            child_path(cur_path, flag_a, flag_l, flag_h)
    elif arg:
        t_path = abs_path(arg)
        if t_path in vfs_data:
            if vfs_data[t_path]["type"] == "dir":
                child_path(t_path, flag_a, flag_l, flag_h)
            else:
                print(f"{arg} not a directory")
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
            print(f"{arg} not a directory")
    else:
        print(f"Wrong directory {arg}")
    return True

def command_rev(arg):
    if not arg:
            print("Waiting for arguments...")
            arg = str(input())
    print("".join(arg)[::-1])
    return True

def command_who():
    print(f"{os.getlogin()} {socket.gethostname()}")
    return True

def command_whoami(arg):
    if arg:
        print("Command doesn't receive arguments")
    else:
        print(os.getlogin())
    return True

def command_exit(arg):
    if arg:
        print("Command doesn't receive arguments")
        return True
    else:
        return False
    
def commands(commnd,arg,flag_a = False, flag_h = False, flag_l = False):
    if commnd == "exit": return command_exit(arg)
    elif commnd == "ls": return command_ls(arg, flag_a, flag_h, flag_l)
    elif commnd == "cd": return command_cd(arg)
    elif commnd == "vfs-save": return command_vfs_save(arg)
    elif commnd == "cp": return command_cp(arg)
    elif commnd == "mv": return command_mv(arg)
    elif commnd == "rev": return command_rev(arg)
    elif commnd == "who": return command_who()
    elif commnd == "whoami": return command_whoami(arg)  
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
            if commnd == "ls":
                arg, flag_a, flag_h, flag_l = ls_parcer(parser, commnd)
            else:
                arg = " ".join(parser[1:]) if len(parser) > 1 else ""
            commands(commnd, arg)

def ls_parcer(parser, commnd):
    flag_a=False
    flag_h=False
    flag_l=False
    remaining=[]
    for part in parser[1:]:
        if part.startswith("-"):
            if "a" in part:
                flag_a = True
            if "l" in part:
                flag_l = True
            if "h" in part:
                flag_h = True
        else:
            remaining.append(part)
    arg = " ".join(remaining)
    return arg, flag_a, flag_h, flag_l

def start_settings():
    if len(sys.argv) < start_len:
        return False
    vfs = sys.argv[1]
    invite = sys.argv[2]
    if len(sys.argv) > start_len:
        script = sys.argv[3]
    else:
        script = ""
    print(f"VFS: {vfs}\nREPL: {invite}\nStarter script path: {script}")
    if not load_vfs(vfs) or (script and not run_start_script(script, invite)):
        return False
    return True

def start():
    if not start_settings():
        return
    interactive_invite = welcome_to_input()
    while True:
        flag_a, flag_h, flag_l = False, False, False
        inputt = input(interactive_invite + " ")
        parser = inputt.strip().split()
        if not parser:
            continue
        commnd = parser[0]
        if commnd=="ls":
            arg, flag_a, flag_h, flag_l = ls_parcer(parser, commnd)
        else:
            arg = " ".join(parser[1:]) if len(parser) > 1 else ""
        if not commands(commnd, arg, flag_a, flag_h, flag_l):
            break
        
if __name__ == "__main__":
    start()
