import collections, operator, cPickle, utils, math

"""
muse = cPickle.load(file("./data/MuseData.pickle"))
print "finished loading muse..."
nottingham = cPickle.load(file("./data/Nottingham.pickle"))
print "finished loading nottingham..."
pianomidi = cPickle.load(file("./data/Piano-midi.de.pickle"))
print "finished loading pianomidi..."
"""
jsb = cPickle.load(file("./data/JSB Chorales.pickle"))
print "finished loading jsb..."

#this is a multinomial NB
def trainNB(data):
    N = len(data)
    prior = collections.defaultdict(int)
    condprob = {}
    for i in range(67, 97):
        condprob[i] = collections.defaultdict(lambda: 0.002)
    for ls in data:
        for quad in ls:
            if (quad):
                for q in quad:
                    prior[q] += 1
            if (len(quad) - 1 > 0):
                classVal = quad[-1]
                for q in quad[:-1]: #in other words, all the other q's
                    condprob[classVal][q] += 1
    for i in range(67, 97):
        for j in condprob[i]:
            condprob[i][j] = math.log(condprob[i][j] / prior[i]) #currently, priors are just counts
        prior[i] = math.log(prior[i] / float(N))
    return (prior, condprob)

def sigmoid(x):
    return 1 / (1 + math.exp(-x))

def makeNBPred(datapoint, prior, condprob):
    classes = collections.defaultdict(int)
    for i in range(67, 97):
        classes[i] = prior[i]
        for t in datapoint:
            classes[i] += condprob[i][t]
    v = list(classes.values())
    v = map(sigmoid, v)
    k = list(classes.keys())
    arg = k[v.index(max(v))]
    print "classes: ", v
    print "logl: ", classes[arg]
    print "arg: ", arg
    return arg

