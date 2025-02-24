import time
import random
from concurrent.futures import ThreadPoolExecutor
import config
from bot import AssisterrBot

def process_account(account):
    """Proses satu akun"""
    logger = config.setup_logging()
    
    if not account.get("enabled", True):
        logger.info(f"[{account['name']}] Account disabled, skipping")
        return f"Account '{account['name']}' skipped (disabled)"
    
    # Tambahkan jeda acak untuk mencegah deteksi bot
    delay = random.uniform(1, 5)
    time.sleep(delay)
    
    bot = AssisterrBot(
        account_name=account["name"],
        access_token=account["access_token"],
        headless=account.get("headless", False)
    )
    
    success, message = bot.run()
    
    if success:
        return f"✅ {account['name']}: {message}"
    else:
        return f"❌ {account['name']}: {message}"

def main():
    logger = config.setup_logging()
    logger.info("======== Starting Assisterr Auto Claim Bot (Multi-Account) ========")
    
    # Load accounts
    accounts = config.load_accounts()
    
    if not accounts:
        logger.error("No accounts found in accounts.json. Please add at least one account.")
        print("\nPlease edit the accounts.json file with your account information.")
        return
    
    logger.info(f"Found {len(accounts)} accounts to process")
    
    # Process all accounts in parallel (max 3 concurrent)
    results = []
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [executor.submit(process_account, account) for account in accounts]
        for future in futures:
            results.append(future.result())
    
    # Print results summary
    print("\nClaim Results:")
    for result in results:
        print(result)
    
    logger.info("======== Assisterr Auto Claim Bot Completed ========")

if __name__ == "__main__":
    main()
