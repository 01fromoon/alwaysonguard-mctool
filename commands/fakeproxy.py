import socket
import threading
import time
import json
from colorama import Fore, Style

DEFAULTS = {
    "motd": "§eAlwaysOnGuard §cFakeProxy §7| §aProxy Check/Honeypot",
    "version": "1.19.4",
    "protocol": 762,
    "max": 1111,
    "online": 0,
    "port": 25565
}
LOG_FILE = "logs/fakeproxy_connections.log"

def log_connection(ip, port, username=None, reason="Handshake/Ping"):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        logline = f"[{timestamp}] {ip}:{port} - {reason}"
        if username:
            logline += f" - username: {username}"
        f.write(logline + "\n")

def build_status_response(opts):
    status = {
        "version": {"name": opts["version"], "protocol": opts["protocol"]},
        "players": {"max": opts["max"], "online": opts["online"], "sample": []},
        "description": {"text": opts["motd"]},
        "favicon": ""
    }
    status_json = json.dumps(status)
    data = status_json.encode("utf-8")
    packet = b"\x00" + len(data).to_bytes(1, 'big') + data
    packet_length = len(packet)
    return packet_length.to_bytes(1, 'big') + packet

def handle_client(conn, addr, opts):
    ip, port = addr
    try:
        data = conn.recv(1024)
        if not data:
            conn.close()
            return
        if data[0] in (0x00, 0x01, 0xFE):
            motd = build_status_response(opts)
            conn.sendall(motd)
            log_connection(ip, port, reason="Ping/Status")
        elif b"MC|PingHost" in data:
            motd = build_status_response(opts)
            conn.sendall(motd)
            log_connection(ip, port, reason="Legacy Ping")
        else:
            username = None
            try:
                username = data.decode(errors='ignore').split("\x00")[-1]
            except Exception:
                pass
            disconnect_msg = {"text": "§cFakeProxy: Giriş engellendi!"}
            disconnect_json = json.dumps(disconnect_msg).encode("utf-8")
            packet = b"\x00" + len(disconnect_json).to_bytes(1, 'big') + disconnect_json
            packet_length = len(packet)
            conn.sendall(packet_length.to_bytes(1, 'big') + packet)
            log_connection(ip, port, username=username, reason="Fake Login Reject")
    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[ERROR] {ip}:{port} - {e}\n")
    finally:
        conn.close()

def parse_args(args):
    import shlex
    result = DEFAULTS.copy()
    tokens = shlex.split(args)
    i = 0
    while i < len(tokens):
        t = tokens[i]
        if t == "--motd" and i+1 < len(tokens):
            result["motd"] = tokens[i+1]
            i += 2
        elif t == "--version" and i+1 < len(tokens):
            result["version"] = tokens[i+1]
            i += 2
        elif t == "--protocol" and i+1 < len(tokens):
            try: result["protocol"] = int(tokens[i+1])
            except: pass
            i += 2
        elif t == "--max" and i+1 < len(tokens):
            try: result["max"] = int(tokens[i+1])
            except: pass
            i += 2
        elif t == "--online" and i+1 < len(tokens):
            try: result["online"] = int(tokens[i+1])
            except: pass
            i += 2
        elif t == "--port" and i+1 < len(tokens):
            try: result["port"] = int(tokens[i+1])
            except: pass
            i += 2
        else:
            i += 1
    return result

def ask_opts_interactive(MESSAGES, lang):
    opts = DEFAULTS.copy()
    try:
        val = input(MESSAGES[lang]["fakeproxy_port"].format(port=opts["port"])).strip()
        if val: opts["port"] = int(val)
        val = input(MESSAGES[lang]["fakeproxy_motd"].format(motd=opts["motd"])).strip()
        if val: opts["motd"] = val
        val = input(MESSAGES[lang]["fakeproxy_version"].format(version=opts["version"])).strip()
        if val: opts["version"] = val
        val = input(MESSAGES[lang]["fakeproxy_protocol"].format(protocol=opts["protocol"])).strip()
        if val: opts["protocol"] = int(val)
        val = input(MESSAGES[lang]["fakeproxy_max"].format(max=opts["max"])).strip()
        if val: opts["max"] = int(val)
        val = input(MESSAGES[lang]["fakeproxy_online"].format(online=opts["online"])).strip()
        if val: opts["online"] = int(val)
    except Exception:
        pass
    return opts

def fakeproxy_command(args, MESSAGES, lang):
    print(Fore.LIGHTYELLOW_EX + "╔" + "═"*44 + "╗")
    print(Fore.LIGHTYELLOW_EX + "║" + Style.RESET_ALL + f"   {MESSAGES[lang]['fakeproxy_start']}   " + Fore.LIGHTYELLOW_EX + "║")
    print(Fore.LIGHTYELLOW_EX + "╚" + "═"*44 + "╝" + Style.RESET_ALL)
    if args.strip():
        opts = parse_args(args)
    else:
        print(Fore.CYAN + "[*] " + MESSAGES[lang]["fakeproxy_settings"] + Style.RESET_ALL)
        opts = ask_opts_interactive(MESSAGES, lang)
    print(Fore.GREEN + f"[+] " + MESSAGES[lang]["fakeproxy_listen"].format(port=opts['port']) + Style.RESET_ALL)
    print(Fore.YELLOW + "[!] " + MESSAGES[lang]["fakeproxy_log"] + Style.RESET_ALL)
    print(Fore.CYAN + "[*] " + MESSAGES[lang]["fakeproxy_ctrlc"] + "\n" + Style.RESET_ALL)
    import os
    if not os.path.exists("logs"):
        os.makedirs("logs")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', opts["port"]))
    server.listen(25)
    try:
        while True:
            conn, addr = server.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr, opts), daemon=True)
            t.start()
    except KeyboardInterrupt:
        print(Fore.LIGHTRED_EX + f"\n[!] {MESSAGES[lang]['fakeproxy_stop']}" + Style.RESET_ALL)
        server.close()