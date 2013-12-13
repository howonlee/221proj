#for alternate q and hmm state configs
#I did this more manually previously, but script is better
import scipy, cPickle, sys, random, collections
from scipy import stats
import numpy as np
from hmm import HMM
from q import QLearner

maxNote = float("-inf")
minNote = float("inf")
noteRange = float("-inf")

class Model:
    def __init__(self, fileName="data/noteData_ex_random.pickle"):
        global maxNote, minNote, noteRange
        self.data = cPickle.load(file("./%s" % fileName))
        print "finished loading data..."
        self.clusterData = self.data["train"]
        self.clusterData = [filter(lambda x: len(x) == 4, l) for l in self.clusterData]
        self.clusterData = [filter(lambda x: not(np.allclose(list(x), [0.,0.,0.,0.])), l) for l in self.clusterData]
        for ls in self.clusterData:
            for quad in ls:
                for note in quad:
                    if note > maxNote:
                        maxNote = note
                    if note < minNote:
                        minNote = note
        noteRange = maxNote - minNote

    def train(self):
        hmmModel = HMM(12, noteRange+1)
        hmmModel2 = HMM(12, noteRange+1)
        obs = []
        ground = []
        actions = []
        for i in range(minNote, maxNote):
            actions.append(i)
        qModel = QLearner(actions, epsilon=0.1, alpha=0.2, gamma=0.9)

#HMM
#1. It might be that the previous pitch played generates the observed note, so the previous pitch played could have been the states (this is different from the Markov model because of the 12-state space and the fact that I wasn't sampling but getting the maximum expectation of the distribution).
#2. It might also be that a lot of four-note runs are produced by the certain class of these short sequences, so the first note of 4-note run, was tried as the hidden state configuration.
#3. Note that a tritone interval sounds much the same anywhere, so it might have been the case that the next note is generated from the difference between the previous note and the note before that.

#Qlearning
#1. The previous note could be construed as a state from which actions, construed as notees, were generated.
#2. The difference between previous note could also be construed as a state from which actions, construed as notes, were generated.
        for ls in self.clusterData:
            for quadidx, quad in enumerate(ls):
#######CHANGE THIS BIT
                tempquad = map(lambda x: x - minNote, quad) #take this out for prevnote stuff
                obs.append(tempquad[1:]) #this is for hmm: you can also do same thing for qlearning to change state that way
                tempquad = map(lambda x: (x - minNote) % 12, quad)
                ground.append(tempquad[:3])
                if (quad):
                    for idx, note in enumerate(quad):
                        if idx > 0:
                            currNote = note
                            prevNote = quad[idx - 1]
                            #Q learning
                            #q.learn(state1, action1, reward, state2)
                            qModel.learn(prevNote, note, 1, note)
        hmmModel.learn(obs, ground)
#######STOP CHANGING HERE
        return (hmmModel, hmmModel2, qModel)

def normalizeVec(vec):
    vecsum = vec.sum()
    return vec / vecsum

def makeHMMPred(datapoint, model):
    best, _2 = model.viterbi(map(lambda x: x - minNote, datapoint))
    return best[-1] + minNote

def makeQLearningPred(datapoint, model):
    return model.chooseAction(datapoint[-1])

if __name__ == "__main__":
    assert(len(sys.argv) == 4) #want this to be the datapoints here
    m = Model()
    hmmmod, hmmmod2, qmod = m.train()
    hmmpred = []
    hmmpred2 = []
    qpred = []
    notes = map(collections.itemgetter(0), cPickle.load(file(sys.argv[1])))
    for i in notes:
        #handle datapoints properly now
        hmmpred.append((makeHMMPred(i, hmmmod), None)) #dummy None values to work with the ks stats script
        hmmpred2.append((makeHMMPred(i, hmmmod2), None))
        qpred.append((makeQLearningPred(i, qmod), None))
    with open(sys.argv[2], 'w') as hmmf:
        cPickle.dump(hmmpred, hmmf)
    with open(sys.argv[3], 'w') as hmmf2:
        cPickle.dump(hmmpred2, hmmf2)
    with open(sys.argv[4], 'w') as qf:
        cPickle.dump(qpred, qf)
