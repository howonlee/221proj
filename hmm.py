from __future__ import division
from math import log
from copy import deepcopy
import numpy as np

class HMM:
    def __init__(self, nStates, nObs):
        """nStates is number of hidden states, nObs is number of possible observed values"""
        self.pi = np.zeros(nStates)
        self.trans = np.zeros((nStates, nStates)) #transition mat
        self.emis = np.zeros((nStates, nObs)) #emission mat
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
        for i, ob in enumerate(obs):
            ground = ground_truth[i]
            assert(len(ob) == len(ground))
            self.pi[ground[0]] += 1
            for j in range(len(ground) - 1):
                self.trans[ ground[j], ground[j+1] ] += 1
                self.emis[ ground[j], ob[j]] += 1
            j += 1
            self.emis[ ground[j], ob[j] ] += 1

        #normalize and convert to log
        self.pi = np.divide(self.pi, len(obs))
        nplog = np.vectorize(self._convert_to_log)
        self.pi = nplog(self.pi)
        for i in range(self.nStates):
            Zt = numpy.sum(self.trans, 1)[i] #is this the right axis?
            Ze = numpy.sum(self.emis, 1)[i] #is this the right axis?
            for j in range(self.nStates):
                self.trans[i, j] /= max(1, Zt)
            for j in range(self.nObs):
                self.emis[i, j] /= max(1, Ze)
            self.trans[i, :] = nplog(self.trans[i, :])
            self.emis[i, :] = nplog(self.emis[i, :])

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
        tab = np.zeros((len(obs), self.nStates))
        backtrack = np.zeros((len(obs), self.nStates))
        backtrack.fill(-1)

        for i in range(self.nStates):
            tab[0, i] = self.emis[i, obs[0]] + self.pi[i]
        for i in range(1, len(obs)):
            for j in range(self.nStates):
                smax = -1
                maxval = float('-inf')
                for s in range(self.nStates):
                    cs = tab[i - 1, s] + self.trans[s, j]
                    if cs > maxval:
                        smax = s
                        maxval = cs
                assert(smax > -1 and smax < self.nStates)
                tab[i, j] = self.emis[j, obs[i]] + maxval
                backtrack[i, j] = smax
        smax = -1
        llike = float('-inf')
        for s in range(self.nStates):
            if llike < tab[len(obs) -1, s]:
                llike = tab[len(obs) - 1, s]
                smax = s

        best = np.zeros(len(obs))
        best.fill(-1)
        best[-1] = smax
        for i in range(N-2, -1, -1):
            best[i] = backtrack[i+1, best[i+1]]
        return best, llike
