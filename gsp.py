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

import logging
import numpy as np

from itertools import combinations

__author__ = "Jackson Antonio do Prado Lima"
__email__ = "jacksonpradolima@gmail.com"
__license__ = "GPL"
__version__ = "1.0"

class GSP:
	def __init__(self, raw_transactions):
		self.freq_patterns = []
		self._pre_processing(raw_transactions)

	def _pre_processing(self, raw_transactions):
		'''
		Prepare the data

		Parameters:
			raw_transactions: the data that it will be analysed
		'''
		# each item is parsed to a set type
		self.transactions = [set(np.array(i)) for i in raw_transactions]

		# different items in the base
		self.unique_candidates = [set([item]) for item in set(x for l in self.transactions for x in l)]

		# the total of different items in the base
		self.t_size = len(self.unique_candidates)

	def _support(self, items, minsup = 0):
		'''
		The support is the probability that the antecedent of the rule is present in the base (transactions) in relation to the total amount of records in the base.

		Parameters
			items: set of items that will be evaluated
			minsup: minimum support
		'''
		results = {}
		for item in items:
			# The number of times the item appears in the base
			frequency = len([t for t in self.transactions if item.issubset(t)])

			# ratio between the frequency and the total of different items in the base
			support = round(frequency / self.t_size, 3)

			if support >= minsup:
				results[tuple(item)] = [frequency, support]
		return results

	def _print_status(self, run, candidates):
		logging.debug("Run {}\nThere are {} candidates.\nThe candidates have been filtered down to {}.\n".format(run, len(candidates), len(self.freq_patterns[run-1])))

	def search(self, minsup = 0.2):
		'''
		Run GSP mining algorithm 

		Parameters
			minsup: minimum support
		'''
		assert (0.0 < minsup) and (minsup <= 1.0)

		# the set of frequent 1-sequence: all singleton sequences (k-itemsets/k-sequence = 1) - Initially, every item in DB is a candidate
		candidates = self.unique_candidates

		# scan transactions to collect support count for each candidate sequence & filter
		self.freq_patterns.append(self._support(candidates, minsup))

		# (k-itemsets/k-sequence = 1)
		k_items = 1

		self._print_status(k_items, candidates)

		# repeat until no frequent sequence or no candidate can be found
		while len(self.freq_patterns[k_items - 1]):
			k_items += 1

			# Generate candidate sets Ck (set of candidate k-sequences) - generate new candidates from the last "best" candidates filtered by minimum support
			candidates = [set(c) for c in combinations(set(x for l in self.freq_patterns[k_items - 2].keys() for x in l), k_items)]

			# candidate pruning - eliminates candidates who are not potentially frequent (using support as threshold)
			self.freq_patterns.append(self._support(candidates, minsup))

			self._print_status(k_items, candidates)
		return self.freq_patterns