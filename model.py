import collections, operator, cPickle, math, random
import numpy as np
from scipy.cluster.vq import *
from hmm import HMM
from q import QLearner

maxNote = float("-inf")
minNote = float("inf")
noteRange = float("-inf")

class Model:
    def __init__(self, fileName):
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
        print "after filtering: ", sum([len(x) for x in self.clusterData])
        _, self.cluster = self.runKMeans(self.clusterData)
        print "finished running clusters..."

    def runKMeans(self, data, iters=1, k=3):
        numPatches = sum([len(x) for x in data])
        music = np.zeros((numPatches, 4), dtype=np.float32)
        totalidx = 0
        for ls in data:
            for idx, quad in enumerate(ls):
                if (quad and len(quad) == 4): #needed because some quads are null
                    assert (len(quad) == 4)
                    music[totalidx] = list(quad)
                    totalidx += 1
        music = whiten(music)
        centroids, clustersId = kmeans2(music, 12)
        return (centroids, clustersId)

    def train(self):
        mmModel = np.zeros((noteRange+1, noteRange+1))
        mm3Model = np.zeros((noteRange+1, noteRange+1, noteRange+1))
        hmmModel = HMM(12, noteRange+1)
        obs = []
        ground = []
        actions = []
        for i in range(minNote, maxNote):
            actions.append(i)
        qModel = QLearner(actions, epsilon=0.1, alpha=0.2, gamma=0.9)
        for ls in self.clusterData:
            for quadidx, quad in enumerate(ls):
                tempquad = map(lambda x: x - minNote, quad)
                obs.append(tempquad[1:])
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
                            #Markov model
                            mmModel[currNote - minNote, prevNote - minNote] += 1
                        if idx > 2:
                            #Markov model, more order
                            currNote = note - minNote
                            prevNote = quad[idx - 1] - minNote
                            prevNote2 = quad[idx - 2] - minNote
                            mm3Model[currNote, prevNote, prevNote2] += 1
        hmmModel.learn(obs, ground)
        return (mmModel, mm3Model, hmmModel, qModel)

def normalizeVec(vec):
    vecsum = vec.sum()
    return vec / vecsum

def makeMMPred(datapoint, model):
    last = datapoint[-1] - minNote
    probs = normalizeVec(model[:, last] + 0.05)
    val = np.random.choice(np.arange(minNote, maxNote+1), p=probs)
    return val

def makeMM3Pred(datapoint, model):
    prev1 = datapoint[-1] - minNote
    prev2 = datapoint[-2] - minNote
    probs = normalizeVec(model[:, prev1, prev2] + 0.05)
    val = np.random.choice(np.arange(minNote, maxNote+1), p=probs)
    return val

def makeHMMPred(datapoint, model):
    best, _2 = model.viterbi(map(lambda x: x - minNote, datapoint)) #this is probably not the right way to do it
    return best[-1] + minNote

def makeQLearningPred(datapoint, model):
    return model.chooseAction(datapoint[-1])
