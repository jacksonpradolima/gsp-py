import logging
import random
from unittest import TestCase

from gsppy.gsp import GSP

logging.basicConfig(level=logging.DEBUG)


class TestGSP(TestCase):
    @staticmethod
    def create_transactions(minsize, maxsize, minvalue, maxvalue):
        return [random.randint(minvalue, maxvalue)
                for _ in range(random.randint(minsize, maxsize))]

    def test_artificial_transactions(self):
        minsize, maxsize, minvalue, maxvalue = 2, 256, 0, 5

        transactions = [TestGSP.create_transactions(
            minsize, maxsize, minvalue, maxvalue) for _ in range(10)]

        result = GSP(transactions).search(0.3)

        # print("========= Status =========")
        # print("Transactions: {}".format(transactions))
        print("GSP: {}".format(result))

    def test_supermarket(self):
        transactions = [
            ['Bread', 'Milk'],
            ['Bread', 'Diaper', 'Beer', 'Eggs'],
            ['Milk', 'Diaper', 'Beer', 'Coke'],
            ['Bread', 'Milk', 'Diaper', 'Beer'],
            ['Bread', 'Milk', 'Diaper', 'Coke']
        ]

        result = GSP(transactions).search(0.3)
        final = [{('Bread',): 4, ('Diaper',): 4, ('Milk',): 4, ('Beer',): 3, ('Coke',): 2},
                 {('Bread', 'Milk'): 3, ('Diaper', 'Beer'): 3, ('Milk', 'Diaper'): 3},
                 {('Bread', 'Milk', 'Diaper'): 2, ('Milk', 'Diaper', 'Beer'): 2}]
        # print("========= Status =========")
        # print("Transactions: {}".format(transactions))
        # print("GSP: {}".format(result))

        self.assertEquals(result, final)
