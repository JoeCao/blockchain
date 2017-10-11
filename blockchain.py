# coding=utf-8
import json
from time import time, strptime, mktime
from urlparse import urlparse

import requests

from hash import pack_block, mine, block_hash, validate_proof

coinbase = '03443b0403858402062f503253482f'

first_block = {
    "header": {
        "difficult_factor": 4,
        "last_block": "0000000000000000000000000000000000000000000000000000000000000000",
        "merkle_tree": "01181212a283e760929f6b1628d903127c65e6fb5a9ad7fe94b790e699269221",
        "nonce": 49578,
        "timestamp": 1294840310.0,
        "version": "0x20000000"
    },
    "index": 1,
    "size": 380,
    "transactions": [
        {
            "amount": 50,
            "recipient": "19000",
            "sender": "03443b0403858402062f503253482f"
        }
    ]
}

block_sample = {
    # 除了size之外，整个block的字节数，这里简化的json dump的字符串长度
    "size": 351,
    # 区块高度，真实的比特币的区块并不包含该参数，而是实时计算的
    'index': 1,
    # 区块头信息
    'header': {
        # 版本号
        'version': '0x02000000',
        # 该区块产生的近似时间（精确到秒的Unix时间戳）
        'timestamp': 1506057125.900785,
        # 根据交易记录生成的默克尔树的root hash
        'merkle_tree': '01181212a283e760929f6b1628d903127c65e6fb5a9ad7fe94b790e699269221',
        # 上一个区块的hash
        'last_block': "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
        # 难度因子，该区块工作量证明算法的难度目标
        'difficult_factor': 4,
        # 用于工作量证明算法的计数器，区块头+nonce形成的串做两次hash256，得到的串满足难度因子的要求
        'nonce': 324984774000,
    },
    'transactions': [
        {
            # 铸币权coinbase交易
            'sender': '1',
            'recipient': '8527147fe1f5426f9dd545de4b27ee00',
            'amount': 50
        },
        {
            'sender': "8527147fe1f5426f9dd545de4b27ee00",
            'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",
            'amount': 5,
        },
        {
            'sender': "8527147fe1f5426f9dd545de4b27ee00",
            'recipient': "a77f5cdfa2934df3954a5c7c7da5df1f",
            'amount': 10,
        },
    ],

}

chain_sample = {
    "chain": [
        {
            "header": {
                "difficult_factor": 4,
                "last_block": "0000000000000000000000000000000000000000000000000000000000000001",
                "merkle_tree": "01181212a283e760929f6b1628d903127c65e6fb5a9ad7fe94b790e699269221",
                "nonce": 86870,
                "timestamp": 1,
                "version": "0x02000000"
            },
            "index": 1,
            "transactions": []
        },
        {
            "header": {
                "difficult_factor": 4,
                "last_block": "0000d2c34b87c6b6071c5368f9038ea06f26ee0b85a580a903562c5ba7725e89",
                "merkle_tree": "01181212a283e760929f6b1628d903127c65e6fb5a9ad7fe94b790e699269221",
                "nonce": 148416,
                "timestamp": 1507616157.488353,
                "version": "0x02000000"
            },
            "index": 2,
            "transactions": [
                {
                    "amount": 10,
                    "recipient": "a77f5cdfa2934df3954a5c7c7da5df1f",
                    "sender": "8527147fe1f5426f9dd545de4b27ee00"
                },
                {
                    "amount": 10,
                    "recipient": "a77f5cdfa2934df3954a5c7c7da5df1f",
                    "sender": "8527147fe1f5426f9dd545de4b27ee00"
                },
                {
                    "amount": 50,
                    "recipient": "ae73a6f9ec1544c0aade07a000d1b8cf",
                    "sender": "0"
                }
            ]
        },
        {
            "header": {
                "difficult_factor": 4,
                "last_block": "0000e54fca79fd8a25cce976c3193deafbbf8d05176c02c1d5c59c055649699b",
                "merkle_tree": "01181212a283e760929f6b1628d903127c65e6fb5a9ad7fe94b790e699269221",
                "nonce": 12017,
                "timestamp": 1507616322.160328,
                "version": "0x02000000"
            },
            "index": 3,
            "transactions": [
                {
                    "amount": 50,
                    "recipient": "ae73a6f9ec1544c0aade07a000d1b8cf",
                    "sender": "0"
                }
            ]
        },
        {
            "header": {
                "difficult_factor": 4,
                "last_block": "000036916c141b26fdce2078a5519d518524b6e8aa2e1e8d69d0ba11ca873848",
                "merkle_tree": "01181212a283e760929f6b1628d903127c65e6fb5a9ad7fe94b790e699269221",
                "nonce": 27475,
                "timestamp": 1507637797.316043,
                "version": "0x02000000"
            },
            "index": 4,
            "transactions": [
                {
                    "amount": 50,
                    "recipient": "ae73a6f9ec1544c0aade07a000d1b8cf",
                    "sender": "0"
                }
            ]
        }
    ],
    "length": 4
}


class Blockchain(object):
    def __init__(self, difficult_factor=4):
        self.chain = []
        self.current_transactions = []
        self.difficult_factor = difficult_factor
        self.nodes = set()

        # 添加创世纪块
        genesis_blockhash = reduce(lambda x, y: x + '0', [str(i) for i in range(0, 64)])
        genesis_timestamp = mktime(strptime('2011-01-12 21:51:50', '%Y-%m-%d %H:%M:%S'))
        # 第一笔coinbase交易
        self.new_transaction(coinbase, '19000', 50)
        self.new_block(previous_hash=genesis_blockhash, timestamp=genesis_timestamp)

    def new_block(self, previous_hash=None, timestamp=None):
        block = {
            'index': len(self.chain) + 1,
            'header': {
                'version': '0x02000000',
                'timestamp': timestamp or time(),
                # TODO 应该是根据交易记录生成默克尔树，待完善
                'merkle_tree': '01181212a283e760929f6b1628d903127c65e6fb5a9ad7fe94b790e699269221',
                # 如果不输入的话，就直接取上一个block的hash
                'last_block': previous_hash or block_hash(self.chain[-1]),
                'difficult_factor': self.difficult_factor
            },
            'transactions': self.current_transactions,

        }
        nonce, blockhash = self.mine(block)
        block['header']['nonce'] = nonce
        block['size'] = len(json.dumps(block))
        # 重置当前的交易池，以前的交易已经被打包了
        self.current_transactions = []
        self.chain.append(block)
        return block

    def coinbase_transaction(self, recipient):
        self.new_transaction(coinbase, recipient, 50, True)

    def new_transaction(self, sender, recipient, amount, is_coinbase=False):
        """
               为下一个block增加一笔交易
               :param sender: <str> 发起者的地址
               :param recipient: <str> 接受者的地址
               :param amount: <int> 费用
               :param is_coinbase: <boolean> 是否是铸币交易，默认是False
               :return: 无返回值
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'coinbase': is_coinbase
        })

    def register_node(self, address):
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url)

    def validate_chain(self, chain):
        # 从头开始验证区块链的有效性
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print "last_block is {0}, current_block is {1}".format(last_block, block)
            header = block['header']
            if header['last_block'] != block_hash(last_block):
                return False
            if not validate_proof(header['difficult_factor'], block_hash(last_block)):
                return False
            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self, response):
        '''
            比较所有节点的区块链长度，以最长且有效的区块链为最终结果，替换为最终结果
        :return: 
            如果有替换为True，如果无替换为False
        '''
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get('http://{0}/chain'.format(node))
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.validate_chain(chain):
                    max_length = length
                    new_chain = chain
        if new_chain:
            self.chain = new_chain
            return True
        else:
            return False

    @staticmethod
    def mine(block):
        bstream = pack_block(block['header'])
        return mine(bstream, block['header']['difficult_factor'])

    @property
    def last_block(self):
        return self.chain[-1]['header']['last_block']


if __name__ == '__main__':
    bc = Blockchain()
    bc.new_transaction('1', '8527147fe1f5426f9dd545de4b27ee00', 50)
    bc.new_block()
    bc.new_transaction('2', '3', 35)
    bc.new_transaction('3', '2', 11)
    bc.new_block()
    print bc.validate_chain(bc.chain)
    print bc.validate_chain(chain_sample['chain'])
