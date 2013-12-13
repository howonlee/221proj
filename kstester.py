import scipy, pickle, sys
from scipy import stats

assert len(sys.argv) == 2
data = sys.argv[1]

uniform = []
#compare against uniform: draw here

jsb = []
#compare against js bach: draw here

#1. ks_2samp on the pred vs uniform pred
k1, p1 = stats.ks_2samp(data, uniform)
print "k against uniform samples is: ", k1
print "p against uniform samples is: ", p1
#2. ks_2samp on the pred vs bach pred
k2, p2 = stats.ks_2samp(data, jsb)
print "k against jsb samples is: ", k2
print "p against jsb samples is: ", p2

