import sqlite3
from datetime import datetime
from web3 import Web3

DATABASE_NAME = 'airdrop.db'

# Polygon RPC URL
POLYGON_RPC_URL = 'https://polygon-mainnet.infura.io'
w3 = Web3(Web3.HTTPProvider(POLYGON_RPC_URL))

def get_connection():
    conn = sqlite3.connect(DATABASE_NAME)
    return conn

def add_user(user_id, username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT OR IGNORE INTO users (user_id, username, last_claim) VALUES (?, ?, ?)', 
                   (user_id, username, datetime.now().isoformat()))
    conn.commit()
    conn.close()

def get_balance(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else 0

def update_balance(user_id, amount):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ? WHERE user_id = ?', (amount, user_id))
    conn.commit()
    conn.close()

def set_withdrawal_address(user_id, address):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET withdrawal_address = ? WHERE user_id = ?', (address, user_id))
    conn.commit()
    conn.close()

def get_withdrawal_address(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT withdrawal_address FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def add_referral(referrer_id, referred_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO referrals (referrer_id, referred_id) VALUES (?, ?)', (referrer_id, referred_id))
    conn.commit()
    conn.close()

def is_referred(referrer_id, referred_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM referrals WHERE referrer_id = ? AND referred_id = ?', (referrer_id, referred_id))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def claim_daily_bonus(user_id):
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().date().isoformat()
    cursor.execute('SELECT last_claim FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    last_claim = result[0] if result else None
    if last_claim and last_claim[:10] == today:
        conn.close()
        return False  # Already claimed today
    cursor.execute('UPDATE users SET last_claim = ? WHERE user_id = ?', (today, user_id))
    update_balance(user_id, 10)  # Add 10 tokens as a daily bonus
    conn.commit()
    conn.close()
    return True

def withdraw(user_id, amount):
    MIN_WITHDRAWAL_AMOUNT = 10000  # Minimum withdrawal amount in tokens
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT balance, withdrawal_address FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    if result:
        balance, address = result
        if amount >= MIN_WITHDRAWAL_AMOUNT and balance >= amount:
            # Assume you have a function to send tokens
            from_address = '0x4EF6008Eb8083Cc416cc7817BA5f046BD9b27bdE'  # The wallet address that holds the tokens
            private_key = '8d75890fc01116c974a7b23fbb128c1e6ed16425e22ee4faacfd8779220a4070'  # Private key for signing the transaction
            
            txn_hash = send_tokens(from_address, private_key, address, amount)
            if txn_hash:
                update_balance(user_id, -amount)
                conn.commit()
                conn.close()
                return f"Tokens sent to {address}. Transaction hash: {txn_hash}"
            else:
                conn.close()
                return "Failed to send tokens."
        elif amount < MIN_WITHDRAWAL_AMOUNT:
            conn.close()
            return "Amount below minimum withdrawal limit."
    conn.close()
    return None

def send_tokens(from_address, private_key, to_address, amount):
    # Token contract ABI and address
    TOKEN_CONTRACT_ABI = '[{"inputs":[{"internalType":"string","name":"name","type":"string"},{"internalType":"string","name":"symbol","type":"string"},{"internalType":"uint8","name":"decimals","type":"uint8"},{"internalType":"uint256","name":"supply","type":"uint256"},{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"feeWallet","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"owner","type":"address"},{"indexed":true,"internalType":"address","name":"spender","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Approval","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":true,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":false,"inputs":[{"indexed":false,"internalType":"address","name":"owner","type":"address"}],"name":"TeamFinanceTokenMint","type":"event"},{"anonymous":false,"inputs":[{"indexed":true,"internalType":"address","name":"from","type":"address"},{"indexed":true,"internalType":"address","name":"to","type":"address"},{"indexed":false,"internalType":"uint256","name":"value","type":"uint256"}],"name":"Transfer","type":"event"},{"inputs":[{"internalType":"address","name":"owner","type":"address"},{"internalType":"address","name":"spender","type":"address"}],"name":"allowance","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"approve","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"decimals","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"subtractedValue","type":"uint256"}],"name":"decreaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"spender","type":"address"},{"internalType":"uint256","name":"addedValue","type":"uint256"}],"name":"increaseAllowance","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"to","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"mint","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"name","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"symbol","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"totalSupply","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transfer","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"sender","type":"address"},{"internalType":"address","name":"recipient","type":"address"},{"internalType":"uint256","name":"amount","type":"uint256"}],"name":"transferFrom","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"}]'  # Replace with your token's ABI
    TOKEN_CONTRACT_ADDRESS = Web3.toChecksumAddress('0xe2b9288e91c7FD71641369cBA747B40B6184C406')

    # Create a contract instance
    contract = w3.eth.contract(address=TOKEN_CONTRACT_ADDRESS, abi=TOKEN_CONTRACT_ABI)

    nonce = w3.eth.getTransactionCount(from_address)
    txn = contract.functions.transfer(to_address, amount).buildTransaction({
        'chainId': 137,  # Polygon Mainnet chain ID, 
        'gas': 2000000,
        'gasPrice': w3.toWei('30', 'gwei'),
        'nonce': nonce
    })

    signed_txn = w3.eth.account.sign_transaction(txn, private_key=private_key)
    txn_hash = w3.eth.sendRawTransaction(signed_txn.rawTransaction)
    return w3.toHex(txn_hash)

def create_task(owner_id, title, description, reward):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tasks (owner_id, title, description, reward) VALUES (?, ?, ?, ?)', 
                   (owner_id, title, description, reward))
    conn.commit()
    conn.close()

def list_tasks(owner_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT id, title, description, reward FROM tasks WHERE owner_id = ?', (owner_id,))
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def get_task_by_id(task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT title, description, reward FROM tasks WHERE id = ?', (task_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def mark_task_complete(user_id, task_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT reward FROM tasks WHERE id = ?', (task_id,))
    result = cursor.fetchone()
    if result:
        reward = result[0]
        update_balance(user_id, reward)
        cursor.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
        conn.commit()
    conn.close()

def initialize_tasks_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            reward REAL NOT NULL
        )
    ''')
    conn.commit()
    conn.close()
