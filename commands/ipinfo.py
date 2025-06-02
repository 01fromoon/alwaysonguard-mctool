import requests
from colorama import Fore, Style

def ipinfo_command(ip, MESSAGES, lang):
    print(Fore.CYAN + f"\n[#] {ip} {MESSAGES[lang]['ipinfo_getting']}..." + Style.RESET_ALL)

    try:
        url = f"http://ip-api.com/json/{ip}?fields=status,message,continent,country,regionName,city,timezone,isp,org"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("status") != "success":
            print(Fore.RED + f"[ERROR] {MESSAGES[lang]['ipinfo_failed']}: {data.get('message', MESSAGES[lang]['unknown_error'])}" + Style.RESET_ALL)
            return

        print(Fore.LIGHTCYAN_EX + f"[{MESSAGES[lang]['ip_info']}]" + Style.RESET_ALL)
        print(f"{Fore.LIGHTCYAN_EX}{MESSAGES[lang]['continent']}: {Fore.LIGHTWHITE_EX}{data.get('continent', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}{MESSAGES[lang]['country']}:   {Fore.LIGHTWHITE_EX}{data.get('country', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}{MESSAGES[lang]['region']}:    {Fore.LIGHTWHITE_EX}{data.get('regionName', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}{MESSAGES[lang]['city']}:      {Fore.LIGHTWHITE_EX}{data.get('city', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}{MESSAGES[lang]['timezone']}:  {Fore.LIGHTWHITE_EX}{data.get('timezone', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}{MESSAGES[lang]['isp']}:       {Fore.LIGHTWHITE_EX}{data.get('isp', 'N/A')}{Style.RESET_ALL}")
        print(f"{Fore.LIGHTCYAN_EX}{MESSAGES[lang]['org']}:       {Fore.LIGHTWHITE_EX}{data.get('org', 'N/A')}{Style.RESET_ALL}")

    except Exception as e:
        print(Fore.RED + f"[ERROR] {MESSAGES[lang]['ipinfo_error']}: {e}" + Style.RESET_ALL)