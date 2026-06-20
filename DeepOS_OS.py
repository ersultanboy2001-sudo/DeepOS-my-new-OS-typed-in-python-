from time import sleep as s
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.request
import urllib.parse
import json
import os
import threading
import random
import os

model = os.popen("getprop ro.product.model").read().strip()
brand = os.popen("getprop ro.product.brand").read().strip()
android = os.popen("getprop ro.build.version.release").read().strip()

phone_specs = {
    "model": model,
    "brand": brand,
    "android": android
}

SERVER_URL = "http://127.0.0.1:8000"

accounts = {
    "20010101": {"username": "er001", "password": "mypassword", "role": "developer"}
}

wifi = False
BootLoader = "Locked"

class DeepOS_Server(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        user_data = json.loads(post_data.decode('utf-8'))

        action = user_data.get("action")
        input_username = user_data.get("username", "").lower().strip()
        input_password = user_data.get("password", "").strip()

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        response = {}

        if action == "login":
            found_uid = None
            user_role = "user"

            for uid, info in accounts.items():
                if info["username"] == input_username and info["password"] == input_password:
                    found_uid = uid
                    user_role = info["role"]
                    break

            if found_uid:
                response = {"status": "success", "uid": found_uid, "role": user_role}
            else:
                response = {"status": "error", "message": "Wrong username or password!"}

        elif action == "register":
            name_taken = False
            for uid, info in accounts.items():
                if info["username"] == input_username:
                    name_taken = True
                    break

            if name_taken:
                response = {"status": "error", "message": "This username is already taken!"}
            else:
                while True:
                    new_uid = str(random.randint(100000, 200000))
                    if new_uid not in accounts:
                        break

                accounts[new_uid] = {
                    "username": input_username,
                    "password": input_password,
                    "role": "user"
                }

                print(f"\n[SERVER LOG]: New user registered! Name: {input_username} | Generated UID: {new_uid}")
                response = {"status": "success", "uid": new_uid, "role": "user"}

        self.wfile.write(json.dumps(response).encode('utf-8'))

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        uid = urllib.parse.parse_qs(parsed.query).get('uid', [None])[0]

        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()

        if uid in accounts:
            response = {
                "status": "success",
                "username": accounts[uid]["username"],
                "role": accounts[uid]["role"]
            }
        else:
            response = {"status": "error", "message": "UID not found"}

        self.wfile.write(json.dumps(response).encode('utf-8'))


def start_server_backend():
    server_address = ('127.0.0.1', 8000)
    HTTPServer(server_address, DeepOS_Server).serve_forever()


BootLoader = "Locked"
current_user = "Guest"
user_role = "user"
current_uid = "unknown"

def encrypt(text): return text[::-1]
def decrypt(text): return text[::-1]


def send_server_request(url, data_dict=None, method="GET"):
    try:
        if method == "POST":
            encoded_data = json.dumps(data_dict).encode('utf-8')
            req = urllib.request.Request(
                url,
                data=encoded_data,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )
        else:
            req = urllib.request.Request(url, method='GET')

        with urllib.request.urlopen(req, timeout=3) as response:
            return json.loads(response.read().decode('utf-8'))

    except Exception:
        return {"status": "error", "message": "Server connection failed"}


def auth_menu():
    global current_user, user_role, current_uid

    print("\n--- DEEPOS AUTHENTICATION SYSTEM ---")

    while True:
        choice = input("Type '1' to Login\nType '2' to Register\n>>> ").strip()

        if choice == "1":
            username = input("Enter Username: ")
            password = input("Enter Password: ")
            print("Connecting to auth server...")

            response = send_server_request(
                SERVER_URL,
                {"action": "login", "username": username, "password": password},
                method="POST"
            )

            if response["status"] == "success":
                current_user = username
                user_role = response["role"]
                current_uid = response["uid"]

                with open("system_uid.txt", "w") as f:
                    f.write(encrypt(current_uid))

                print("Login successful! Session saved.")
                break
            else:
                print(f"Error: {response.get('message','')}\n")

        elif choice == "2":
            username = input("Create Username: ")
            password = input("Create Password: ")

            response = send_server_request(
                SERVER_URL,
                {"action": "register", "username": username, "password": password},
                method="POST"
            )

            if response["status"] == "success":
                current_user = username
                user_role = response["role"]
                current_uid = response["uid"]

                with open("system_uid.txt", "w") as f:
                    f.write(encrypt(current_uid))

                print(f"Registration successful! Your generated Server UID is: {current_uid}")
                print("Session saved.")
                break
            else:
                print(f"Registration failed: {response.get('message','')}\n")


def boot_system():
    global current_user, user_role, current_uid

    print("boot-in components...(fast mode)")
    s(0.3)
    print("booting core...(it will take 5 seconds)")
    s(0.5)
    print("initing OS...")
    s(0.3)
    print("searching server for UID...")
    s(0.5)

    if os.path.exists("system_uid.txt"):
        encrypted_uid = open("system_uid.txt").read().strip()
        saved_uid = decrypt(encrypted_uid)

        response = send_server_request(f"{SERVER_URL}/?uid={saved_uid}")

        if response["status"] == "success":
            current_user = response["username"]
            user_role = response["role"]
            current_uid = saved_uid
        else:
            print("Saved UID is invalid or deleted from server.")
            auth_menu()
    else:
        auth_menu()

    print("Booting...")
    s(0.5)
    print("starting DeepOS...")
    s(1)
    print("=" * 40)
    print(f"Welcome to DeepOS 0.1.1.01!(Rework). Logged as: {current_user} [{user_role.upper()}]")
    print("Type /help to see available commands.")
    print("=" * 40)


if __name__ == "__main__":
    threading.Thread(target=start_server_backend, daemon=True).start()
    s(0.2)

    boot_system()

    while True:
        cmd = input(f"\n/users/0/server/uid/{current_uid}/data/deeposserv/cmd/shell/{current_user}/\n $ /").lower().strip()

        if cmd == "help":
            print("available commands:\n • /help\n • /logout\n • /dev\n • /settings\n • /wi-fi\n • /clicker\n • /rps")

        elif cmd == "logout":
            if wifi == False:
                print("JOIN TO WIFI FIRST!\n/wifi's/join/err01\n most recent call!")
            else:
                if os.path.exists("system_uid.txt"):
                    os.remove("system_uid.txt")
                    print("Session cleared! Restart DeepOS to log in again.")

        elif cmd == "dev":
            if BootLoader == "Locked":
                print("\nCoreError no 1//:BOOTLOADER LOCKED\nSYSERROR no 1:YOU NEED TO UNLOCK BootLoader v0.1\n")
            else:
                print("Developer mode:", user_role)

        elif cmd == "settings":
            print("=" * 35)
            print("DEEPOS SETTINGS v0.1.0")
            print("=" * 35)
            setting = input("type 1 to open characteristics page\ntype 2 for unlocking BootLoader\n>>> ").strip()

            if setting == "1":
                print("Characteristics page:\n")
                print("phone:")
                print("phone: ",phone_specs["brand"],end="",sep="")
                print("\nphone type:",phone_specs["model"],end="")
                print("\nandoid type:",phone_specs["android"],end="")
                
                print(f"\nAccount: {current_user} \nPrivilege: {user_role}")
            elif setting == "2":
                password = input("TYPE SYSTEM PASSWORD TO UNLOCK IT\n>>> ")
                if password == "20010101":
                    print("CONGRATULATIONS YOU UNLOCKED IT!")
                    BootLoader = "Unlocked"
                else:
                    print("Incorrect password!")

        elif cmd == "wi-fi":
            print(f"/data/deepos/deeposserv/user/{current_user}deepos/deepossys/systemapps/wifi/wifiloader/load/\n wifi's:\n • Kirguz\n")
            wificheck = input("type wi-fi name for join\n/load/wifi's/kirguz/password/passwordcheck\n>>>").lower().strip()

            if wificheck == "kirguz":
                password2 = input("NEED PASSWORD!\n>>>")
                if password2 == "12344321":
                    print("joined to wifi succesfully!")
                    wifi = True
                else:
                    print("invalid wifi password!")
            else:
                print("invalid wifi name!")

        elif cmd == "clicker":
            print("=== DEEP-CLICKER ===")
            clicks = 0
            while True:
                user_input = input("Press ENTER to click (type 'exit' to quit): ")
                if user_input.lower() == 'exit':
                    break
                clicks += 1
                print(f"Total clicks: {clicks}")

        elif cmd == "rps":
            print("=== ROCK, PAPER, SCISSORS ===")
            choices = ["rock", "paper", "scissors"]
            ai_choice = random.choice(choices)
            user_choice = input("Choose (rock/paper/scissors): ").lower()

            if user_choice in choices:
                print(f"DeepOS chose: {ai_choice}")
                if user_choice == ai_choice:
                    print("It's a tie! 🤝")
                elif (user_choice == "rock" and ai_choice == "scissors") or \
                     (user_choice == "scissors" and ai_choice == "paper") or \
                     (user_choice == "paper" and ai_choice == "rock"):
                    print("You win! 🎉")
                else:
                    print("DeepOS wins! 🤖")
            else:
                print("Error: Invalid choice!")

        else:
            print("Users/Commands/404NotFound://\nShellError no 1:// Incorrect command")
