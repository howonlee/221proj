import collections, operator, cPickle, math, random
import numpy as np
from hmm import HMM
from q import QLearner

"""
muse = cPickle.load(file("./data/MuseData.pickle"))
print "finished loading muse..."
pianomidi = cPickle.load(file("./data/Piano-midi.de.pickle"))
print "finished loading pianomidi..."
nottingham = cPickle.load(file("./data/Nottingham.pickle"))
clusterData = nottingham["train"]
"""
def runKMeans(data, iters=1, k=3):
    numPatches = sum([len(x) for x in data])
    music = np.zeros((numPatches, 4))
    totalidx = 0
    for ls in data:
        for idx, quad in enumerate(ls):
            if (quad and len(quad) == 4): #needed because some quads are null
                assert (len(quad) == 4)
                music[totalidx] = list(quad)
                totalidx += 1
    music = music.T
    np.random.shuffle(music)
    # This line starts you out with randomly initialized centroids in a matrix
    # with patchSize rows and k columns. Each column is a centroid.
    centroids = np.random.randn(4,k)
    clustersId = np.random.randint(k, size=numPatches)
    for i in range(iters):
        clustersId = np.array([np.argmin([np.linalg.norm(music[:, p] - centroids[:, c]) for c in range(k)]) for p in range(numPatches)])
        for c in range(k):
            mean = np.mean([music[:, p] for p in xrange(numPatches) if clustersId[p] == c], axis=0)
            if np.isnan(mean).any():
                continue
            centroids[:, c] = mean
        #map(lambda c: np.mean([music[:, p] for p in xrange(numPatches) if clustersId[p] == c], axis=0, out=centroids[:, c]), range(k))
    print "centroids: ", centroids
    print "clustersId: ", clustersId
    return (centroids, clustersId)

pianomidi = cPickle.load(file("./data/Piano-midi.de.pickle"))
print "finished loading pianomidi..."
clusterData = pianomidi["train"]
clusterData = [filter(lambda x: len(x) == 4, l) for l in clusterData]
clusterData = [filter(lambda x: not(np.allclose(list(x), [0.,0.,0.,0.])), l) for l in clusterData]
maxNote = float("-inf")
minNote = float("inf")
noteRange = float("-inf")
for ls in clusterData:
    for quad in ls:
        for note in quad:
            if note > maxNote:
                maxNote = note
            if note < minNote:
                minNote = note
noteRange = maxNote - minNote

print "after filtering: ", sum([len(x) for x in clusterData])
_, cluster = runKMeans(clusterData)
print "finished running clusters..."

def train(data):
    mmModel = np.zeros((noteRange+1, noteRange+1))
    mm3Model = np.zeros((noteRange+1, noteRange+1, noteRange+1))
    mmKatzModel = np.zeros((noteRange+1, noteRange+1, noteRange+1))
    mmKneserNeyModel = np.zeros((noteRange+1, noteRange+1, noteRange+1))
    hmmModel = HMM(noteRange+1, noteRange+1)
    obs = []
    ground = []
    actions = []
    for i in range(minNote, maxNote):
        actions.append(i)
    qModel = QLearner(actions, epsilon=0.1, alpha=0.2, gamma=0.9)
    for ls in data:
        for quadidx, quad in enumerate(ls):
            obs.append(map(lambda x: x - minNote, quad))
            ground.append([cluster[quadidx]] * len(quad))
            if (quad):
                for idx, note in enumerate(quad):
                    if idx > 0:
                        currNote = note
                        prevNote = quad[idx - 1]
                        #Q learning
                        #q.learn(state1, action1, reward, state2)
                        qModel.learn(prevNote, cluster[quadidx], 1, note) #this is a bit wrong
                        #Markov model
                        mmModel[currNote - minNote, prevNote - minNote] += 1
                    if idx > 2:
                        #Markov model, more order
                        currNote = note - minNote
                        prevNote = quad[idx - 1] - minNote
                        prevNote2 = quad[idx - 2] - minNote
                        mm3Model[currNote, prevNote, prevNote2] += 1
                        #do some stuff with Katz, Kneser-Ney model here
    #fuck around with Katz, Kneser-Ney model here
    hmmModel.learn(obs, ground)
    return (mmModel, mm3Model, hmmModel, qModel, mmKatzModel, mmKneserNeyModel)

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

def makeMMKatzPred(datapoint, model):
    val = 1
    return val

def makeMMKneserNeyPred(datapoint, model):
    val = 1
    return val

def makeHMMPred(datapoint, model):
    best, _2 = model.viterbi(map(lambda x: x - minNote, datapoint)) #this is probably not the right way to do it
    return best[-1] + minNote

def makeQLearningPred(datapoint, model):
    return model.chooseAction(datapoint[-1])
