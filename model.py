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
noteRange = 96 - 43 + 1
print "finished loading jsb..."

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
    model = np.zeros((noteRange, noteRange))
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
    model = np.zeros((noteRange, noteRange, noteRange))
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
    """Todo: link into HMM class"""
    """ next action: figure out how the hidden states in HMM will work """
    """ or maybe say that the hidden state is the first member of the quad? """
    model = HMM(noteRange, noteRange)
    obs = []
    ground = []
    for ls in data:
        for quad in ls:
            if (len(quad) > 1): #needed because some quads are null
                obs.append(map(lambda x: x - minNote, quad))
                ground.append([quad[0] - minNote] * len(quad))
    print "=================== obs ==============="
    print obs
    print "=================== ground ==============="
    print ground

    model.learn(obs, ground) #this is a bit wrong

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
                        q.learn(prevNote, quad[0], 1, note) #this is a bit wrong
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

def makeMMPred(datapoint, model, _):
    """Todo: make probabilistic"""
    last = datapoint[-1] - minNote
    val = np.argmax(model[:, last]) + minNote #use np.random.choice(67, 97, p=something)
    return val

def makeMM3Pred(datapoint, model, _):
    """Todo: make probabilistic"""
    prev1 = datapoint[-1] - minNote
    prev2 = datapoint[-2] - minNote
    val = np.argmax(model[:, prev1, prev2]) + maxNote #use np.random.choice(67, 97, p=something)
    return val

def makeHMMPred(datapoint, model, _):
    #states are chords?
    best, _2 = model.viterbi(datapoint) #this is probably not the right way to do it
    return best[-1]

def makeQLearningPred(datapoint, model, _):
    #do some learning here
    return model.chooseAction(datapoint)
