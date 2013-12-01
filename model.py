import collections, operator, cPickle, utils, math, random
import numpy as np
from hmm import HMM
from q import QLearner

"""
muse = cPickle.load(file("./data/MuseData.pickle"))
print "finished loading muse..."
pianomidi = cPickle.load(file("./data/Piano-midi.de.pickle"))
print "finished loading pianomidi..."
nottingham = cPickle.load(file("./data/Nottingham.pickle"))
print "finished loading nottingham..."
"""
jsb = cPickle.load(file("./data/JSB Chorales.pickle"))
maxNote = 96
minNote = 43
noteRange = 96 - 43
print "finished loading jsb..."
cluster = runKMeans(jsb["train"])
print "finished running clusters..."

def runKMeans(data, iters=10, k=12):
    """
    Runs K-means to learn k centroids, for iter iterations.

    Args:
      k - number of centroids.
      patches - 2D numpy array of size patchSize x numPatches
      maxIter - number of iterations to run K-means for

    Returns:
      centroids - 2D numpy array of size patchSize x k
    """
    music = np.zeros((noteRange+1, noteRange+1, noteRange+1, noteRange+1))
    for ls in data:
        for quad in ls:
            if (quad): #needed because some quads are null
                note0 = quad[0] - minNote
                note1 = quad[1] - minNote
                note2 = quad[2] - minNote
                note3 = quad[3] - minNote
                music[note0, note1, note2, note3] += 1

    # This line starts you out with randomly initialized centroids in a matrix
    # with patchSize rows and k columns. Each column is a centroid.
    centroids = np.random.randn(4,k)
    N = len(data[0])
    #numPatches = patches.shape[1]
    clustersId = np.random.randint(0, k, size=numPatches)

    for i in range(iters):
        clustersId = np.array([np.argmin([np.linalg.norm(patches[:, p] - centroids[:, c]) for c in range(k)]) for p in range(numPatches)])
        map(lambda c: np.mean([patches[:, p] for p in xrange(numPatches) if clustersId[p] == c], axis=0, out=centroids[:, c]), range(k))
    return centroids

#this is a multinomial NB
#it is terrible at this task
def trainNB(data):
    N = len(data)
    prior = collections.defaultdict(int)
    condprob = {}
    for i in range(minNote, maxNote):
        condprob[i] = collections.defaultdict(lambda: 0.002)
    for ls in data:
        for quad in ls:
            if (quad): #needed because some quads are null
                for q in quad:
                    if q < minNote or q > maxNote: continue
                    prior[q] += 1
            if (len(quad) - 1 > 0):
                classVal = quad[-1]
                for q in quad[:-1]: #in other words, all the other q's
                    if q < minNote or q > maxNote: continue
                    condprob[classVal][q] += 1
    for i in range(minNote, maxNote):
        for j in condprob[i]:
            #there exist smarter ways of normalizing...
            condprob[i][j] = math.log(condprob[i][j] / prior[i]) #currently, priors are just counts
        prior[i] = math.log(prior[i] / float(N))
    return (prior, condprob)

def trainMM(data):
    N = len(data)
    model = np.zeros((noteRange + 1, noteRange + 1))
    for ls in data:
        for quad in ls:
            if (quad): #needed because some quads are null
                for idx, q in enumerate(quad):
                    if idx > 0:
                        currNote = q - minNote
                        prevNote = quad[idx - 1] - minNote
                        model[currNote, prevNote] += 1
    return (model, None)

def trainMMOrder3(data):
    N = len(data)
    model = np.zeros((noteRange+1, noteRange+1, noteRange+1))
    for ls in data:
        for quad in ls:
            if (quad): #needed because some quads are null
                for idx, q in enumerate(quad):
                    if idx > 2:
                        currNote = q - minNote
                        prevNote = quad[idx - 1] - minNote
                        prevNote2 = quad[idx - 2] - minNote
                        model[currNote, prevNote, prevNote2] += 1
    return (model, None)

def trainHMM(data):
    model = HMM(noteRange+1, noteRange+1)
    obs = []
    ground = []
    for ls in data:
        for quad in ls:
            if (len(quad) > 1): #needed because some quads are null
                obs.append(map(lambda x: x - minNote, quad))
                ground.append([cluster[quad]] * len(quad))
    model.learn(obs, ground) #this is a bit wrong
    return (model, None)

def trainQLearning(data):
    actions = []
    for i in range(minNote, maxNote):
        actions.append(i)
    q = QLearner(actions, epsilon=0.1, alpha=0.2, gamma=0.9)
    for ls in data:
        for quad in ls:
            if (quad):
                for idx, note in enumerate(quad):
                    if idx > 1:
                        currNote = note
                        prevNote = quad[idx - 1]
                        q.learn(prevNote, cluster[quad], 1, note) #this is a bit wrong
                        #q.learn(state1, action1, reward, state2)
    return (q, None)

def makeNBPred(datapoint, prior, condprob):
    classes = collections.defaultdict(int)
    for i in range(minNote, maxNote):
        classes[i] = prior[i]
        for t in datapoint:
            classes[i] += condprob[i][t]
    v = list(classes.values())
    k = list(classes.keys())
    arg = k[v.index(max(v))]
    return arg

def normalizeVec(vec):
    vecsum = vec.sum()
    return vec / vecsum

def makeMMPred(datapoint, model, _):
    last = datapoint[-1] - minNote
    probs = normalizeVec(model[:, last] + 0.05)
    val = np.random.choice(np.arange(minNote, maxNote+1), p=probs)
    return val

def makeMM3Pred(datapoint, model, _):
    prev1 = datapoint[-1] - minNote
    prev2 = datapoint[-2] - minNote
    probs = normalizeVec(model[:, prev1, prev2] + 0.05)
    val = np.random.choice(np.arange(minNote, maxNote+1), p=probs)
    return val

def makeHMMPred(datapoint, model, _):
    best, _2 = model.viterbi(map(lambda x: x - minNote, datapoint)) #this is probably not the right way to do it
    return best[-1] + minNote

def makeQLearningPred(datapoint, model, _):
    return model.chooseAction(datapoint[-1])
