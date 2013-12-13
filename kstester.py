import scipy, cPickle, sys, random
from scipy import stats
import numpy as np

assert len(sys.argv) == 2
data = cPickle.load(file(sys.argv[1]))

uniform = [random.randint(1, 12) for i in len(data)]
jsbdata = cPickle.load(file("~/Dropbox/School/fall_13_14/cs221/proj/musicproj/data/JSB Chorales.pickle"))
jsbdist = jsbdata['train']
jsbdist = [filter(lambda x: len(x) == 4, l) for l in jsbdist]
jsbdist = [filter(lambda x: not(np.allclose(list(x), [0.,0.,0.,0.])), l) for l in jsbdist]
jsbmodel = np.zeros((12,12,12))
for ls in jsbdist:
  for quadidx, quad in enumerate(ls):
    tempquad = map(lambda x: x % 12, quad)
    for idx, note in enumerate(quad):
      if idx > 2:
        currNote = note - minNote
        prevNote = quad[idx - 1] - minNote
        prevNote2 = quad[idx - 2] - minNote
        jsbmodel[currNote, prevNote, prevNote2] += 1
def normalizeVec(vec):
    vecsum = vec.sum()
    return vec / vecsum
def jsbdraw(prev=None, prev2=None):
  if prev is None:
    probs = normalizeVec(jsbmodel.sum(axis=2).sum(axis=1)[:] + 0.05)
  elif prev2 is None:
    probs = normalizeVec(jsbmodel.sum(axis=2)[:, prev] + 0.05)
  else:
    probs = normalizeVec(jsbmodel[:, prev, prev2] + 0.05)
  return np.random.choice(np.arange(1, 13), p=probs)

jsb = []
for i in len(data):
  if len(jsb) >= 2:
    jsb.append(jsbdraw(prev=jsb[-1], prev2=jsb[-2]))
  elif len(jsb) >= 1:
    jsb.append(jsbdraw(prev=jsb[-1]))
  else:
    jsb.append(jsbdraw())

#1. ks_2samp on the pred vs uniform pred
k1, p1 = stats.ks_2samp(data, uniform)
print "k against uniform samples is: ", k1
print "p against uniform samples is: ", p1
#2. ks_2samp on the pred vs bach pred
k2, p2 = stats.ks_2samp(data, jsb)
print "k against jsb samples is: ", k2
print "p against jsb samples is: ", p2

