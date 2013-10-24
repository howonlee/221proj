import collections, operator, cPickle, utils

def argmax(pairs):
    return max(pairs, key=operator.itemgetter(1))[0]
def argmax_iter(vals):
    return argmax(enumerate(vals))

#muse = cPickle.load(file("./data/MuseData.pickle"))
#print "finished loading muse..."
jsb = cPickle.load(file("./data/JSB Chorales.pickle"))
print "finished loading jsb..."
#nottingham = cPickle.load(file("./data/Nottingham.pickle"))
#print "finished loading nottingham..."
#pianomidi = cPickle.load(file("./data/Piano-midi.de.pickle"))
#print "finished loading pianomidi..."
for ls in jsb["train"]:
    for quad in ls:
        if quad:
            print utils.reverseMidiNoteMapping[quad[-1]]
