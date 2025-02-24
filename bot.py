import time
import requests
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

import config

class AssisterrBot:
    def __init__(self, account_name, access_token, headless=False):
        self.account_name = account_name
        self.access_token = access_token
        self.logger = config.setup_logging()
        self.chrome_options = config.get_chrome_options(headless)
        self.driver = None
        
    def setup_driver(self):
        """Initialize webdriver with options"""
        try:
            self.driver = webdriver.Chrome(options=self.chrome_options)
            self.driver.maximize_window()
            self.logger.info(f"[{self.account_name}] WebDriver initialized successfully")
            return True
        except Exception as e:
            self.logger.error(f"[{self.account_name}] Failed to initialize WebDriver: {e}")
            return False
    
    def login_with_token(self):
        """Login to Assisterr.ai using access token"""
        try:
            self.logger.info(f"[{self.account_name}] Attempting to login with access token")
            
            # Buka halaman utama
            self.driver.get(config.ASSISTERR_BASE_URL)
            
            # Tambahkan token ke local storage untuk autentikasi
            self.driver.execute_script(f"localStorage.setItem('accessToken', '{self.access_token}');")
            
            # Navigate ke dashboard
            self.driver.get(config.ASSISTERR_DASHBOARD_URL)
            
            # Tunggu sampai halaman dashboard muncul
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.XPATH, "//div[contains(@class, 'dashboard') or contains(@class, 'home')]"))
            )
            
            self.logger.info(f"[{self.account_name}] Login successful!")
            return True
            
        except TimeoutException:
            self.logger.error(f"[{self.account_name}] Timeout occurred while waiting for dashboard elements")
            return False
        except Exception as e:
            self.logger.error(f"[{self.account_name}] Login failed: {e}")
            return False
    
    def claim_via_api(self):
        """Claim reward melalui API request langsung"""
        try:
            self.logger.info(f"[{self.account_name}] Attempting to claim reward via API")
            
            headers = {
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.post(
                config.ASSISTERR_API_CLAIM_URL, 
                headers=headers
            )
            
            if response.status_code == 200:
                self.logger.info(f"[{self.account_name}] Daily reward claimed successfully via API!")
                return True, "Claimed via API"
            else:
                self.logger.error(f"[{self.account_name}] API claim failed: {response.status_code} - {response.text}")
                return False, f"API Error: {response.status_code}"
                
        except Exception as e:
            self.logger.error(f"[{self.account_name}] Failed to claim via API: {e}")
            return False, f"API Exception: {str(e)}"
    
    def claim_daily_reward(self):
        """Claim daily reward dari dashboard menggunakan browser"""
        try:
            self.logger.info(f"[{self.account_name}] Attempting to claim daily reward via browser")
            
            # Tunggu tombol claim muncul
            WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, "//button[contains(text(), 'Claim') or contains(@class, 'claim-button')]"))
            )
            
            # Cari dan klik tombol claim
            claim_button = self.driver.find_element(By.XPATH, "//button[contains(text(), 'Claim') or contains(@class, 'claim-button')]")
            
            # Periksa apakah tombol dapat diklik
            if claim_button.is_enabled():
                claim_button.click()
                self.logger.info(f"[{self.account_name}] Claim button clicked")
                
                # Tunggu konfirmasi claim berhasil
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//div[contains(text(), 'Success') or contains(text(), 'Claimed')]"))
                )
                
                self.logger.info(f"[{self.account_name}] Daily reward claimed successfully via browser!")
                return True, "Claimed via browser"
            else:
                message = "Claim button found but disabled. Already claimed today?"
                self.logger.warning(f"[{self.account_name}] {message}")
                return False, message
                
        except TimeoutException:
            message = "No claim button found or already claimed today"
            self.logger.warning(f"[{self.account_name}] {message}")
            return False, message
        except NoSuchElementException:
            message = "Claim button not found on page"
            self.logger.warning(f"[{self.account_name}] {message}")
            return False, message
        except Exception as e:
            message = f"Failed to claim: {str(e)}"
            self.logger.error(f"[{self.account_name}] {message}")
            return False, message
    
    def run(self):
        """Run the claim process for this account"""
        self.logger.info(f"[{self.account_name}] Starting claim process")
        result_message = ""
        
        try:
            # Coba metode API terlebih dahulu (lebih efisien)
            api_success, api_message = self.claim_via_api()
            
            if api_success:
                config.save_claim_history(self.account_name, True, api_message)
                return True, api_message
                
            # Jika API gagal, gunakan metode browser automation
            self.logger.info(f"[{self.account_name}] API claim failed, trying browser automation")
            
            if not self.setup_driver():
                message = "Failed to setup WebDriver"
                config.save_claim_history(self.account_name, False, message)
                return False, message
            
            if not self.login_with_token():
                message = "Failed to login with token"
                config.save_claim_history(self.account_name, False, message)
                return False, message
            
            browser_success, browser_message = self.claim_daily_reward()
            config.save_claim_history(self.account_name, browser_success, browser_message)
            return browser_success, browser_message
                
        except Exception as e:
            message = f"Unexpected error: {str(e)}"
            self.logger.error(f"[{self.account_name}] {message}")
            config.save_claim_history(self.account_name, False, message)
            return False, message
            
        finally:
            if self.driver:
                self.driver.quit()
                self.logger.info(f"[{self.account_name}] Browser session closed")
