from web3 import Web3
import time
import concurrent.futures
import threading

w3 = Web3(Web3.HTTPProvider('xxxxxxx'))

if not w3.is_connected():
    print("无法连接到Holesky网络")
    exit()

sender_address = " xxxx  "
sender_private_key = " xxx "

TRANSFER_AMOUNT = 0.005
MAX_WORKERS = 10  # 同时处理的最大交易数
MAX_RETRIES = 3   # 最大重试次数

def read_receivers(filename):
    with open(filename, 'r') as file:
        receivers = [line.strip() for line in file if line.strip()]
    print(f"读取到 {len(receivers)} 个接收地址")
    return receivers

nonce_lock = threading.Lock()
nonce = w3.eth.get_transaction_count(sender_address)

def transfer_eth(to_address):
    global nonce
    amount_wei = w3.to_wei(TRANSFER_AMOUNT, 'ether')
    
    for attempt in range(MAX_RETRIES):
        try:
            if not w3.is_connected():
                print("无法连接到以太坊网络,正在重试...")
                time.sleep(5)
                continue

            with nonce_lock:
                current_nonce = nonce
                nonce += 1

            gas_price = int(w3.eth.gas_price * 1.1)

            tx = {
                'nonce': current_nonce,
                'to': to_address,
                'value': amount_wei,
                'gas': 21000,
                'gasPrice': gas_price,
                'chainId': 17000
            }

            print(f"准备发送交易:")
            print(f"  From: {sender_address}")
            print(f"  To: {to_address}")
            print(f"  Amount: {TRANSFER_AMOUNT} ETH")
            print(f"  Nonce: {current_nonce}")
            print(f"  Gas Price: {w3.from_wei(gas_price, 'gwei')} Gwei")

            signed_tx = w3.eth.account.sign_transaction(tx, sender_private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            
            tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
            print(f"已发送 {TRANSFER_AMOUNT} ETH 到 {to_address}")
            print(f"交易哈希: {tx_hash.hex()}")
            print(f"交易已被打包到区块: {tx_receipt['blockNumber']}")
            return  # 成功发送交易，退出函数

        except Exception as e:
            print(f"发送到 {to_address} 的交易失败 (尝试 {attempt+1}/{MAX_RETRIES}): {str(e)}")
            if attempt < MAX_RETRIES - 1:
                print("等待5秒后重试...")
                time.sleep(5)
            else:
                print(f"发送到 {to_address} 的交易在 {MAX_RETRIES} 次尝试后仍然失败")

def main():
    sender_balance = w3.eth.get_balance(sender_address)
    print(f"发送地址余额: {w3.from_wei(sender_balance, 'ether')} ETH")

    receivers = read_receivers('address.txt')
    total_amount_needed = w3.to_wei(TRANSFER_AMOUNT, 'ether') * len(receivers)
    print(f"总共需要发送: {w3.from_wei(total_amount_needed, 'ether')} ETH")

    if sender_balance < total_amount_needed:
        print("发送地址余额不足,无法完成所有交易")
        return

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [executor.submit(transfer_eth, receiver) for receiver in receivers]
        
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()  # 获取结果，但不做任何处理
            except Exception as e:
                print(f"处理交易时发生异常: {str(e)}")

    print("所有转账操作已完成。")

if __name__ == "__main__":
    main()
