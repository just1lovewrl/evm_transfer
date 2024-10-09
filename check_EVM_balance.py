import threading
from web3 import Web3
from eth_account import Account
import time

# 连接到 TWVM 网络
w3 = Web3(Web3.HTTPProvider('xxxxx'))

# 输入和输出文件
INPUT_FILE = 'prvite_key.txt'
OUTPUT_FILE = 'holders.txt'

# 线程锁
file_lock = threading.Lock()

# 用于存储有余额的私钥
valid_private_keys = set()

def check_balance(private_key):
    try:
        account = Account.from_key(private_key)
        address = account.address
        balance = w3.eth.get_balance(address)
        if balance > 0:
            with file_lock:
                valid_private_keys.add(private_key.strip())
            print(f'Address {address} has TWVM balance: {w3.from_wei(balance, "ether")} TWVM')
    except Exception as e:
        print(f'Error processing private key: {e}')

def process_keys(keys):
    for key in keys:
        check_balance(key.strip())

# 读取私钥
with open(INPUT_FILE, 'r') as f:
    private_keys = f.readlines()

# 创建线程
num_threads = 10  # 可以根据需要调整线程数
keys_per_thread = len(private_keys) // num_threads
threads = []

for i in range(num_threads):
    start = i * keys_per_thread
    end = start + keys_per_thread if i < num_threads - 1 else len(private_keys)
    thread = threading.Thread(target=process_keys, args=(private_keys[start:end],))
    threads.append(thread)
    thread.start()

# 等待所有线程完成
for thread in threads:
    thread.join()
用
# 将去重后的私钥写入文件
with open(OUTPUT_FILE, 'w') as f:
    for key in valid_private_keys:
        f.write(f'{key}\n')

print(f'处理完成，去重后的结果已保存到 {OUTPUT_FILE}')
print(f'共找到 {len(valid_private_keys)} 个有效私钥')

