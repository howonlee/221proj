import scipy, cPickle, sys, random
from operator import itemgetter
from scipy import stats
import numpy as np

assert len(sys.argv) == 3
data = map(itemgetter(0), cPickle.load(file(sys.argv[1])))
data2 = map(itemgetter(0), cPickle.load(file(sys.argv[2])))

print data2
#why is this so much easier goddamn it

#1. ks_2samp on the pred vs uniform pred
k1, p1 = stats.ks_2samp(data, data2)
print "k betw samples is: ", k1
print "p betw samples is: ", p1

