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

    def learn(self, obs, ground_truth, reset=True):
        """
        Learns from list of observation seq, and associated ground truths
        obs: list of list of ints in {0, ... nObs-1}, which is list of observed sequences.
        ground_truth: list of list of ints in {0, ... nStates - 1} which is associated list of ground truths.
        Neither of these are np arrays!
        """
        assert(len(obs) == len(ground_truth))
        if reset:
            self.__init__(self.nStates, self.nObs) #reset
        for i, ob in enumerate(obs):
            ground = ground_truth[i]
            assert(len(ob) == len(ground))
            if len(ground) == 1: continue
            self.pi[ground[0]] += 1
            for j in range(len(ground) - 1):
                self.trans[ ground[j], ground[j+1] ] += 1
                self.emis[ ground[j], ob[j]] += 1
            j += 1
            self.emis[ ground[j], ob[j] ] += 1
        print "transition matrix after learning, before normalizing: ", self.trans
        print "emission matrix after learning, before normalizing: ", self.emis

        #normalize and convert to log
        nplog = np.vectorize(self._convert_to_log)
        self.pi = nplog(np.divide(self.pi, len(obs)))
        Zt = self.trans.sum(axis=1)
        Zt[Zt < 1] = 1
        Ze = self.emis.sum(axis=1)
        Ze[Ze < 1] = 1
        self.trans = nplog(self.trans / Zt[:, np.newaxis])
        self.emis = nplog(self.emis / Ze[:, np.newaxis])
        print "transition matrix after normalizing: ", self.trans
        print "emission matrix after normalizing: ", self.emis

    def _convert_to_log(self, val):
        if val > 0:
            return log(val)
        else:
            return float('-inf')

    def viterbi(self, obs):
        """
        Viterbi inference of highest likelihood hidden states seq given observations
        O(|obs| * nStates^2)
        Observations is not numpy arrays!
        """
        tab = np.zeros((len(obs), self.nStates))
        backtrack = np.zeros((len(obs), self.nStates))
        backtrack.fill(-1)

        for i in range(self.nStates):
            tab[0, i] = self.emis[i, obs[0]] + self.pi[i]
        print self.trans
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
        llike = np.amax(tab[len(obs) - 1, :])
        smax = np.argmax(tab, axis=1) #hopefully one argmax
        if (type(smax) != "int"):
            smax = smax[0]

        best = np.zeros(len(obs))
        best.fill(-1)
        best[-1] = smax
        for i in range(len(obs)-2, -1, -1):
            best[i] = backtrack[i+1, best[i+1]]
        return list(best), llike
