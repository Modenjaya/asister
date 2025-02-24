import os
import json
import logging
from datetime import datetime

# Konfigurasi path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
DATA_DIR = os.path.join(BASE_DIR, "data")

# Buat direktori jika belum ada
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(DATA_DIR, exist_ok=True)

# Konfigurasi logging
def setup_logging():
    log_file = os.path.join(LOGS_DIR, "claim_bot.log")
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("AssisterrBot")

# Fungsi untuk membaca akun dari file accounts.json
def load_accounts():
    accounts_file = os.path.join(BASE_DIR, "accounts.json")
    try:
        if os.path.exists(accounts_file):
            with open(accounts_file, "r") as f:
                return json.load(f)
        else:
            # Buat file contoh jika belum ada
            sample_accounts = [
                {
                    "name": "Account 1",
                    "access_token": "your_token_here",
                    "enabled": True
                }
            ]
            with open(accounts_file, "w") as f:
                json.dump(sample_accounts, f, indent=4)
            return []
    except Exception as e:
        print(f"Error loading accounts: {e}")
        return []

# Fungsi untuk menyimpan riwayat klaim
def save_claim_history(account_name, status, message=""):
    history_file = os.path.join(DATA_DIR, "claim_history.json")
    history = []
    
    # Baca history yang sudah ada
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except json.JSONDecodeError:
            history = []
    
    # Tambahkan entry baru
    entry = {
        "account": account_name,
        "date": datetime.now().strftime("%Y-%m-%d"),
        "time": datetime.now().strftime("%H:%M:%S"),
        "status": status,
        "message": message
    }
    
    history.append(entry)
    
    # Simpan kembali
    with open(history_file, "w") as f:
        json.dump(history, f, indent=4)

# URL dan endpoints
ASSISTERR_BASE_URL = "https://build.assisterr.ai"
ASSISTERR_DASHBOARD_URL = f"{ASSISTERR_BASE_URL}/dashboard"
ASSISTERR_API_CLAIM_URL = f"{ASSISTERR_BASE_URL}/api/rewards/claim-daily"

# Default Chrome options
def get_chrome_options(headless=False):
    from selenium.webdriver.chrome.options import Options
    
    options = Options()
    if headless:
        options.add_argument("--headless")
    
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    
    return options
