import time
import os
import json
from datetime import datetime
from colorama import init, Fore, Style
import requests
import socket
import importlib

ASCII_BLOCK = [
    "🟩🟩🟩⬜⬜🟩🟩🟩",
    "🟩🟩🟩🟩🟩🟩🟩⬜",
    "🟩⬛⬛🟩🟩⬛⬛⬜",
    "🟩⬛⬛🟩🟩⬛⬛🟩",
    "🟩🟩🟩⬛⬛⬜🟩🟩",
    "🟩🟩⬛⬛⬛⬛🟩⬜",
    "⬜🟩⬛⬛⬛⬛🟩🟩",
    "🟩🟩⬛🟩🟩⬛🟩🟩"
]

COLOR_MAP = {
    "🟩": Fore.GREEN,
    "⬛": Fore.BLACK,
    "⬜": Fore.WHITE
}

VERSION_TEXT = "AlwaysOnGuard Minecraft tool v1.0.0 - 01.06.2025"

LANGUAGES = {
    "1": {"code": "tr", "name": "Türkçe"},
    "2": {"code": "en", "name": "English"},
    "3": {"code": "es", "name": "Español"}
}

with open("messages.json", encoding="utf-8") as f:
    MESSAGES = json.load(f)

LANGUAGE_CHANGED_MSG = {
    "tr": "✔ Dil başarıyla Türkçe olarak değiştirildi.",
    "en": "✔ Language changed to English.",
    "es": "✔ El idioma se cambió a Español."
}

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_ascii_block_centered(animated=True, delay=0.08):
    init(autoreset=True)
    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80
    for line in ASCII_BLOCK:
        colored_line = ""
        for char in line:
            color = COLOR_MAP.get(char, Fore.RESET)
            colored_line += color + char + Style.RESET_ALL
        pad = (term_width - len(line)) // 2
        print(" " * pad + colored_line)
        if animated:
            time.sleep(delay)

def print_animated_text_centered(text, color=Fore.GREEN, delay=0.03):
    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80
    pad = (term_width - len(text)) // 2
    print(" " * pad, end='')
    for char in text:
        print(color + char + Style.RESET_ALL, end='', flush=True)
        time.sleep(delay)
    print()

def print_static_centered(text, color=Fore.WHITE):
    try:
        term_width = os.get_terminal_size().columns
    except OSError:
        term_width = 80
    pad = (term_width - len(text)) // 2
    print(" " * pad + color + text + Style.RESET_ALL)

def get_colored_prompt():
    return (
        Fore.RED + "AoA@mctool" +
        Fore.RESET + ":" +
        Fore.WHITE + "〜" +
        Fore.BLUE + "$ " +
        Style.RESET_ALL
    )

def choose_language():
    clear_screen()
    print("\n".join([f"{k}. {v['name']}" for k, v in LANGUAGES.items()]))
    print(LANGUAGES["1"]["name"] + " / " + LANGUAGES["2"]["name"] + " / " + LANGUAGES["3"]["name"])
    print(MESSAGES["en"].get("choose_lang", "Select language:"))
    while True:
        try:
            lang_choice = input("> ").strip()
            if lang_choice in LANGUAGES:
                return LANGUAGES[lang_choice]["code"]
            else:
                print("Invalid selection. Please try again.")
        except (EOFError):
            print()
            return None
        except KeyboardInterrupt:
            print()
            print(Fore.MAGENTA + MESSAGES["tr"].get("exiting", "Çıkılıyor...") + Style.RESET_ALL)
            time.sleep(2)
            return None

def print_help_box(lang):
    help_data = {
        "tr": [
            ("help", "Komut listesini ve açıklamaları gösterir"),
            ("exit", "Uygulamadan çıkar"),
            ("server [ip/domain]", "Minecraft sunucu bilgisini getirir"),
            ("dns [domain]", "Domainin DNS kayıtlarını gösterir"),
            ("ipinfo [ip]", "IP adresi hakkında bilgi verir"),
            ("iphistory [domain]", "Bir domainin geçmiş IP kayıtlarını listeler"),
            ("scan [ip/dosya] [port]", "Port taraması yapar"),
            ("botsattack [ip] [port] [sayi=10]", "Botlarla hedefe bağlantı kurar"),
            ("password [kullanıcıadı]", "Kullanıcı adı için tahmini şifre verir"),
            ("fakeproxy [--port P] [--motd M] ...", "Gelişmiş sahte Minecraft proxy başlatır"),
            ("language [tr/en/es]", "Dili değiştirir"),
        ],
        "en": [
            ("help", "Shows the list of commands and descriptions"),
            ("exit", "Exits the application"),
            ("server [ip/domain]", "Fetches Minecraft server info"),
            ("dns [domain]", "Shows DNS records of a domain"),
            ("ipinfo [ip]", "Shows info about an IP address"),
            ("iphistory [domain]", "Lists past IPs of a domain"),
            ("scan [ip/file] [port]", "Performs a port scan"),
            ("botsattack [ip] [port] [count=10]", "Connects bots to the target"),
            ("password [username]", "Gives a guessed password for username"),
            ("fakeproxy [--port P] [--motd M] ...", "Starts an advanced fake Minecraft proxy"),
            ("language [tr/en/es]", "Changes the language"),
        ],
        "es": [
            ("help", "Muestra la lista de comandos y descripciones"),
            ("exit", "Sale de la aplicación"),
            ("server [ip/domain]", "Obtiene información del servidor de Minecraft"),
            ("dns [domain]", "Muestra los registros DNS de un dominio"),
            ("ipinfo [ip]", "Muestra información sobre una dirección IP"),
            ("iphistory [domain]", "Lista IPs anteriores de un dominio"),
            ("scan [ip/archivo] [puerto]", "Realiza un escaneo de puertos"),
            ("botsattack [ip] [puerto] [cantidad=10]", "Conecta bots al objetivo"),
            ("password [usuario]", "Da una contraseña estimada para el usuario"),
            ("fakeproxy [--port P] [--motd M] ...", "Inicia un proxy Minecraft falso avanzado"),
            ("language [tr/en/es]", "Cambia el idioma"),
        ],
    }
    box_title = {
        "tr": " KULLANILABİLİR KOMUTLAR ",
        "en": " AVAILABLE COMMANDS ",
        "es": " COMANDOS DISPONIBLES "
    }[lang]
    border_color = Fore.LIGHTGREEN_EX
    cmd_color = Fore.LIGHTCYAN_EX
    desc_color = Fore.WHITE

    commands = help_data[lang]
    max_cmd_len = max(len(cmd) for cmd, _ in commands)
    max_desc_len = max(len(desc) for _, desc in commands)
    box_width = max_cmd_len + max_desc_len + 6  

    print(border_color + "╔" + "═"*box_width + "╗")
    print(border_color + "║" + Style.RESET_ALL + box_title.center(box_width) + border_color + "║")
    print(border_color + "╠" + "═"*box_width + "╣")
    for cmd, desc in commands:
        line = (
            border_color + "║ " +
            cmd_color + cmd.ljust(max_cmd_len) + Style.RESET_ALL +
            "  " +
            desc_color + desc.ljust(max_desc_len) + Style.RESET_ALL +
            border_color + " ║"
        )
        print(line)
    print(border_color + "╚" + "═"*box_width + "╝" + Style.RESET_ALL)

def main():
    init(autoreset=True)
    program_start_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lang = choose_language()
    if lang is None:
        return
    clear_screen()
    print_static_centered(VERSION_TEXT, color=Fore.LIGHTYELLOW_EX)
    print_static_centered(f"{MESSAGES[lang]['start_time']}: {program_start_time}", color=Fore.LIGHTBLUE_EX)
    print()
    welcome_text = MESSAGES[lang]["welcome"]
    print_animated_text_centered(welcome_text, Fore.GREEN, delay=0.02)
    time.sleep(0.1)
    print_ascii_block_centered(animated=True, delay=0.08)
    print()
    print_static_centered(MESSAGES[lang]["warning"], color=Fore.LIGHTRED_EX)
    print_static_centered(MESSAGES[lang]["greet"], color=Fore.CYAN)
    print()
    exiting = False
    prompt_str = get_colored_prompt()
    while True:
        try:
            if exiting:
                break
            command = input(prompt_str).strip()
            lower_command = command.lower()
            if lower_command == "help":
                print()
                print_help_box(lang)
                print()
            elif lower_command == "exit":
                print(Fore.MAGENTA + MESSAGES[lang]["bye"] + Style.RESET_ALL)
                break
            elif lower_command.startswith("language "):
                parts = command.split(maxsplit=1)
                if len(parts) < 2:
                    if lang == "tr":
                        print(Fore.YELLOW + "Kullanım: language [tr/en/es]" + Style.RESET_ALL)
                    elif lang == "es":
                        print(Fore.YELLOW + "Uso: language [tr/en/es]" + Style.RESET_ALL)
                    else:
                        print(Fore.YELLOW + "Usage: language [tr/en/es]" + Style.RESET_ALL)
                else:
                    new_lang = parts[1].strip().lower()
                    lang_codes = {"tr", "en", "es"}
                    if new_lang in lang_codes:
                        lang = new_lang
                        print(Fore.GREEN + LANGUAGE_CHANGED_MSG[lang] + Style.RESET_ALL)
                        print_static_centered(MESSAGES[lang]["greet"], color=Fore.CYAN)
                    else:
                        if lang == "tr":
                            print(Fore.RED + "Geçersiz dil kodu! (Kullanılabilir: tr, en, es)" + Style.RESET_ALL)
                        elif lang == "es":
                            print(Fore.RED + "¡Código de idioma inválido! (Disponible: tr, en, es)" + Style.RESET_ALL)
                        else:
                            print(Fore.RED + "Invalid language code! (Available: tr, en, es)" + Style.RESET_ALL)
            elif lower_command.startswith("fakeproxy"):
                try:
                    fakeproxy_mod = importlib.import_module("commands.fakeproxy")
                    fakeproxy_mod.fakeproxy_command(command[len("fakeproxy"):], MESSAGES, lang)
                except Exception as e:
                    print(Fore.RED + f"[ERROR] fakeproxy komutu çalıştırılırken hata oluştu: {e}" + Style.RESET_ALL)
            elif lower_command.startswith("server "):
                parts = command.split(maxsplit=1)
                if len(parts) < 2:
                    print(Fore.RED + MESSAGES[lang]["usage_server"] + Style.RESET_ALL)
                else:
                    server_addr = parts[1].strip()
                    try:
                        server_mod = importlib.import_module("commands.server")
                        server_mod.server_command(server_addr, MESSAGES, lang)
                    except Exception as e:
                        print(Fore.RED + f"[ERROR] server komutu çalıştırılırken hata oluştu: {e}" + Style.RESET_ALL)
            elif lower_command.startswith("dns "):
                parts = command.split(maxsplit=1)
                if len(parts) < 2:
                    print(Fore.RED + MESSAGES[lang]["usage_dns"] + Style.RESET_ALL)
                else:
                    domain = parts[1].strip()
                    try:
                        dns_mod = importlib.import_module("commands.dns")
                        dns_mod.dns_command(domain, MESSAGES, lang)
                    except Exception as e:
                        print(Fore.RED + f"[ERROR] dns komutu çalıştırılırken hata oluştu: {e}" + Style.RESET_ALL)
            elif lower_command.startswith("ipinfo "):
                parts = command.split(maxsplit=1)
                if len(parts) < 2:
                    print(Fore.RED + MESSAGES[lang]["usage_ipinfo"] + Style.RESET_ALL)
                else:
                    ip = parts[1].strip()
                    try:
                        ipinfo_mod = importlib.import_module("commands.ipinfo")
                        ipinfo_mod.ipinfo_command(ip, MESSAGES, lang)
                    except Exception as e:
                        print(Fore.RED + f"[ERROR] ipinfo komutu çalıştırılırken hata oluştu: {e}" + Style.RESET_ALL)
            elif lower_command.startswith("iphistory "):
                parts = command.split(maxsplit=1)
                if len(parts) < 2:
                    usage = MESSAGES[lang].get("usage_iphistory", "Kullanım: iphistory [domain]")
                    print(Fore.RED + usage + Style.RESET_ALL)
                else:
                    domain = parts[1].strip()
                    try:
                        iphistory_mod = importlib.import_module("commands.iphistory")
                        iphistory_mod.iphistory_command(domain, MESSAGES, lang)
                    except Exception as e:
                        print(Fore.RED + f"[ERROR] iphistory komutu çalıştırılırken hata oluştu: {e}" + Style.RESET_ALL)
            elif lower_command.startswith("scan"):
                scan_args = command.split(maxsplit=1)
                try:
                    scan_mod = importlib.import_module("commands.scan")
                    if len(scan_args) > 1:
                        scan_mod.scan_command(scan_args[1], MESSAGES, lang)
                    else:
                        scan_mod.scan_command("", MESSAGES, lang)
                except Exception as e:
                    print(Fore.RED + f"[ERROR] scan komutu çalıştırılırken hata oluştu: {e}" + Style.RESET_ALL)
            elif lower_command.startswith("botsattack"):
                bots_args = command.split(maxsplit=1)
                try:
                    bots_mod = importlib.import_module("commands.botsattack")
                    if len(bots_args) > 1:
                        bots_mod.botsattack_command(bots_args[1], MESSAGES, lang)
                    else:
                        bots_mod.botsattack_command("", MESSAGES, lang)
                except Exception as e:
                    print(Fore.RED + f"[ERROR] botsattack komutu çalıştırılırken hata oluştu: {e}" + Style.RESET_ALL)
            elif lower_command.startswith("password"):
                pw_args = command.split(maxsplit=1)
                try:
                    pw_mod = importlib.import_module("commands.password")
                    if len(pw_args) > 1:
                        pw_mod.password_command(pw_args[1], MESSAGES, lang)
                    else:
                        pw_mod.password_command("", MESSAGES, lang)
                except Exception as e:
                    print(Fore.RED + f"[ERROR] password komutu çalıştırılırken hata oluştu: {e}" + Style.RESET_ALL)
            elif lower_command == "":
                continue
            else:
                print(Fore.RED + MESSAGES[lang]["unknown"] + Style.RESET_ALL)
        except (EOFError):
            print()
            break
        except KeyboardInterrupt:
            if not exiting:
                print()
                print(Fore.MAGENTA + MESSAGES[lang]["exiting"] + Style.RESET_ALL)
                exiting = True
                try:
                    for _ in range(20):
                        time.sleep(0.1)
                except KeyboardInterrupt:
                    pass
                break
            else:
                break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
