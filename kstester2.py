import scipy, cPickle, sys, random
from operator import itemgetter, mod
from scipy import stats
import numpy as np

assert len(sys.argv) == 3
data = map(itemgetter(0), cPickle.load(file(sys.argv[1])))
data2 = map(itemgetter(0), cPickle.load(file(sys.argv[2])))
data = map(lambda x: mod(x, 12), data)
data2 = map(lambda x: mod(x, 12), data2)
print data
print data2

#don't forget to munge the data properly:
#ks test is for equality of 1-d probability distributions, to compare sample with reference distribution, or to compared two samples
#this HAS to be two samples, alright
k1, p1 = stats.ks_2samp(data, data2)
print "k betw samples is: ", k1
print "p betw samples is: ", p1

