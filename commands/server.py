import socket
from colorama import Fore, Style
from mcstatus import JavaServer
import time

def paint(text, color=Fore.LIGHTGREEN_EX):
    print(color + text + Style.RESET_ALL)

def check_domain(server):
    try:
        socket.inet_aton(server.split(":")[0])
        return False
    except socket.error:
        return True

def get_ip_port(server):
    if ':' in server:
        host, port = server.split(':', 1)
    else:
        host, port = server, 25565
    try:
        ip = socket.gethostbyname(host)
        port = int(port)
        return ip, port
    except Exception:
        return None, None

def mcstatus(server):
    try:
        address, port = (server.split(":") + [25565])[:2]
        port = int(port)
        mcserver = JavaServer(address, port)
        status = mcserver.status()
        motd = status.description if isinstance(status.description, str) else str(status.description)
        version = status.version.name if hasattr(status.version, "name") else "?"
        protocol = status.version.protocol if hasattr(status.version, "protocol") else "?"
        players = f"{status.players.online}/{status.players.max}"
        ping = int(status.latency)
        s = (motd + " " + version).lower()
        if "bungeeguard" in s:
            server_type = "bungeeguard"
        elif "waterfall" in s:
            server_type = "waterfall"
        elif "paper" in s:
            server_type = "paper"
        elif "velocity" in s:
            server_type = "velocity"
        elif "spigot" in s:
            server_type = "spigot"
        elif "purpur" in s:
            server_type = "purpur"
        else:
            server_type = "unknown"
        return [address, motd, version, protocol, players, ping, server_type]
    except Exception:
        return None

def show_server(server, address, motd, version, protocol, players, ping, server_type, MESSAGES, lang):
    print(Fore.LIGHTCYAN_EX + f"\n[{MESSAGES[lang]['server_info']}]" + Style.RESET_ALL)
    print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['server']}]   " + Fore.LIGHTWHITE_EX + f"{server}" + Style.RESET_ALL)
    print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['ip']}]       " + Fore.LIGHTWHITE_EX + f"{address}" + Style.RESET_ALL)
    print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['motd']}]     " + Fore.LIGHTWHITE_EX + f"{motd}" + Style.RESET_ALL)
    print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['version']}]  " + Fore.LIGHTWHITE_EX + f"{version}" + Style.RESET_ALL)
    print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['protocol']}] " + Fore.LIGHTWHITE_EX + f"{protocol}" + Style.RESET_ALL)
    print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['players']}]  " + Fore.LIGHTWHITE_EX + f"{players}" + Style.RESET_ALL)
    print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['ping']}]     " + Fore.LIGHTWHITE_EX + f"{ping}ms" + Style.RESET_ALL)
    print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['type']}]     " + Fore.LIGHTGREEN_EX + f"{server_type}" + Style.RESET_ALL)

def server_command(server, MESSAGES, lang):
    """
    Gets information about the specified server.
    :param server: IP/Domain and Port (example: mc.alwaysonguard.net or 1.2.3.4:25565)
    :param MESSAGES: Message dictionary for localization
    :param lang: Selected language key
    """
    try:
        old_server = server
        if check_domain(server):
            ip, port = get_ip_port(server)
            if ip is not None:
                server = f"{ip}:{port}"

        paint(f"\n  [INFO] {server} {MESSAGES[lang]['getting_data']}", Fore.LIGHTCYAN_EX)
        time.sleep(0.3)
        paint(f"  [INFO] {server} {MESSAGES[lang]['sending_bots']}", Fore.LIGHTGREEN_EX)
        time.sleep(0.3)

        data = mcstatus(server)
        if data is not None:
            show_server(server, *data, MESSAGES, lang)
        else:
            if check_domain(server):
                data = mcstatus(old_server)
                if data is not None:
                    show_server(server, *data, MESSAGES, lang)
                    return
            paint(f'\n  [ERROR] {MESSAGES[lang]["server_unreachable"]}', Fore.LIGHTRED_EX)
    except KeyboardInterrupt:
        return