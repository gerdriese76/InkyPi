import json
import os
import logging
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

class User:
    def __init__(self, username, password_hash):
        self.username = username
        self.password_hash = password_hash

    def to_dict(self):
        return {
            "username": self.username,
            "password_hash": self.password_hash
        }

    @classmethod
    def from_dict(cls, data):
        return cls(data["username"], data["password_hash"])

class UserManager:
    def __init__(self, config_dir):
        self.config_file = os.path.join(config_dir, "users.json")
        self.users = self.load_users()

    def load_users(self):
        if not os.path.exists(self.config_file):
            return {}
        try:
            with open(self.config_file, 'r') as f:
                data = json.load(f)
                return {u["username"]: User.from_dict(u) for u in data}
        except Exception as e:
            logger.error(f"Failed to load users: {e}")
            return {}

    def save_users(self):
        try:
            with open(self.config_file, 'w') as f:
                data = [u.to_dict() for u in self.users.values()]
                json.dump(data, f, indent=4)
        except Exception as e:
            logger.error(f"Failed to save users: {e}")

    def add_user(self, username, password):
        if username in self.users:
            return False
        self.users[username] = User(username, generate_password_hash(password))
        self.save_users()
        return True

    def delete_user(self, username):
        if username in self.users:
            del self.users[username]
            self.save_users()
            return True
        return False

    def verify_user(self, username, password):
        user = self.users.get(username)
        if user and check_password_hash(user.password_hash, password):
            return True
        return False
    
    def has_users(self):
        return len(self.users) > 0

    def get_users(self):
        return list(self.users.values())
