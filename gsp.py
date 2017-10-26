#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
===============================================
GSP (Generalized Sequential Pattern) algorithm
===============================================

GSP algorithm made with Python3 to deal with arrays as transactions.

Example:

transactions = [
				['Bread', 'Milk'],
				['Bread', 'Diaper', 'Beer', 'Eggs'],
				['Milk', 'Diaper', 'Beer', 'Coke'],
				['Bread', 'Milk', 'Diaper', 'Beer'],
				['Bread', 'Milk', 'Diaper', 'Coke']
			]
"""
# print(__doc__)

import logging
import numpy as np

from itertools import combinations

__author__ = "Jackson Antonio do Prado Lima"
__email__ = "jacksonpradolima@gmail.com"
__license__ = "GPL"
__version__ = "1.0"

class GSP:
	def __init__(self, raw_transactions):
		self._pre_processing(raw_transactions)

	def _pre_processing(self, raw_transactions):
		'''
		Prepare the data
		'''
		# each item is parsed to a set type
		self.transactions = [set(np.array(i)) for i in raw_transactions]

		# different items in the base
		self.unique_candidates = set(x for l in self.transactions for x in l)

	def _frequency(self, items):
		'''
		Frequency of occurrence of a set of items in the base

		Parameters
			items: set of items that will be evaluated
		'''

		results = {}
		for item in items:
			freq = 0
			aux = set([item]) if type(item) != set else item
			for t in self.transactions:
				if aux.issubset(t):
					freq += 1
			results[tuple(aux)] = freq
		return results

	def _support(self, items, minsup = 0):
		'''
		The support is the probability that the antecedent of the rule is present in the base (transactions) in relation to the total amount of records in the base.
		'''

		results = {}
		t_size = len(self.unique_candidates)

		for key, freq in items.items():
			# ratio between the number of times the item appears in the base by the total of different items in the base
			qnt = freq / t_size
			if qnt > minsup:
				results[key] = qnt
		return results

	def _print_status(self, run, candidates_size, new_freq_patterns_size):
		logging.debug("Run {}\nThere are {} candidates.\nThe candidates have been filtered down to {}.\n".format(run, candidates_size, new_freq_patterns_size))

	def search(self, minsup = 0.2):
		'''
		Run GSP mining algorithm 

		Parameters
			minsup: minimum support
		'''
		assert (0.0 < minsup) and (minsup <= 1.0)

		# initial candidates: all singleton sequences (k-itemsets/k-sequence = 1) - Initially, every item in DB is a candidate
		candidates = self.unique_candidates

		# scan transactions to collect support count for each candidate sequence & filter
		freq_patterns = new_freq_patterns = self._support(self._frequency(candidates), minsup)

		# (k-itemsets/k-sequence = 1)
		k_items = 1

		self._print_status(k_items, len(candidates), len(new_freq_patterns))

		# repeat until no frequent sequence or no candidate can be found
		while True:
			# is there anything left?
			if new_freq_patterns:
				freq_patterns = new_freq_patterns
				k_items += 1
			else:
				return freq_patterns

			# if any left, generate new candidates from the "best" supports
			candidates = [set(c) for c in combinations(set(x for l in new_freq_patterns.keys() for x in l), k_items)]

			# candidate pruning - eliminates candidates who are not potentially frequent (using support as threshold)
			new_freq_patterns = self._support(self._frequency(candidates), minsup)

			self._print_status(k_items, len(candidates), len(new_freq_patterns))
