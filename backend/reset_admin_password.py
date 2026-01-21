import json
import bcrypt
import os

def load_json(filename, default=None):
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return json.load(f)
    return default

def save_json(filename, data):
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

users = load_json('users.json')
if 'admin@legal.com' in users:
    print("Found admin user. Updating password...")
    password = "123456"
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    users['admin@legal.com']['password'] = hashed
    save_json('users.json', users)
    print(f"Password for admin@legal.com reset to {password} (Hash: {hashed})")
else:
    print("Admin user not found!")
