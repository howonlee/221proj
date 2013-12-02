import utils, sys, pygame, cPickle

soundMappings = utils.initSoundMappings()

if __name__ == "__main__":
    assert (len(sys.argv) == 2)
    toUnpickle = sys.argv[1]
    data = cPickle.load(file(toUnpickle))
    prevTime = data[0][1]
    for val in data:
        note = val[0]
        time = val[1] - prevTime
        prevTime = time
        play(note)
        wait(time)
