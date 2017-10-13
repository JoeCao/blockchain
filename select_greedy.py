# coding=utf=8
# 使用贪心算法，在UTXO中找到符合支付要求的
from sys import argv


class OutputInfo(object):
    def __init__(self, tx_hash, tx_index, value):
        self.tx_hash = tx_hash
        self.tx_index = tx_index
        self.value = value

    def __repr__(self):
        return '{0}:{1}:with {2} satoshis'.format(self.tx_hash, self.tx_index, self.value)


def select_output_greedy(unspent, min_value):
    if not unspent:
        return None
    lessers = [utxo for utxo in unspent if utxo.value < min_value]
    greater = [utxo for utxo in unspent if utxo.value > min_value]
    if greater:
        min_greater = min(greater)
        change = min_greater.value - min_value
        return [min_greater], change
    # 将小于需要支付的费用的utxo按照从小到大排序
    lessers.sort(key=(lambda utxo: utxo.value), reverse=True)
    sum = 0
    result = []
    for utxo in lessers:
        result.append(utxo)
        sum = sum + utxo.value
        if sum > min_value:
            change = sum - min_value
            return result, 'change {0} satoshis'.format(change)
    return None, 0


if __name__ == '__main__':
    unspent = [
        OutputInfo("faa92f1fd29e2fe296eda702c48bd11ffd52313e986e99ddad9084062167", 1, 8000000),
        OutputInfo("6596fd070679de96e405d52b51b8e1d644029108ec4cbfe451454486796a1ecf", 0, 16050000),
        OutputInfo("b2affea89ff82557c60d635a2a3137b8f88f12ecec85082f7d0a1f82ee203ac4", 0, 10000000),
        OutputInfo("7dbc497969c7475e45d952c4a872e213fb15d45e5cd3473c386a71a1b0c136a1", 0, 25000000),
        OutputInfo("55ea01bd7e9afd3d3ab9790199e777d62a0709cf0725e80a7350fdb22d7b8ec6", 17, 5470541),
        OutputInfo("12b6a7934c1df821945ee9ee3b3326d07ca7a65fd6416ea44ce8c3db0c078c64", 0, 10000000),
        OutputInfo("7f42eda67921ee92eae5f79bd37c68c9cb859b899ce70dba68c48338857b7818", 0, 16100000), ]
    if len(argv) > 1:
        target = long(argv[1])
    else:
        target = 55000000

    print "For transaction amount %d Satoshis (%f bitcoin) use: " % (target, target / 10.0 ** 8)
    print select_output_greedy(unspent, target)

