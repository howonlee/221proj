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
print "finished loading jsb..."

#this is a multinomial NB
#it is terrible at this task
def trainNB(data):
    N = len(data)
    prior = collections.defaultdict(int)
    condprob = {}
    for i in range(67, 97):
        condprob[i] = collections.defaultdict(lambda: 0.002)
    for ls in data:
        for quad in ls:
            if (quad): #needed because some quads are null
                for q in quad:
                    if q < 67 or q > 97: continue
                    prior[q] += 1
            if (len(quad) - 1 > 0):
                classVal = quad[-1]
                for q in quad[:-1]: #in other words, all the other q's
                    if q < 67 or q > 97: continue
                    condprob[classVal][q] += 1
    for i in range(67, 97):
        for j in condprob[i]:
            #there exist smarter ways of normalizing...
            condprob[i][j] = math.log(condprob[i][j] / prior[i]) #currently, priors are just counts
        prior[i] = math.log(prior[i] / float(N))
    return (prior, condprob)

def trainMM(data):
    N = len(data)
    model = np.zeros((30, 30))
    for ls in data:
        for quad in ls:
            if (quad): #needed because some quads are null
                for idx, q in enumerate(quad):
                    if idx > 0:
                        currNote = q - 67
                        prevNote = quad[idx - 1] - 67
                        model[currNote, prevNote] += 1
    return (model, None)

def trainMMOrder3(data):
    N = len(data)
    model = np.zeros((30, 30, 30))
    for ls in data:
        for quad in ls:
            if (quad): #needed because some quads are null
                for idx, q in enumerate(quad):
                    if idx > 2:
                        currNote = q - 67
                        prevNote = quad[idx - 1] - 67
                        prevNote2 = quad[idx - 2] - 67
                        model[currNote, prevNote, prevNote2] += 1
    return (model, None)

def trainHMM(data):
    raise NotImplemented("Not implemented")
    model = HMM(nStates, nObs)
    for ls in data:
        for quad in ls:
            if (quad): #needed because some quads are null
                for idx, q in enumerate(quad):
                    if idx > 2:
                        currNote = q - 67
                        prevNote = quad[idx - 1] - 67
                        prevNote2 = quad[idx - 2] - 67
                        model[currNote, prevNote, prevNote2] += 1

def trainQLearning(data):
    #we have to treat the q learner as having a state which it learns previously
    actions = {}
    #fill out actions here
    q = QLearner(actions, epsilon=0.1, alpha=0.2, gamma=0.9)
    #do some actual learning here
    return (q, None)

def makeNBPred(datapoint, prior, condprob):
    classes = collections.defaultdict(int)
    for i in range(67, 97):
        classes[i] = prior[i]
        for t in datapoint:
            classes[i] += condprob[i][t]
    v = list(classes.values())
    k = list(classes.keys())
    arg = k[v.index(max(v))]
    #is this right?
    return arg

def makeMMPred(datapoint, model, _):
    last = datapoint[-1] - 67
    val = np.argmax(model[:, last]) + 67
    return val

def makeMM3Pred(datapoint, model, _):
    prev1 = datapoint[-1] - 67
    prev2 = datapoint[-2] - 67
    val = np.argmax(model[:, prev1, prev2]) + 67
    return val

def makeHMMPred(datapoint, model, _):
    return 67

def makeQLearningPred(datapoint, model, _):
    return model.chooseAction(datapoint)
