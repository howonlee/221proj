#for alternate q and hmm state configs
#I did this more manually previously, but script is better
import scipy, cPickle, sys, random, collections, itertools
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
        obs2 = []
        ground2 = []
        actions = []
        for i in range(minNote, maxNote):
            actions.append(i)
        qModel = QLearner(actions, epsilon=0.1, alpha=0.2, gamma=0.9)

#HMM
#2. It might also be that a lot of four-note runs are produced by the certain class of these short sequences, so the first note of 4-note run, was tried as the hidden state configuration.
#3. Note that a tritone interval sounds much the same anywhere, so it might have been the case that the next note is generated from the difference between the previous note and the note before that.
        for ls in self.clusterData:
            for quadidx, quad in enumerate(ls):
                tempquad = map(lambda x: x - minNote, quad)
                obs.append(tempquad[:])
                obs2.append(tempquad[:])
                tempquad2 = map(lambda x: (x - minNote) % 12, quad)
                notediff = [tempquad[0] - tempquad[1], tempquad[1] - tempquad[2], tempquad[2] - tempquad[3], tempquad[3] - tempquad[4]]
                notediff = map(lambda x: abs(x), notediff)
                ground.append(notediff) #difference between prev note and note before that
                ground2.append(tempquad2[0] * 4)
                if (quad):
                    for idx, note in enumerate(quad):
                        if idx > 0:
                            prevNote = quad[idx - 1]
                            qModel.learn(abs(prevNote - note), note, 1, note)
        hmmModel.learn(obs, ground)
        hmmModel2.learn(obs2, ground2)
        return (hmmModel, hmmModel2, qModel)

def normalizeVec(vec):
    vecsum = vec.sum()
    return vec / vecsum

def makeHMMPred(datapoint, model):
    best, _2 = model.viterbi(map(lambda x: x - minNote, datapoint))
    return best[-1] + minNote

def makeQLearningPred(datapoint, model):
    return model.chooseAction(abs(datapoint[-1] - datapoint[-2]))

def makeNgram(inputlist, n):
    return zip(*[inputlist[i:] for i in range(n)])

if __name__ == "__main__":
    assert(len(sys.argv) == 4) #want this to be the datapoints here
    m = Model()
    hmmmod, hmmmod2, qmod = m.train()
    hmmpred = []
    hmmpred2 = []
    qpred = []
    notes = map(collections.itemgetter(0), cPickle.load(file(sys.argv[1])))
    for datapt in makeNgram(notes, 10): #handle datapoints properly instead of this
        print datapt
        hmmpred.append((makeHMMPred(datapt, hmmmod), None)) #dummy None values to work with the ks stats script
        hmmpred2.append((makeHMMPred(datapt, hmmmod2), None))
        qpred.append((makeQLearningPred(datapt, qmod), None))
    with open(sys.argv[2], 'w') as hmmf:
        cPickle.dump(hmmpred, hmmf)
    with open(sys.argv[3], 'w') as hmmf2:
        cPickle.dump(hmmpred2, hmmf2)
    with open(sys.argv[4], 'w') as qf:
        cPickle.dump(qpred, qf)
