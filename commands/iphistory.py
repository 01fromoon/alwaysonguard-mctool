import socket
import requests
from colorama import Fore, Style

def truncate(text, max_len):
    return text if len(text) <= max_len else text[:max_len-3] + "..."

def iphistory_command(domain, MESSAGES, lang):
    print(Fore.CYAN + f"\n[#] {MESSAGES[lang]['iphistory_for']}: {domain}" + Style.RESET_ALL)
    header_ip = MESSAGES[lang]['ip_address']
    header_org = MESSAGES[lang]['organization']
    ip_col_width = 18
    org_col_width = 40

    print(Fore.LIGHTGREEN_EX + f"{header_ip:<{ip_col_width}}  {header_org:<{org_col_width}}" + Style.RESET_ALL)
    print(Fore.LIGHTGREEN_EX + "-" * (ip_col_width + org_col_width + 2) + Style.RESET_ALL)

    try:
        try:
            ips = socket.gethostbyname_ex(domain)[2]
            if not ips:
                print(Fore.RED + "[ERROR] " + MESSAGES[lang]['no_a_records'] + Style.RESET_ALL)
                return
        except socket.gaierror:
            print(Fore.RED + "[ERROR] " + MESSAGES[lang]['domain_not_resolved'] + Style.RESET_ALL)
            return

        for ip in ips:
            try:
                url = f"http://ip-api.com/json/{ip}?fields=status,message,org"
                resp = requests.get(url, timeout=5)
                data = resp.json()
                org = truncate(data.get("org", "N/A"), org_col_width) if data.get("status") == "success" else "N/A"
                print(f"{Fore.WHITE}{ip:<{ip_col_width}}  {Fore.LIGHTCYAN_EX}{org}{Style.RESET_ALL}")
            except Exception as e:
                print(f"{Fore.RED}[ERROR] {MESSAGES[lang]['info_for_ip_failed'].format(ip=ip, error=e)}{Style.RESET_ALL}")

    except Exception as e:
        print(Fore.RED + f"[ERROR] {MESSAGES[lang]['iphistory_general_error']}: {e}" + Style.RESET_ALL)