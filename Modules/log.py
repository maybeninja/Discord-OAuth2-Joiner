import datetime
import os
import threading
from colorama import Fore, Style, init

class Logger:
    def __init__(self) -> None:
        init(autoreset=True)
        self.colors = {
            "green": Fore.GREEN,
            "red": Fore.RED,
            "yellow": Fore.YELLOW,
            "blue": Fore.BLUE,
            "magenta": Fore.MAGENTA,
            "cyan": Fore.CYAN,
            "white": Fore.WHITE,
            "black": Fore.BLACK,
            "reset": Style.RESET_ALL,
            "lightblack": Fore.LIGHTBLACK_EX,
            "lightred": Fore.LIGHTRED_EX,
            "lightgreen": Fore.LIGHTGREEN_EX,
            "lightyellow": Fore.LIGHTYELLOW_EX,
            "lightblue": Fore.LIGHTBLUE_EX,
            "lightmagenta": Fore.LIGHTMAGENTA_EX,
            "lightcyan": Fore.LIGHTCYAN_EX,
            "lightwhite": Fore.LIGHTWHITE_EX
        }
        # Initialize a threading lock
        self.lock = threading.Lock()

    def clear(self):
        os.system("cls" if os.name == "nt" else "clear")

    def timestamp(self):
        return datetime.datetime.now().strftime("%H:%M:%S") 

    def log(self, message, obj, color, label):
        with self.lock:  # Ensure that only one thread can write at a time
            print(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors[color]}{label} {self.colors['lightblack']}➜ {self.colors['white']}{message} [{self.colors[color]}{obj}{self.colors['white']}] {self.colors['reset']}")

    def captcha(self, message, obj=""):
        self.log(message, obj, "lightcyan", "SOLVED")

    def revoked(self, message, obj=""):
        self.log(message, obj, "lightmagenta", "REVOKED")

    def success(self, message, obj=""):
        self.log(message, obj, "lightmagenta", "SUCCESS")

    def created(self, message, obj=""):
        self.log(message, obj, "lightgreen", "CREATED")

    def error(self, message, obj=""):
        self.log(message, obj, "lightred", "ERROR")

    def warning(self, message, obj=""):
        self.log(message, obj, "lightyellow", "WARN")

    def info(self, message, obj=""):
        self.log(message, obj, "lightblue", "INFO")

    def custom(self, message, obj, color):
        self.log(message, obj, color, color.upper())

    def input(self, message):
        with self.lock:  
            return input(f"{self.colors['lightblack']}{self.timestamp()} » {self.colors['lightcyan']}INPUT   {self.colors['lightblack']}➜ {self.colors['white']}{message}{self.colors['reset']}")
