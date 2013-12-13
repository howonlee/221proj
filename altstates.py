#for alternate q and hmm state configs
#I did this more manually previously, but script is better
import scipy, cPickle, sys, random
from scipy import stats
import numpy as np

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
        obs = []
        ground = []
        actions = []
        for i in range(minNote, maxNote):
            actions.append(i)
        qModel = QLearner(actions, epsilon=0.1, alpha=0.2, gamma=0.9)
        for ls in self.clusterData:
            for quadidx, quad in enumerate(ls):
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
        return (hmmModel, qModel)

def normalizeVec(vec):
    vecsum = vec.sum()
    return vec / vecsum

def makeHMMPred(datapoint, model):
    best, _2 = model.viterbi(map(lambda x: x - minNote, datapoint)) #this is probably not the right way to do it
    return best[-1] + minNote

def makeQLearningPred(datapoint, model):
    return model.chooseAction(datapoint[-1])
