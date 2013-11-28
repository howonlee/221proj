from __future__ import division
from math import log
from copy import deepcopy
import numpy as np

class HMM:
    def __init__(self, nStates, nObs):
        """nStates is number of hidden states, nObs is number of possible observed values"""
        self.pi = np.zeros(nStates)
        self.t = np.zeros((nStates, nStates))
        self.e = np.zeros((nStates, nObs))
        #self.pi = [0] * nStates #initial state probs
        #self.t = [[0] * nStates for i in range(nStates)] #transition mat
        #self.e = [[0] * nObs for i in range(nStates)] #emission mat
        self.nStates = nStates
        self.nObs = nObs

    def learn(self, obs, ground_truth):
        """
        Learns from list of observation seq, and associated ground truths
        obs: list of list of ints in {0, ... nObs-1}, which is list of observed sequences.
        ground_truth: list of list of ints in {0, ... nStates - 1} which is associated list of ground truths.
        """
        assert(len(obs) == len(ground_truths))
        self.__init__(self.nStates, self.nObs) #reset
        for i, o in enumerate(obs):
            t = ground_truth[i]
            assert(len(o) == len(t))
            self.pi[t[0]] += 1
            for j in range(len(t) - 1):
                self.t[t[j]][t[j+1]] += 1
                self.e[t[j]][o[j]] += 1
            j += 1
            self.e[t[j]][o[j]] += 1
        #normalize and convert to log
        for i in range(self.nStates):
            self.pi[i] /= len(obs)
            self.pi[i] = self._convert_to_log(self.pi[i])
            Zt = sum(self.t[i])
            Ze = sum(self.e[i])
            for j in range(self.nStates):
                self.t[i][j] /= max(1, Zt)
                self.t[i][j] = self._convert_to_log(self.t[i][j])
            for j in range(self.nObs):
                self.e[i][j] /= max(1, Ze)
                self.e[i][j] = self._convert_to_log(self.e[i][j])

    def _convert_to_log(val):
        if val > 0:
            return log(val)
        else:
            return float('-inf')

    def viterbi(self, obs):
        """
        Viterbi inference of highest likelihood hidden states seq given observations
        O(|obs| * nStates^2)
        """
        tab = [[0] * self.nStates for i in range(len(obs))]
        backtrack = [[-1] * self.nStates for i in range(len(obs))]

        for i in range(self.nStates):
            tab[0][i] = self.e[i][obs[0]] + self.pi[i]
        for i in range(1, len(obs)):
            for j in range(self.nStates):
                smax = -1
                maxval = float('-inf')
                for s in range(self.nStates):
                    cs = tab[i - 1][s] + self.t[s][j]
                    if cs > maxval:
                        smax = s
                        maxval = cs
                assert(smax > -1 and smax < self.nStates)
                tab[i][j] = self.e[j][obs[i]] + maxval
                backtrack[i][j] = smax
        smax = -1
        llike = float('-inf')
        for s in range(self.nStates):
            if llike < tab[len(obs) - 1][s]:
                llike = tab[len(obs) - 1][s]
                smax =s

        best = [-1] * len(obs)
        best[-1] = smax
        for i in range(N-2, -1, -1):
            best[i] = backtrack[i+1][best[i+1]]
        return best, llike
