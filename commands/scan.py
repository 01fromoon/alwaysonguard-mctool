import os
import socket
import threading
from queue import Queue
from colorama import Fore, Style, init

init(autoreset=True)

def modern_print(msg, color=Fore.WHITE, icon=None, MESSAGES=None, lang=None):
    icons = {
        "success": f"{Fore.GREEN}✔{Style.RESET_ALL}",
        "fail": f"{Fore.RED}✘{Style.RESET_ALL}",
        "scan": f"{Fore.CYAN}🔎{Style.RESET_ALL}",
        "info": f"{Fore.BLUE}ℹ{Style.RESET_ALL}",
        "warn": f"{Fore.YELLOW}⚠{Style.RESET_ALL}",
        "ip": f"{Fore.LIGHTMAGENTA_EX}🌐{Style.RESET_ALL}",
        "port": f"{Fore.LIGHTCYAN_EX}🛡{Style.RESET_ALL}",
    }
    if icon and icon in icons:
        print(f"  {icons[icon]} {color}{msg}{Style.RESET_ALL}")
    else:
        print(f"  {color}{msg}{Style.RESET_ALL}")

def ask_input(msg, color=Fore.LIGHTMAGENTA_EX):
    return input(f"{color}{msg}{Style.RESET_ALL} ")

def parse_ips(ip_arg):
    if os.path.isfile(ip_arg):
        with open(ip_arg, "r") as f:
            return [line.strip() for line in f if line.strip()]
    elif "*" in ip_arg:
        base = ip_arg.split('.')[:-1]
        return [f"{'.'.join(base)}.{i}" for i in range(1, 255)]
    elif "," in ip_arg:
        return [ip.strip() for ip in ip_arg.split(",") if ip.strip()]
    else:
        return [ip_arg.strip()]

def parse_ports(port_arg):
    ports = set()
    for part in port_arg.split(","):
        part = part.strip()
        if '-' in part:
            start, end = part.split('-')
            ports.update(range(int(start), int(end)+1))
        else:
            ports.add(int(part))
    return sorted(list(ports))

def print_table_boxed(results, ips, ports, MESSAGES, lang):
    header = [MESSAGES[lang]["ip"], MESSAGES[lang]["port"], MESSAGES[lang]["state"], MESSAGES[lang]["service"]]
    rows = []
    for ip in ips:
        for port in ports:
            res = results.get((ip, port), None)
            state = MESSAGES[lang]["open"] if res and res['open'] else MESSAGES[lang]["closed"]
            svc = res['service'] if res else "-"
            rows.append([ip, str(port), state, svc])

    col_widths = [max(len(str(row[i])) for row in rows + [header]) for i in range(4)]
    col_widths = [w+2 for w in col_widths]

    total_width = sum(col_widths) + len(col_widths) + 1

    TL, TM, TR = "╔", "╦", "╗"
    ML, MM, MR = "╠", "╬", "╣"
    BL, BM, BR = "╚", "╩", "╝"
    H, V = "═", "║"
    print(Fore.LIGHTWHITE_EX + TL + H*(total_width-2) + TR + Style.RESET_ALL)
    head_line = V + "".join([
        f" {Fore.LIGHTCYAN_EX}{header[i]:<{col_widths[i]-1}}{Style.RESET_ALL}" for i in range(4)
    ]) + V
    print(head_line)
    print(Fore.LIGHTWHITE_EX + ML + H*(total_width-2) + MR + Style.RESET_ALL)
    for row in rows:
        state_col = Fore.GREEN + row[2] + Style.RESET_ALL if row[2]==MESSAGES[lang]["open"] else Fore.RED + row[2] + Style.RESET_ALL
        svc_col = Fore.LIGHTYELLOW_EX + row[3] + Style.RESET_ALL
        line = (V +
            f" {Fore.LIGHTWHITE_EX}{row[0]:<{col_widths[0]-1}}{Style.RESET_ALL}" +
            f" {Fore.LIGHTCYAN_EX}{row[1]:<{col_widths[1]-1}}{Style.RESET_ALL}" +
            f" {state_col:<{col_widths[2]}}" +
            f" {svc_col:<{col_widths[3]}}" +
            V
        )
        print(line)
    print(Fore.LIGHTWHITE_EX + BL + H*(total_width-2) + BR + Style.RESET_ALL)
    return rows, header, col_widths

def save_results_boxed(rows, header, col_widths, MESSAGES, lang):
    os.makedirs("saves", exist_ok=True)
    fname = os.path.join("saves", "savedscans.txt")
    with open(fname, "w", encoding="utf-8") as f:
        TL, TR, H = "╔", "╗", "═"
        ML, MR = "╠", "╣"
        BL, BR = "╚", "╝"
        V = "║"
        total_width = sum(col_widths) + len(col_widths) + 1
        f.write(TL + H*(total_width-2) + TR + "\n")
        head_line = V + "".join([
            f" {header[i]:<{col_widths[i]-1}}" for i in range(4)
        ]) + V + "\n"
        f.write(head_line)
        f.write(ML + H*(total_width-2) + MR + "\n")
        for row in rows:
            state_col = row[2]
            svc_col = row[3]
            line = (V +
                f" {row[0]:<{col_widths[0]-1}}" +
                f" {row[1]:<{col_widths[1]-1}}" +
                f" {state_col:<{col_widths[2]}}" +
                f" {svc_col:<{col_widths[3]}}" +
                V + "\n"
            )
            f.write(line)
        f.write(BL + H*(total_width-2) + BR + "\n")
    modern_print(MESSAGES[lang]["results_saved"].format(fname=fname), Fore.LIGHTYELLOW_EX, "info", MESSAGES, lang)

def port_worker(ip, queue, results, timeout):
    while not queue.empty():
        port = queue.get()
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            service = "-"
            if result == 0:
                try:
                    service = socket.getservbyport(port)
                except Exception:
                    service = "-"
                results[(ip, port)] = {'open': True, 'service': service}
            else:
                results[(ip, port)] = {'open': False, 'service': service}
            sock.close()
        except Exception:
            results[(ip, port)] = {'open': False, 'service': "-"}
        queue.task_done()

def scan_command(argstr="", MESSAGES=None, lang="tr"):
    BANNER = MESSAGES[lang]["scan_banner"]
    HELP = MESSAGES[lang]["scan_help"]
    print(BANNER)
    if not argstr.strip():
        modern_print(MESSAGES[lang]["no_arguments"], Fore.RED, "fail", MESSAGES, lang)
        print(HELP)
        return

    args = argstr.strip().split()
    if len(args) < 2:
        modern_print(MESSAGES[lang]["wrong_usage"], Fore.RED, "fail", MESSAGES, lang)
        print(HELP)
        return

    ip_arg = args[0]
    port_arg = args[1]
    threads = 60 
    for i, arg in enumerate(args):
        if arg == "--threads" and len(args) > i+1:
            try:
                threads = int(args[i+1])
            except: pass

    ips = parse_ips(ip_arg)
    ports = parse_ports(port_arg)

    modern_print(MESSAGES[lang]["scanning"].format(ips=len(ips), ports=len(ports), threads=threads), Fore.CYAN, "scan", MESSAGES, lang)
    results = {}
    for idx, ip in enumerate(ips):
        modern_print(MESSAGES[lang]["scanning_ip"].format(ip=ip), Fore.LIGHTMAGENTA_EX, "ip", MESSAGES, lang)
        queue = Queue()
        for port in ports:
            queue.put(port)
        threads_list = []
        for _ in range(min(threads, queue.qsize())):
            t = threading.Thread(target=port_worker, args=(ip, queue, results, 0.7))
            t.daemon = True
            t.start()
            threads_list.append(t)
        queue.join()
        for t in threads_list:
            t.join()
    rows, header, col_widths = print_table_boxed(results, ips, ports, MESSAGES, lang)
    save_results_boxed(rows, header, col_widths, MESSAGES, lang)