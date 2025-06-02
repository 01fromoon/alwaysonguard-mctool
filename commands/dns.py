import socket
from colorama import Fore, Style

def paint(text, color=Fore.LIGHTGREEN_EX):
    print(color + text + Style.RESET_ALL)

def get_dns_records(domain):
    records = []
    try:
        for result in socket.getaddrinfo(domain, None, socket.AF_INET):
            ip = result[4][0]
            records.append((domain, ip, "A"))
    except Exception:
        pass
    try:
        for result in socket.getaddrinfo(domain, None, socket.AF_INET6):
            ip = result[4][0]
            records.append((domain, ip, "AAAA"))
    except Exception:
        pass
    return records

def dns_command(server_address, MESSAGES, lang):
    """
    Girilebilen domain ve IP'leri listeler.
    :param server_address: Domain veya IP adresi
    :param MESSAGES: messages.json içeriği
    :param lang: seçili dil anahtarı
    """
    paint(f"\n  [INFO] {server_address} {MESSAGES[lang]['dns_searching']}...", Fore.LIGHTCYAN_EX)
    records = get_dns_records(server_address)
    if records:
        print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['dns_records']}]" + Style.RESET_ALL)
        for domain, ip, record_type in records:
            print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['domain']}]   " + Fore.LIGHTWHITE_EX + f"{domain}" + Style.RESET_ALL)
            print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['ip']}]       " + Fore.LIGHTWHITE_EX + f"{ip}" + Style.RESET_ALL)
            print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['type']}]     " + Fore.LIGHTGREEN_EX + f"{record_type}" + Style.RESET_ALL)
            print(Fore.LIGHTCYAN_EX + "----------------------" + Style.RESET_ALL)
    else:
        paint(f"  [ERROR] {MESSAGES[lang]['dns_not_found']}", Fore.LIGHTRED_EX)