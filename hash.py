# coding=utf-8
import hashlib
import sys

from bitstring import BitArray


def custom_range(start=0, stop=None, step=1):
    '''xrange in python 2.7 fails on numbers larger than C longs.
    we write a custom version'''
    if stop is None:
        # handle single argument case. ugly...
        stop = start
        start = 0
    i = start
    while i < stop:
        yield i
        i += step


xrange = custom_range

# 模拟的区块字符

block_sample = {
    "header": {
        "difficult_factor": 4,
        "last_block": "0000000000000000000000000000000000000000000000000000000000000000",
        "merkle_tree": "01181212a283e760929f6b1628d903127c65e6fb5a9ad7fe94b790e699269221",
        "nonce": 90447,
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


def mine(binary_stream, difficult_factor):
    assert binary_stream.length == 608
    # print('start hash256')
    for nonce in xrange(0, sys.maxint):
        # print('try nonce:' + str(nonce))
        # 将随机数加到末位的4个byte中
        temp = binary_stream.copy()
        temp.append('uint:32=' + str(nonce))
        # print temp.hex
        digest = hashlib.sha256(hashlib.sha256(temp.tobytes()).digest()).hexdigest()
        # print digest
        if validate_proof(difficult_factor, digest):
            return nonce, digest
    return -1, ''


def validate_proof(difficult_factor, digest):
    start_zero = reduce(lambda x, y: x + '0', [str(i) for i in range(0, difficult_factor)])
    if digest and digest.startswith(start_zero):
        return True
    else:
        return False


def pack_block(block_header):
    binary_stream = BitArray()
    # 加入版本号
    binary_stream.append(block_header['version'])
    # 加入上一个区块号的hash值
    binary_stream.append(bytearray.fromhex(block_header['last_block']))
    # 所有交易构成的默克尔树的hash值
    binary_stream.append(bytearray.fromhex(block_header['merkle_tree']))
    # 时间戳
    binary_stream.append('uint:32=' + str(long(block_header['timestamp'])))
    # 难度因子，这里默认为5
    binary_stream.append('uint:32=' + str(block_header['difficult_factor']))
    return binary_stream


def block_hash(block):
    block_header = block['header']
    stream = pack_block(block_header)
    assert stream.length == 608
    stream.append('uint:32=' + str(block_header['nonce']))
    assert stream.length == 640
    digest = hashlib.sha256(hashlib.sha256(stream.tobytes()).digest()).hexdigest()
    return digest


if __name__ == '__main__':
    print mine(pack_block(block_sample['header']), block_sample['header']['difficult_factor'])

    print block_hash(block_sample)
    # print bytearray.fromhex('10')
    # print('---- create byte arrays of block ----')
    # block_header = pack_block(block_sample['header'])
    # print(block_header.length)
    # start = time.time()
    # print cal_block_hash(block_header)
    # elapsed = str(time.time() - start)
    # print('耗时{0}秒'.format(elapsed))
