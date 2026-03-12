# Simple Password Manager with encryption!
#These imports are for encryption!
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import json
import hashlib
from getpass import getpass
# Define the base directory for storing files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
passwords_path = os.path.join(BASE_DIR, "passwords.json")
salt_path = os.path.join(BASE_DIR, "salt.key")
master_path = os.path.join(BASE_DIR, "master.hash")

print("Loading from:", passwords_path)
# Function to generate a key from the master password
def generate_key(master_password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(master_password.encode()))
    return key
# Check if salt exists, if not create one

if os.path.exists(salt_path):
    with open(salt_path, "rb") as salt_file:
        salt = salt_file.read()
else:
    salt = os.urandom(16)
    with open(salt_path, "wb") as salt_file:
        salt_file.write(salt)
# Try to load existing data
try:
    with open(passwords_path, "r") as file:
        data = json.load(file)
except FileNotFoundError:
    data = {}
# Master password setup / verification
if not os.path.exists(master_path):

    print("No master password found.")
    master_password = getpass("Create a master password: ")

    hashed = hashlib.sha256(master_password.encode()).hexdigest()

    with open(master_path, "w") as f:
        f.write(hashed)

    print("Master password created!")

else:

    master_password = getpass("Enter your master password: ")
    hashed = hashlib.sha256(master_password.encode()).hexdigest()

    with open(master_path, "r") as f:
        stored_hash = f.read()

    if hashed != stored_hash:
        print("Incorrect master password. Exiting.")
        exit()
key = generate_key(master_password, salt)
fernet = Fernet(key)

while True:
    # Display the menu
    print("\nPassword Manager")
    print("1. Add a new password")
    print("2. View saved passwords")
    print("3. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        website = input("Enter the website: ")
        email = input("Enter the email: ")
        password = input("Enter the password: ")
        encrypted_password = fernet.encrypt(password.encode()).decode()
        print("DEBUG ENCRYPTED:", encrypted_password)  # Debugging line to check encryption

        data[website] = {
            "email": email,
            "password": encrypted_password
        }

        # Save immediately after adding
        with open(passwords_path, "w") as file:
            json.dump(data, file, indent=4)

        print("Password saved successfully!")

    elif choice == "2":
        if not data:
            print("No saved passwords found.")
        else:
            for website, credentials in data.items():
                encrypted_password = credentials.get("password")
                email = credentials.get("email")
                try:
                    decrypted_password = fernet.decrypt(encrypted_password.encode()).decode()
                except Exception:
                    decrypted_password = "<decryption failed>"
                print(f"Website: {website}\n  Email: {email}\n  Password: {decrypted_password}\n")

    elif choice == "3":
        # Save before exiting
        with open(passwords_path, "w") as file:
            json.dump(data, file, indent=4)

        print("Exiting the Password Manager. Goodbye!")
        break

    else:
        print("Invalid choice. Please select 1, 2, or 3.")