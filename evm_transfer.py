from web3 import Web3
import time
import random
import threading

# 初始化 Web3
w3 = Web3(Web3.HTTPProvider('https://rpc.mantle.xyz'))

# 账户地址列表
account_addresses = [
    '',
    ''
    ]

# 私钥列表，与账户地址对应
private_keys = [
    '',
    '',
]

# 转账函数
def make_transfer(account_address, private_key):
    for _ in range(10000):  # 替换为您希望执行的转账次数
        raw_input = "0x646174613a2c7b2270223a226d72632d3230222c226f70223a226d696e74222c227469636b223a22626f726e222c22616d74223a2231303030227d"
        decoded_data = bytes.fromhex(raw_input[2:])
        nonce = w3.eth.get_transaction_count(account_address)

        tx = {
            'from': account_address,
            'to': account_address,
            'value': 0,
            'data': decoded_data,
            'gas': 50000,
            'nonce': nonce,
            'gasPrice': w3.to_wei('0.05', 'gwei')
        }

        # 签署并发送交易
        signed_tx = w3.eth.account.sign_transaction(tx, private_key)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        print(f"交易哈希: {tx_hash.hex()}")

        # 随机等待3到15秒
        time.sleep(random.randint(3, 15))

# 创建和启动线程
threads = []
for i in range(len(account_addresses)):
    thread = threading.Thread(target=make_transfer, args=(account_addresses[i], private_keys[i]))
    threads.append(thread)
    thread.start()

# 等待所有线程完成
for thread in threads:
    thread.join()
