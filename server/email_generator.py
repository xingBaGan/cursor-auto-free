import random
import time
from config import Config

class EmailGenerator:
    def __init__(self):
        configInstance = Config()
        self.domain = configInstance.get_domain()
        self.default_password = self.generate_password()
        self.default_first_name = self.generate_random_name()
        self.default_last_name = self.generate_random_name()

    def generate_password(self, length=12):
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
        return "".join(random.choices(chars, k=length))

    def generate_random_name(self, length=6):
        first_letter = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        rest_letters = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length - 1))
        return first_letter + rest_letters

    def generate_email(self, length=8):
        random_str = "".join(random.choices("abcdefghijklmnopqrstuvwxyz", k=length))
        timestamp = str(int(time.time()))[-6:]
        return f"{random_str}{timestamp}@{self.domain}"

    def get_account_info(self):
        return {
            "email": self.generate_email(),
            "password": self.default_password,
            "first_name": self.default_first_name,
            "last_name": self.default_last_name,
        } 