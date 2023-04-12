from geniusweb.issuevalue.Bid import Bid
from geniusweb.issuevalue.Domain import Domain
import numpy as np
from time import time
from geniusweb.progress.ProgressTime import ProgressTime
from geniusweb.progress.ProgressRounds import ProgressRounds

DECAY_EXP = 0.3

# agent creates an opponent model using frequency modeling
class OpponentModel:
    def __init__(self, domain: Domain, params=None):
        
        self._domain = domain # we do not use the offers, we just need the frequencies
        self._freqs = {} # stores frequencies of offers made by the opponent

        # controls effect of time in decay over time - can be modified to improve performance
        self._exp = params.get('decay_exp', DECAY_EXP) if params else DECAY_EXP
        self._decay = params.get('decay', True) if params else True

        for i in self._domain.getIssues():
            self._freqs[i] = {}

    def update(self, bid: Bid, progress):
        issues = self._domain.getIssues()
        for i in issues:
            val = bid.getValue(i)
            if val not in self._freqs[i]:
                self._freqs[i][val] = 0
            if self._decay:
                t = progress.get(time() * 1000)
                inc = 1 * ((1 - t) ** self._exp)
                self._freqs[i][val] += inc
            else:
                self._freqs[i][val] + 1
    def predict_utility(self, bid: Bid):
        max_frequencies = {}
        # get utility weights for each issue, with highest-frequency of most common bid values
        for i in self._domain.getIssues():
            max_frequencies[i] = 0
            # check for max
            for val in self._freqs[i]:
                if max_frequencies[i] < self._freqs[i][val]:
                    max_frequencies[i] = self._freqs[i][val]

        highest_freq = -np.inf
        for i in self._domain.getIssues():
            if max_frequencies[i] > highest_freq:
                highest_freq = max_frequencies[i]

        util_weights = {}
        # normalize weights
        for i in self._domain.getIssues():
            # avoid div by 0
            if highest_freq == 0:
                util_weights[i] = 0
            else:
                util_weights[i] = max_frequencies[i] / highest_freq

        # frequency normalization and multiply with weights:
        normalised_freqs = []
        for i in self._domain.getIssues():
            val = bid.getValue(i)
            if val in self._freqs[i]:
                normalised_freqs.append((self._freqs[i][val] / max_frequencies[i]) * util_weights[i])

        utility_pred = np.sum(normalised_freqs) / len(self._domain.getIssues())
        return utility_pred
