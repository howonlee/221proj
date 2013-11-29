from hmm import HMM
import unittest

def test_hmm():
    m = HMM(2, 2)
    observations = [[0,0,0,0,0,1,1,1,1,1,0,1,0,0,0,1,0,1,1,1,1],[0,0,0,0,1,0,1,1,0,1,1,0,0,1,0,0,1,1,1,1,0,0,1,0,0]]
    ground = [[0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1],[0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,0]]
    m.learn(observations, ground)
    trueres = ([0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0], -21.944)
    res = m.viterbi(observations[1])
    assert trueres[0] == res[0]
    print trueres[1]
    print res[1]
    assert abs(trueres[1] - res[1]) < 0.1

if __name__ == "__main__":
    m = HMM(2, 2)
    observations = [[0,0,0,0,0,1,1,1,1,1,0,1,0,0,0,1,0,1,1,1,1],[0,0,0,0,1,0,1,1,0,1,1,0,0,1,0,0,1,1,1,1,0,0,1,0,0]]
    ground = [[0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,1,1,1,1,1,1],[0,0,0,0,1,1,1,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,0]]
    m.learn(observations, ground)
    trueres = ([0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 0, 0, 0], -21.944)
    res = m.viterbi(observations[1])
    assert trueres[0] == res[0]
    print "true res: ", trueres[1]
    print "res: ", res[1]
    assert abs(trueres[1] - res[1]) < 0.1
