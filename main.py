import argparse
import logging
import random

from gsp import GSP

logging.basicConfig(level=logging.DEBUG)


def create_transactions(minsize, maxsize, minvalue, maxvalue):
    return [random.randint(minvalue, maxvalue)
            for _ in range(random.randint(minsize, maxsize))]

minsize, maxsize, minvalue, maxvalue = 2, 256, 0, 5

transactions = [create_transactions(
    minsize, maxsize, minvalue, maxvalue) for _ in range(10000)]

# transactions = [
#     ['Bread', 'Milk'],for _ in procs:
#     ['Bread', 'Diaper', 'Beer', 'Eggs'],
#     ['Milk', 'Diaper', 'Beer', 'Coke'],
#     ['Bread', 'Milk', 'Diaper', 'Beer'],
#     ['Bread', 'Milk', 'Diaper', 'Coke']
# ]

# transactions = [[3, 5, 2, 0, 4, 4, 1, 1], [2, 5, 5], [5, 3, 2, 4, 4, 0, 4], [4, 3, 0, 0], [
#     1, 0, 4, 0, 0, 4], [2, 5, 1, 3, 5, 2, 5, 3], [0, 4, 0, 4, 5], [4, 2],
#     [5], [2, 3, 0, 0, 0, 3, 0, 2, 3]]

result = GSP(transactions).search(0.3)

print("========= Status =========")
print("Transactions: {}".format(transactions))
print("GSP: {}".format(result))
