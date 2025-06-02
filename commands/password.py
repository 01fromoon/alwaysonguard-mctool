import time
from colorama import Fore, Style, init

init(autoreset=True)

def password_command(argstr="", MESSAGES=None, lang="tr"):
    username = argstr.strip()
    if not username:
        print(Fore.RED + "[ERROR] " + MESSAGES[lang]["username_required"] + Style.RESET_ALL)
        print(Fore.LIGHTYELLOW_EX + MESSAGES[lang]["password_usage"] + Style.RESET_ALL)
        return

    print(Fore.LIGHTCYAN_EX + MESSAGES[lang]["querying_password"].format(username=username) + Style.RESET_ALL)
    time.sleep(2)
    print(Fore.LIGHTRED_EX + MESSAGES[lang]["user_not_found"].format(username=username) + Style.RESET_ALL)