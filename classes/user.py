#   Name: Kayden Ye
#   Date: 30/06/2025
#   File: classes/user.py

import hashlib

class User:
    def __init__(self, 
                 username: str,
                 email: str,
                 password_hash: str):
        
        self.username = username
        self.email = email
        self.password_hash = password_hash  # Already hashed

    def __str__(self):
        return f"User(username='{self.username}', email='{self.email}')"

    def get_username(self):
        return self.username

    def get_email(self):
        return self.email

    def get_password_hash(self):
        return self.password_hash

    def set_username(self, new_username: str):
        self.username = new_username

    def set_email(self, new_email: str):
        self.email = new_email

    def set_password(self, raw_password: str):
        self.password_hash = self.hash_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return self.hash_password(raw_password) == self.password_hash

    @staticmethod
    def hash_password(password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()
