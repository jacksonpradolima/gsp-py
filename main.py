import argparse
import logging 

from gsp import GSP

logging.basicConfig(level=logging.DEBUG)

# Considers these transactions
items = [
			[1, 2],
			[1, 3, 4, 6],
			[2, 3, 4, 5],
			[1, 2, 3, 4],
			[1, 2, 3, 5]
		]

print(GSP(items).search(0.3))
