# coding=utf-8
import hashlib

import jsonpickle

from merkle import merkle

ZERO = reduce(lambda x, y: x + '0', [str(i) for i in range(0, 32)])


class TxIn(object):
    def __init__(self, previous_hash, previous_index, script=b'', sequence=4294967295, ):
        '''
        初始化一笔交易输入
        :param previous_hash: 上一个UTXO的hash值，Coinbase就是32个0
        :param previous_index: 上个UTXO的index
        :param script: 用于解锁的脚本，这里简化为用户的账本Address
        :param sequence: 交易版本
        '''
        self.previous_hash = previous_hash
        self.previous_index = previous_index
        self.script = script
        self.sequence = sequence

    @classmethod
    def coinbase_tx_in(class_, script):
        tx = class_(previous_hash=ZERO, previous_index=4294967295, script=script)
        return tx


class TxOut(object):
    def __init__(self, address, value):
        '''
        生成一笔交易输出
        :param address: 给谁转钱了 
        :param value: 转了多少钱
        '''
        self.address = address
        self.value = value


class Transaction(object):
    TxIn = TxIn
    TxOut = TxOut

    def __init__(self, txs_in, txs_out, coin_base=False, version=1, lock_time=0):
        self.version = version
        self.lock_time = lock_time
        self.txs_in = txs_in
        self.txs_out = txs_out

    @classmethod
    def coinbase_tx(cls, address, coin_value):
        tx_in = cls.TxIn.coinbase_tx_in('')
        tx_out = cls.TxOut(address, coin_value)
        return cls([tx_in], [tx_out], True)

    def hash(self):
        return hashlib.sha256(hashlib.sha256(self.to_json()).digest()).hexdigest()

    def to_json(self):
        return jsonpickle.encode(self)

    def from_json(self, json_string):
        return jsonpickle.decode(json_string)


if __name__ == '__main__':
    tx = Transaction.coinbase_tx("11111", 50)
    print tx.to_json()
    print tx.hash()
    obj = tx.from_json(tx.to_json())
    print obj.hash()
    in1 = TxIn(tx.hash(), 0)
    out1 = TxOut("2222", 49)
    out2 = TxOut("3333", 1)
    txnew = Transaction([in1], [out1, out2])
    print txnew.to_json()
    print txnew.hash()
    print merkle([tx.hash(), txnew.hash(), obj.hash()])
