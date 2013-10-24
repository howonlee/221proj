import collections, operator, cPickle, utils

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
classpriors = {}
freqs = {}
for i in range(67, 97):
    freqs[i] = collections.defaultdict(int)
for ls in jsb["train"]:
    for quad in ls:
        if (quad):
            for q in quad:
                classpriors[q] += 1
        if (len(quad) - 1 > 0):
            classVal = quad[-1]
            for q in quad[:-1]:
                freqs[classVal][q] += 1

