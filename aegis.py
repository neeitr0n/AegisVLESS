import sqlite3
import json
import socket
import random
import os
import subprocess
import base64
import datetime
import threading
import time
import re
import string 
import argparse
import shutil
import textwrap 
from http.server import BaseHTTPRequestHandler, HTTPServer

# --- Configuration ---

SNI_SELECTION_MODE = "" # "best_ping" or "random_sni";  best_ping = finds lowest latency ; random_sni = random choice from pool
PORT_SELECTION_MODE = "" # "dynamic" or "standard";       dynamic = dynamic random ports (42k-65k) ; standard = common web ports e.g 80, 443, 2053 and other
MY_REMARK = ""
SECRET_PATH = ""

STANDARD_PORTS = [

    80, 443, 2053, 2083, 2087, 2096, 8443,
    81, 8000, 8001, 8008, 8080, 8081, 8082, 8880, 8888,
    8444, 9443, 3128, 3129, 5000, 5001, 5500, 6000,
    2082, 2086, 2089, 2095, 2099

]

ALLOWED = string.ascii_letters + string.digits

# ---------------------

def ensure_firewall_port(port):
    try:
        check_status = subprocess.check_output(["sudo", "ufw", "status"]).decode()

        if str(port) not in check_status:
            print(f"[Firewall] Port {port} is closed. Opening...")
            subprocess.run(["sudo", "ufw", "allow", f"{port}/tcp"], check=True, capture_output=True)
            print(f"[Firewall] Port {port} successfully opened!")

        else:
            print(f"[Firewall] Port {port} is already allowed in UFW.")

    except Exception as e:
        print(f"[Warning] Firewall check failed: {e}")
        print("Make sure to run the script with 'sudo'.")

def close_firewall_port(port):
    try:
        check_status = subprocess.check_output(["sudo", "ufw", "status"]).decode()
        
        if str(port) in check_status:
            print(f"[Firewall] Port {port} is no longer needed. Closing...")
            subprocess.run(["sudo", "ufw", "delete", "allow", f"{port}/tcp"], check=True, capture_output=True)
            print(f"[Firewall] Port {port} closed successfully.")

    except Exception as e:
        print(f"[Warning] Failed to close old port {port}: {e}")        

def rotation_worker(sur, nav, db_file, remark):
    temp_remark = f"{remark}_migration"

    while True:
        wait_seconds = random.randint(3600, 10800)

        now = datetime.datetime.now()
        wake_up_time = now + datetime.timedelta(seconds=wait_seconds)

        delta = datetime.timedelta(seconds=wait_seconds)
        print(f"\n[Scheduler] Timer started: waiting for {delta}")
        print(f"[Scheduler] Next rotation at: {wake_up_time.strftime('%H:%M:%S')}")

        time.sleep(wait_seconds)

        print("\n[Scheduler] Time's up! Starting scheduled rotation...")
        
        if SNI_SELECTION_MODE == "best_ping":
            new_sni = nav.get_best_sni()
        elif SNI_SELECTION_MODE == "random_sni":
            new_sni = nav.get_random_sni()

        if PORT_SELECTION_MODE == 'standard':
            new_port = nav.get_standard_port(current_port)
        elif PORT_SELECTION_MODE == 'dynamic':
            new_port = nav.find_free_port()

        new_sid = nav.get_random_shortid()

        ensure_firewall_port(new_port)

        if sur.clone_inbound(db_file, remark, temp_remark, new_port, new_sni, new_sid):
            try:
                subprocess.run(["x-ui", "restart"], check=True)

                inbound_data = sur.get_inbound_info(db_file, temp_remark)
                if inbound_data:
                    id_in, port_in, proxy_settings, net_settings = inbound_data

                    new_link = sur.generate_vless_link(port_in, proxy_settings, net_settings, remark)
                    SubscriptionHandler.vless_link = new_link

                    print(f"[Scheduler] Subscription updated to new port {port_in}. Waiting for clients to migrate...")

                time.sleep(2400)

                print("[Scheduler] Finalizing migration: removing old inbound and renaming new one...")
                sur.delete_inbound(db_file, remark)
                sur.rename_inbound(db_file, temp_remark, remark)

                subprocess.run(["x-ui", "restart"], check=True)
                print(f"[Scheduler] Seamless migration complete. Port {new_port} is now primary.")

            except Exception as e:
                print(f"[Scheduler] Error during migration steps: {e}")    

def first_time_setup():
    global SNI_SELECTION_MODE, PORT_SELECTION_MODE, MY_REMARK, SECRET_PATH

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_box([
            "AegisVLESS - First-Time Setup",
            "",
            "Enter the inbound remark name to manage:"
        ])
        remark = input(">>> ").strip()
        if not remark:
            print_box(["Error: remark cannot be empty!"])
            input("Press Enter to continue...")
            continue

        if sur.get_inbound_info(DB_FILE, remark):
            MY_REMARK = remark
            break

        print_box([f"Error: inbound «{remark}» not found in DB."])
        input("Press Enter to try again...")

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_box([
            "Select SNI Selection Mode:",
            "[1] BestPing - choose SNI with lowest latency",
            "[2] Random - random SNI from pool",
            "",
            "Enter choice (1/2):"
        ])
        choice = input(">>> ").strip()
        if choice == '1':
            SNI_SELECTION_MODE = "best_ping"
            break
        if choice == '2':
            SNI_SELECTION_MODE = "random_sni"
            break
        print_box(["Invalid choice - please enter 1 or 2."])
        input("Press Enter to continue...")

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_box([
            "Select Port Selection Mode:",
            "[1] Dynamic - random ports (49152-65535)",
            "[2] Standard - common web-ports (80,443,2053 …)",
            "",
            "Enter choice (1/2):"
        ])
        choice = input(">>> ").strip()
        if choice == '1':
            PORT_SELECTION_MODE = "dynamic"
            break
        if choice == '2':
            PORT_SELECTION_MODE = "standard"
            break
        print_box(["Invalid choice - please enter 1 or 2."])
        input("Press Enter to continue...")

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_box([
            "Select Subscription Path Mode:",
            "[1] Generate secure random path (32 chars)",
            "[2] Enter custom path",
            "",
            "Enter choice (1/2):"
        ])
        choice = input(">>> ").strip()
        if choice == '1':
            SECRET_PATH = generate_secure_path()
            print_box([f"Generated path: {SECRET_PATH}"])
            input("Press Enter to continue...")
            break

        if choice == '2':
            os.system('cls' if os.name == 'nt' else 'clear')
            print_box(["Enter your custom path (e.g mysecretpath; only letters and numbers):"])
            custom = input(">>> ").strip()
            if not custom:
                print_box(["Error: path cannot be empty!"])
                input("Press Enter to continue...")
                continue
            SECRET_PATH = sanitize_path(custom)
            break

        print_box(["Invalid choice - please enter 1 or 2."])
        input("Press Enter to continue...")

    script_path = os.path.abspath(__file__)
    try:
        with open(script_path, 'r') as f:
            content = f.read()

        updates = [
            (r'^(SNI_SELECTION_MODE\s*=\s*)["\'][^"\']*["\']',
             f'\\1"{SNI_SELECTION_MODE}"'),
            (r'^(PORT_SELECTION_MODE\s*=\s*)["\'][^"\']*["\']',
             f'\\1"{PORT_SELECTION_MODE}"'),
            (r'^(MY_REMARK\s*=\s*)["\'][^"\']*["\']',
             f'\\1"{MY_REMARK}"'),
            (r'^(SECRET_PATH\s*=\s*)["\'][^"\']*["\']',
             f'\\1"{SECRET_PATH}"')
        ]

        for pattern, repl in updates:
            content = re.sub(pattern, repl, content, flags=re.MULTILINE)

        with open(script_path, 'w') as f:
            f.write(content)

        os.system('cls' if os.name == 'nt' else 'clear')
        print_box([
            "First-Time setup completed successfully!",
            "",
            f"Inbound remark : {MY_REMARK}",
            f"SNI mode       : {SNI_SELECTION_MODE}",
            f"Port mode      : {PORT_SELECTION_MODE}",
            f"Secret path    : {SECRET_PATH}"
        ])
        input("Press Enter to continue...")

    except Exception as e:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_box([f"[Error] Could not save configuration: {e}"])
        input("Press Enter to continue...")

def generate_secure_path(length=32):
    random_path = ''.join(random.choice(ALLOWED) for _ in range(length))
    return f"/{random_path}"

def sanitize_path(raw_path: str) -> str:
    cleaned = "".join(ch for ch in raw_path.lstrip("/") if ch in ALLOWED)

    if not cleaned:
        return generate_secure_path()
    else:
        return "/" + cleaned

def _calc_inner_width(lines: list) -> int:
    longest = max(len(l) for l in lines)
    need    = longest + 2
    term_w  = shutil.get_terminal_size((80, 24)).columns
    return min(max(need, 32), term_w - 2)


def _border(inner: int, top: bool = True) -> str:
    left  = "╔" if top else "╚"
    right = "╗" if top else "╝"
    return f"{left}{'═' * inner}{right}"


def _line(text: str, inner: int) -> str:
    usable = inner - 2
    if len(text) > usable:
        text = textwrap.shorten(text, width=usable, placeholder="…")
    return f"║ {text:<{usable}} ║"


def print_box(lines: list):
    inner = _calc_inner_width(lines)
    print(_border(inner, top=True))
    for line in lines:
        print(_line(line, inner))
    print(_border(inner, top=False))

class Surgeon: 
    def __init__(self):
        pass

    def get_inbound_info(self, db_path, remark_name):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            query = "SELECT id, port, settings, stream_settings FROM inbounds WHERE remark = ?"
            cursor.execute(query, (remark_name,))
            row = cursor.fetchone()

            if row:
                inbound_id, port, proxy_settings_raw, stream_settings_raw = row

                network_settings = json.loads(stream_settings_raw)
                while isinstance(network_settings, str):
                    network_settings = json.loads(network_settings)

                proxy_settings = json.loads(proxy_settings_raw)
                while isinstance(proxy_settings, str):
                    proxy_settings = json.loads(proxy_settings)

                sni = network_settings.get('realitySettings', {}).get('serverNames', ['Not Found'])[0]

                #print(f"Success! Current server: {remark_name}")
                #print(f"Current port: {port}")
                #print(f"Current SNI domain: {sni}")

                return inbound_id, port, proxy_settings, network_settings
            else:
                print(f"Error! Server ({remark_name}) not founded!")
                return None
        
        except Exception as e:
            print(f"Error occured while reading the database: {e}")    
        finally:
            if conn:
                conn.close()  
    
    def update_inbound(self, db_path, inbound_id, new_port, settings, new_sni, new_sid):
        try:
            if isinstance(new_sni, dict) and isinstance(settings, str):
                settings, new_sni = new_sni, settings

            if 'realitySettings' in settings:

                settings['realitySettings']['serverNames'] = [new_sni]
                settings['realitySettings']['target'] = f"{new_sni}:443"
                settings['realitySettings']['shortIds'] = [new_sid]

                if 'settings' not in settings['realitySettings']:
                    settings['realitySettings']['settings'] = {}

                settings['realitySettings']['settings']['serverName'] = new_sni
                settings['realitySettings']['settings']['padding'] = True

            updated_settings_raw = json.dumps(settings)

            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            query = "UPDATE inbounds SET port = ?, stream_settings = ? WHERE id = ?"
            cursor.execute(query, (new_port, updated_settings_raw, inbound_id))

            conn.commit()
            print(f"[Surgeon] Database updated: ID: {inbound_id} -> Port: {new_port}, SNI Domain: {new_sni}, SID: {new_sid}")
            return True
        
        except Exception as e:
            print(f"[Surgeon] Critical update error: {e}")
            return False
        
        finally:
            if conn:
                conn.close()

    def clone_inbound(self, db_path, original_remark, temp_remark, new_port, new_sni, new_sid):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("DELETE FROM inbounds WHERE remark = ? OR tag = ?", (temp_remark, temp_remark))

            cursor.execute("SELECT up, down, total, remark, enable, expiry_time, listen, port, protocol, settings, stream_settings, tag, sniffing from inbounds WHERE remark = ?", (original_remark,))
            row = list(cursor.fetchone())

            row[3] = temp_remark
            row[7] = new_port
            row[11] = temp_remark

            net_settings = json.loads(row[10])
            if 'realitySettings' in net_settings:
                net_settings['realitySettings']['serverNames'] = [new_sni]
                net_settings['realitySettings']['target'] = f"{new_sni}:443"
                net_settings['realitySettings']['shortIds'] = [new_sid]
            row[10] = json.dumps(net_settings)

            proxy_settings = json.loads(row[9])
            if 'clients' in proxy_settings:
                for client in proxy_settings['clients']:

                    if client['email'].endswith('_mig'):
                        client['email'] = client['email'][:-4]
                    else:
                        client['email'] = f"{client['email']}_mig"  

            row[9] = json.dumps(proxy_settings)        

            placeholders = ','.join(["?"] * len(row))
            query = f"INSERT INTO inbounds (up, down, total, remark, enable, expiry_time, listen, port, protocol, settings, stream_settings, tag, sniffing) VALUES ({placeholders})"
            cursor.execute(query, row)

            conn.commit()
            print(f"[Surgeon] Inbound Clone created: {temp_remark} on port {new_port}")
            return True
        
        except Exception as e:
            print(f"[Surgeon] Clone error: {e}")
            return False
        finally:
            conn.close()

    def delete_inbound(self, db_path, remark_name):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT id FROM inbounds WHERE remark = ?", (remark_name,))
            ids = cursor.fetchall()

            for row_id in ids:
                cursor.execute("DELETE FROM client_traffics WHERE inbound_id = ?", (row_id[0],))

            cursor.execute("DELETE FROM inbounds WHERE remark = ?", (remark_name,))
            conn.commit()

            print(f"[Surgeon] Inbound deleted: {remark_name}")
            return True
        
        except Exception as e:
            print(f"[Surgeon] Delete error: {e}")
        finally:
            conn.close()

    def rename_inbound(self, db_path, old_remark, new_remark):
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inbounds WHERE remark = ? OR tag = ?", (new_remark, new_remark))
            cursor.execute("UPDATE inbounds SET remark = ?, tag = ? WHERE remark = ?", (new_remark, new_remark, old_remark))
            conn.commit()

            print(f"[Surgeon] Renamed: {old_remark} -> {new_remark}")
            return True
        
        except Exception as e:
            print(f"[Surgeon] Rename error: {e}")
            return False
        finally:    
            conn.close()

    def generate_vless_link(self, port, proxy_settings, network_settings, remark, nav=None):
        try:
            ip_cmd = subprocess.check_output(["curl", "-s", "ifconfig.me"])
            server_ip = ip_cmd.decode("utf-8").strip()

            user_uuid = proxy_settings.get('clients', [{}])[0].get('id', 'no-id')

            reality = network_settings.get('realitySettings', {})
            sni = reality.get('serverNames', ['google.com'])[0]
            pbk = reality.get('settings', {}).get('publicKey', 'no-key')
            sid = reality.get('shortIds', [''])[0]

            noise_params = ""
            if nav:
                noise = nav.get_noise_settings()

                noise_params = f"&fp={noise['fp']}&seed={noise['seed']}"
                if noise['padding']:
                    noise_params += "&padding=1"

            else:
                noise_params = "&fp=chrome"        

            current_time = datetime.datetime.now().strftime("%H:%M")
            new_remark = f"{remark}_{current_time}"

            link = f"vless://{user_uuid}@{server_ip}:{port}?type=tcp&encryption=none&security=reality&sni={sni}{noise_params}&pbk={pbk}&sid={sid}#{new_remark}"

            return link
        
        except Exception as e:
            print(f"[Surgeon] Link creating error: {e}")
            return None

    def register_as_service(self):
        service_path = "/etc/systemd/system/aegis.service"

        print("[System] Registering AegisPort as a system serivce...")

        script_path = os.path.abspath(__file__)
        work_dir = os.path.dirname(script_path)

        service_code = f"""[Unit]
Description=Aegis Surgeon Subscription Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory={work_dir}
ExecStart=/usr/bin/python3 -u {script_path}
Restart=always

[Install]
WantedBy=multi-user.target
"""
        try:
            with open(service_path, "w") as f:
                f.write(service_code)

            subprocess.run(["systemctl", "daemon-reload"], check=True)
            print("[OK] Service registered successfully.")

            self.set_autostart_state(enabled=True)

        except PermissionError:
            print("[Error] Run the script with 'sudo' to register the service")

        except Exception as e:
            print(f"[Error] Failed to register service: {e}")

    def set_autostart_state(self, enabled=True):
        if not os.path.exists("/etc/systemd/system/aegis.service"):
            print("[!] The service must be registered first.")
            return
        
        action = "enable" if enabled else "disable"

        try:
            subprocess.run(["systemctl", action, "aegis"], check=True)
            status_text = "ENABLED" if enabled else "DISABLED"
            print(f"[System] Autostart on server boot: {status_text}")

        except Exception as e:
            print(f"[Error] Error changing autostart state: {e}")

    def uninstall_service(self):
        try:
            subprocess.run(["systemctl", "stop", "aegis"], check=False)
            subprocess.run(["systemctl", "disable", "aegis"], check=False)

            service_path = "/etc/systemd/system/aegis.service"
            if os.path.exists(service_path):
                os.remove(service_path)
                
            subprocess.run(["systemctl", "daemon-reload"], check=False)
            
            print("[System] Aegis service uninstalled successfully!")
            return True
            
        except Exception as e:
            print(f"[Error] Failed to uninstall service: {e}")
            return False            

class Navigator:
    def __init__(self, port_range=(49152,65535), max_attempts = 10):
        self.port_range = port_range
        self.max_attempts = max_attempts
        self.sni_pool = [
            "rutube.ru", "yandex.ru", "ya.ru", "www.python.org",
            "www.microsoft.com", "www.apple.com", "www.samsung.com", "www.oracle.com",
            "www.pinterest.com", "www.python.org", "www.kernel.org", "www.cisco.org",
            "www.nvidia.com", "www.amd.com"
        ]

    def find_free_port(self):
        attempts = 0
        while attempts < self.max_attempts:
            port = random.randint(*self.port_range)
            attempts += 1

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", port))
                    print(f"[Navigator] Available port found: {port}; attemps: {attempts}")
                    return port

                except socket.error:
                    print(f"[Navigator] Port {port} taken, trying next...")
                    continue    

        raise Exception(f"Failed to find an available port after {self.max_attempts} attempts.")  
    
    def get_standard_port(self, current_port=None):
        candidates = [p for p in STANDARD_PORTS if p != current_port]
        random.shuffle(candidates)

        for port in candidates:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                try:
                    s.bind(("127.0.0.1", port))
                    return port
                except OSError:
                    continue
        raise RuntimeError("No free standard port found")

    def get_random_sni(self):
        selected = random.choice(self.sni_pool)
        print(f"[Navigator] SNI choosen: {selected}")
        return selected
    
    def get_random_shortid(self):
        sid = "".join(random.choices("0123456789abcdef", k=8))
        print(f"[Navigator] New ShortID generated: {sid}")
        return sid
    
    def get_noise_settings(self):

        fingerprints = ["chrome", "firefox", "safari", "edge", "qq"]
        return {
            "fp": random.choice(fingerprints),
            "padding": random.choice([True, False]),
            "seed": "".join(random.choices("0123456789abcdef", k=32))
        }
    
    def get_best_sni(self):
        print(f"[Navigator] Analyzing SNI pool for best latency...")
        results = []

        for sni in self.sni_pool:
            try:
                start = time.time()
                with socket.create_connection((sni, 443), timeout=2):
                    latency = (time.time() - start) * 1000
                results.append((sni, latency))
                print(f"Domain - {sni}: {int(latency)}ms")

            except:
                print(f"Domain - {sni}: Connection failed (skipped)")
                continue

        if not results:
            return self.get_random_sni()

        best_sni = min(results, key=lambda x: x[1])[0]
        print(f"[Navigator] Winner: {best_sni}")
        return best_sni    

class SubscriptionHandler(BaseHTTPRequestHandler):
    
    vless_link = ""
    secret_path = SECRET_PATH if SECRET_PATH else generate_secure_path()

    def do_GET(self):
        
        if self.path == self.secret_path:
        
            encoded_content = base64.b64encode(self.vless_link.encode("utf-8")).decode("utf-8")
            
            self.send_response(200)
            self.send_header("Content-type", "text/plain; charset=utf-8")
            self.end_headers()

            self.wfile.write(encoded_content.encode("utf-8"))
            print(f"[Server] Subscription was delivered successfully: {self.client_address}")

        else:
            self.send_error(404, "Not Found")

    def log_message(self, format, *args):
        return        

class AegisManager:
    def __init__(self, surgeon, navigator, db_file, remark):
        self.sur = surgeon
        self.nav = navigator
        self.db_file = db_file
        self.remark = remark

    def _ui_lines(self):

        title   = "Aegis - Configuration Menu"
        status  = f"Service Status: {'Running' if self.check_service_status() else 'Inactive'}"
        inbound = f"Current Inbound: {self.remark}"
        sni     = f"Current SNI Mode: {SNI_SELECTION_MODE}"
        port    = f"Current Port Mode: {PORT_SELECTION_MODE}"

        menu_items = [
            "[1] Show Current Configuration",
            "[2] Change SNI Selection Mode",
            "[3] Change Port Selection Mode",
            "[4] Change Inbound",
            "[5] Change Subscription Path",
            "[6] Start Service",
            "[7] Stop Service",
            "[8] Restart Service",
            "[9] Uninstall Service",
            "[10] Exit"
        ]

        return [title, status, inbound, sni, port] + menu_items

    def _calc_inner_width(self) -> int:
        longest = max(len(line) for line in self._ui_lines())
        needed  = longest + 2
        term_width = shutil.get_terminal_size((80, 24)).columns
        inner = min(max(needed, 32), term_width - 2)
        return inner

    def _border(self, inner: int, top: bool = True) -> str:
        left  = "╔" if top else "╚"
        right = "╗" if top else "╝"
        return f"{left}{'═' * inner}{right}"

    def _line(self, text: str, inner: int) -> str:
        usable = inner - 2
        if len(text) > usable:
            text = textwrap.shorten(text, width=usable, placeholder="…")
        return f"║ {text:<{usable}} ║"

    def _print_box(self, lines: list[str], inner: int):
        print(self._border(inner, top=True))
        for line in lines:
            print(self._line(line, inner))
        print(self._border(inner, top=False))

    def show_menu(self):
        while True:
            os.system('cls' if os.name == 'nt' else 'clear')
            inner = self._calc_inner_width()

            self._print_box(["Aegis - Configuration Menu"], inner)

            info = [
                f"Service Status: {'Running' if self.check_service_status() else 'Inactive'}",
                f"Current Inbound: {self.remark}",
                f"Current SNI Mode: {SNI_SELECTION_MODE}",
                f"Current Port Mode: {PORT_SELECTION_MODE}"
            ]
            self._print_box(info, inner)

            menu_items = [
                "[1] Show Current Configuration",
                "[2] Change SNI Selection Mode",
                "[3] Change Port Selection Mode",
                "[4] Change Inbound",
                "[5] Change Subscription Path",
                "[6] Start Service",
                "[7] Stop Service",
                "[8] Restart Service",
                "[9] Uninstall Service",
                "[10] Exit"
            ]
            self._print_box(menu_items, inner)

            choice = input("\n Enter your choice (1-10): ").strip()

            if choice == '1':
                self.show_current_configuration()

            elif choice == '2':
                self.change_sni_mode()

            elif choice == '3':
                self.change_port_mode()

            elif choice == '4':
                self.change_inbound_remark()

            elif choice == '5':
                self.change_secret_path()

            elif choice == '6':
                self.start_service()

            elif choice == '7':
                self.stop_service()

            elif choice == '8':
                self.restart_service()

            elif choice == '9':
                self.uninstall_service()

            elif choice == '10':
                os.system('cls' if os.name == 'nt' else 'clear')
                print("Goodbye!\n")
                break

            else:
                print("Invalid choice. Please try again.")
                input("Press 'Enter' to continue...")

    def show_current_configuration(self):
        inbound_data = self.sur.get_inbound_info(self.db_file, self.remark)
        
        if inbound_data:
            id_in, port_in, proxy_in, net_in = inbound_data

            user_uuid = proxy_in.get('clients', [{}])[0].get('id', 'N/A')
            current_sid = net_in.get('realitySettings', {}).get('shortIds', ['N/A'])[0]
            current_sni = net_in.get('realitySettings', {}).get('serverNames', ['N/A'])[0]

            link = self.sur.generate_vless_link(port_in, proxy_in, net_in, self.remark)

            ip_cmd = subprocess.check_output(["curl", "-s", "ifconfig.me"]).decode().strip()
            sub_url = f"http://{ip_cmd}:8080{SubscriptionHandler.secret_path}"

            print(f"Inbound ID:   {id_in}")
            print(f"Remark:       {self.remark}")
            print(f"Current Port: {port_in}")
            print(f"Current SNI:  {current_sni}")
            print(f"ShortID:      {current_sid}")
            print(f"User UUID:    {user_uuid}\n")

            print("="*50)
            print("Current Subscription Data")
            print("="*50)
            print(f"\nClient VLESS Link: \n\n{link}")
            print(f"\nSubscription Server URL: \n\n{sub_url}\n")
            print("="*50)

        else:
            print("[Error] Could not retrieve current configuration.")

        input("\nPress 'Enter' to continue...")

    def change_inbound_remark(self):
        global MY_REMARK
        print(f"Current inbound remark: {MY_REMARK}")
        
        while True:
            new_remark = input("Enter new inbound remark name: ").strip()
            if new_remark:
                inbound_data = self.sur.get_inbound_info(self.db_file, new_remark)

                if inbound_data:
                    self.update_config_in_code("MY_REMARK", new_remark)
                    MY_REMARK = new_remark
                    self.remark = new_remark
                    print(f"Inbound remark changed to: {new_remark}")
                    self.restart_service_quiet()
                    break

                else:
                    print(f"[Error] Inbound '{new_remark}' not found in database!")
                    retry = input("Do you want to try again? (y/N): ").strip().lower()
                    
                    if retry != 'y':
                        break

            else:
                print("Inbound remark cannot be empty!")
        
        input("\nPress Enter to continue...")

    def change_secret_path(self):
        global SECRET_PATH

        print(f"\nCurrent path: {SECRET_PATH or '(generated automatically)'}\n")
        while True:
            print("[1] Generate a new secure random path")
            print("[2] Enter custom path manually")
            choice = input("Select an option (1/2): ").strip()

            if choice == '1':
                new_path = generate_secure_path()
                print(f"[System] Generated path: {new_path}")
                break

            if choice == '2':
                new_path = input("Enter path (any symbols will be stripped, only letters and digits are kept): ").strip()
                if not new_path:
                    print("[Error] Path cannot be empty!")
                    continue

                new_path = sanitize_path(new_path)
                break


            print("[Error] Invalid choice. Please enter '1' or '2'")

        self.update_config_in_code("SECRET_PATH", new_path)

        SECRET_PATH = new_path
        SubscriptionHandler.secret_path = new_path

        print(f"[Config] SECRET_PATH changed to: {new_path}")

        self.restart_service_quiet()
        input("\nPress Enter to continue...")

    def check_service_status(self):
        try:
            result = subprocess.run(["systemctl", "is-active", "aegis"], 
                                capture_output=True, text=True, check=False)
            return result.stdout.strip() == "active"
        except:
            return False

    def show_service_status(self):
        if self.check_service_status():
            print("╔════════════════════════════════╗")
            print("║ Service Status: Running        ║")
        else:
            print("╔════════════════════════════════╗")
            print("║ Service Status: Inactive       ║")

    def show_current_modes(self):
        print(f"║ Current SNI Mode: {SNI_SELECTION_MODE}             ║")
        print(f"║ Current Port Mode: {PORT_SELECTION_MODE}            ║")
        print("╚════════════════════════════════╝")

    def change_sni_mode(self):
        global SNI_SELECTION_MODE        
        print("Current SNI modes:")
        print("1. best_ping - Selects SNI with lowest latency")
        print("2. random_sni - Randomly selects SNI from pool")
        
        choice = input("Select mode (1 or 2): ").strip()
        if choice == '1':
            self.update_config_in_code("SNI_SELECTION_MODE", "best_ping")
            SNI_SELECTION_MODE = "best_ping"
            print("SNI mode changed to: best_ping")
            self.restart_service_quiet()
        elif choice == '2':
            self.update_config_in_code("SNI_SELECTION_MODE", "random_sni")
            SNI_SELECTION_MODE = "random_sni"
            print("SNI mode changed to: random_sni")
            self.restart_service_quiet()
        else:
            print("Invalid choice")
        input("\nPress Enter to continue...")

    def change_port_mode(self):
        global PORT_SELECTION_MODE
        print("Current port modes:")
        print("1. dynamic - Uses Dynamic ports (49152-65535)")
        print("2. standard - Uses Standard Web ports (80, 443, etc.)")
        
        choice = input("Select mode (1 or 2): ").strip()
        if choice == '1':
            self.update_config_in_code("PORT_SELECTION_MODE", "dynamic")
            PORT_SELECTION_MODE = "dynamic"
            print("Port mode changed to: dynamic")
            self.restart_service_quiet()
        elif choice == '2':
            self.update_config_in_code("PORT_SELECTION_MODE", "standard")
            PORT_SELECTION_MODE = "standard"
            print("Port mode changed to: standard")
            self.restart_service_quiet()
        else:
            print("Invalid choice")
        input("\nPress Enter to continue...")

    def reset_config(self):
        global SNI_SELECTION_MODE, PORT_SELECTION_MODE, MY_REMARK, SECRET_PATH
        SNI_SELECTION_MODE = ""
        PORT_SELECTION_MODE = ""
        MY_REMARK = ""
        SECRET_PATH = ""

        self.remark = ""
        SubscriptionHandler.secret_path = ""

        self.update_config_in_code("SNI_SELECTION_MODE", "")
        self.update_config_in_code("PORT_SELECTION_MODE", "")
        self.update_config_in_code("MY_REMARK", "")
        self.update_config_in_code("SECRET_PATH", "")

        print("[Config] All runtime configuration cleared.")

    def update_config_in_code(self, var_name, new_value):
        try:
            script_path = os.path.abspath(__file__)
            
            with open(script_path, 'r') as f:
                content = f.read()
            
            pattern = f'^({var_name}\\s*=\\s*)["\'][^"\']*["\']'
            replacement = f'\\1"{new_value}"'
            new_content = re.sub(pattern, replacement, content, flags=re.MULTILINE)
            
            with open(script_path, 'w') as f:
                f.write(new_content)
                
            print(f"[Config] {var_name} permanently updated to '{new_value}'")
            
        except Exception as e:
            print(f"[Error] Could not update configuration: {e}")

    def restart_service_quiet(self):
        try:
            subprocess.run(["systemctl", "restart", "aegis"], 
                        capture_output=True, check=False)
            print("[Service] Restarted to apply new settings")

        except Exception as e:
            print(f"[Warning] Could not restart service: {e}")
            print("Please restart service manually for changes to take effect")

    def start_service(self):
        try:
            subprocess.run(["systemctl", "start", "aegis"], check=True)
            print("[System] Aegis service started successfully!")

        except Exception as e:
            print(f"[Error] Failed to start service: {e}")

        input("\nPress 'Enter' to continue...")    

    def stop_service(self):
        try:
            subprocess.run(["systemctl", "stop", "aegis"], check=True)
            print("[System] Aegis service stopped successfully!")

        except Exception as e:
            print(f"[Error] Failed to stop service: {e}")

        input("\nPress 'Enter' to continue...")

    def restart_service(self):
        try:
            subprocess.run(["systemctl", "restart", "aegis"], check=True)
            print("[System] Aegis service restarted successfully!")

        except Exception as e:
            print(f"[Error] Failed to restart service: {e}")

        input("\nPress 'Enter' to continue...")

    def uninstall_service(self):
        confirm = input("Are you sure you want to uninstall Aegis service? (y/N): ").strip().lower()
        if confirm == 'y':
        
            if self.sur.uninstall_service():
                self.reset_config()
                print("Service uninstalled successfully!")
            else:
                print("Uninstallation failed.")

        else:
            print("Uninstallation canceled.")
        
        input("\nPress 'Enter' to continue...")    

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='AegisVLESS')
    parser.add_argument('-menu', '--menu', action='store_true', help='Open interactive menu')

    args = parser.parse_args()

    SERVER_DB = "/etc/x-ui/x-ui.db"
    DB_FILE = SERVER_DB if os.path.exists(SERVER_DB) else "x-ui.db"

    sur = Surgeon()
    nav = Navigator()

    if args.menu:
        aegis_manager = AegisManager(sur, nav, DB_FILE, MY_REMARK)
        aegis_manager.show_menu()
        exit(0)
    
    is_service = os.getenv("INVOCATION_ID") is not None
    service_exists = os.path.exists("/etc/systemd/system/aegis.service")

    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"--- AegisPort: Running on {DB_FILE} ---")

    if not os.path.exists("/etc/systemd/system/aegis.service"):
        print("[System] First run detected. Performing system configuration...")

        first_time_setup()

        sur.register_as_service()
   
        print("\n[System] First-time setup completed. Loading configuration...")
        
        with open(__file__, 'r') as f:
            content = f.read()
        
        import re
        sni_match = re.search(r'^SNI_SELECTION_MODE\s*=\s*"([^"]*)"', content, re.MULTILINE)
        port_match = re.search(r'^PORT_SELECTION_MODE\s*=\s*"([^"]*)"', content, re.MULTILINE)
        remark_match = re.search(r'^MY_REMARK\s*=\s*"([^"]*)"', content, re.MULTILINE)
        
        SNI_SELECTION_MODE = sni_match.group(1) if sni_match else ""
        PORT_SELECTION_MODE = port_match.group(1) if port_match else ""
        MY_REMARK = remark_match.group(1) if remark_match else ""
        
        print("[System] Configuration loaded, starting service...\n")
        subprocess.run(["sudo", "systemctl", "start", "aegis"], check=False)

        exit(0)

    if not is_service and service_exists:

        inbound_data = sur.get_inbound_info(DB_FILE, MY_REMARK)
        if inbound_data:
            id_in, port_in, proxy_in, net_in = inbound_data

            user_uuid = proxy_in.get('clients', [{}])[0].get('id', 'N/A')
            current_sid = net_in.get('realitySettings', {}).get('shortIds', ['N/A'])[0]
            current_sni = net_in.get('realitySettings', {}).get('serverNames', ['N/A'])[0]

            link = sur.generate_vless_link(port_in, proxy_in, net_in, MY_REMARK)

            ip_cmd = subprocess.check_output(["curl", "-s", "ifconfig.me"]).decode().strip()
            sub_url = f"http://{ip_cmd}:8080{SubscriptionHandler.secret_path}"

            print(f"Inbound ID:   {id_in}")
            print(f"Remark:       {MY_REMARK}")
            print(f"Current Port: {port_in}")
            print(f"Current SNI:  {current_sni}")
            print(f"ShortID:      {current_sid}")
            print(f"User UUID:    {user_uuid}")

            print("\n" + "="*50)
            print("Current Subscription Data:")
            print("="*50)
            print(f"\nClient VLESS link: \n\n{link}")
            print(f"\nSubscription Server URL: \n\n{sub_url}\n")
            print("="*50)


        print("\n[!] Aegis is already running as a system service.")
        print("[!] To update ports, use: 'sudo systemctl restart aegis'")
        print("[!] To see logs, use: 'sudo journalctl -u aegis -f'\n")
        print("[!] For managment options, run with '-menu' argument:\n")
        print("[#] 'sudo python3 aegis.py -menu'\n")
        exit(0)    

    inbound_data = sur.get_inbound_info(DB_FILE, MY_REMARK)

    if not inbound_data:
        print(f"[Fatal] Could not find inbound '{MY_REMARK}'. Exiting.")
        exit(1)

    if inbound_data:
        inbound_id, current_port, proxy_settings, current_network_settings = inbound_data
        
        link = sur.generate_vless_link(current_port, proxy_settings, current_network_settings, MY_REMARK)

        print("\n[SUCCESS] Using existing configuration without changes.")
        print(f"[System] Current port: {current_port}")
        print(f"[System] Current SNI: {current_network_settings.get('realitySettings', {}).get('serverNames', ['N/A'])[0]}")
        print(f"[System] Current ShortID: {current_network_settings.get('realitySettings', {}).get('shortIds', ['N/A'])[0]}")

        if link:
            SUB_PORT = 8080

            ensure_firewall_port(SUB_PORT)
            SubscriptionHandler.vless_link = link

            scheduler_thread = threading.Thread(
                target=rotation_worker,
                args=(sur, nav, DB_FILE, MY_REMARK),
                daemon=True
            )
            scheduler_thread.start()

            ip_cmd = subprocess.check_output(["curl", "-s", "ifconfig.me"]).decode().strip()
            sub_url = f"http://{ip_cmd}:{SUB_PORT}{SubscriptionHandler.secret_path}"

            print(f"\n--- Subscription Server Started ---")
            print(f"Using existing subscription data until next rotation")
            print(f"Subscription URL: {sub_url}")
            print(f"Status: Waiting for connections... (Ctrl+C to stop)\n")
            print(f"---------------------------------------\n")

            server = HTTPServer(('0.0.0.0', SUB_PORT), SubscriptionHandler)
            server.serve_forever()
