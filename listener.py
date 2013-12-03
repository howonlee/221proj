import sys, pygame, cPickle, time
from model import *

if __name__ == "__main__":
    assert (len(sys.argv) == 2)
    model = Model("data/noteData_ex_random.pickle")
    import utils
    pygame.init()
    pygame.mixer.init(44100, -16, 2, buffer=512)
    pygame.mixer.set_num_channels(12)
    toUnpickle = sys.argv[1]
    data = cPickle.load(file(toUnpickle))
    soundMappings = utils.initSoundMappings()
    for val in data:
        note = val[0]
        t = val[1] - origTime
        soundMappings[note].play(loops=-1)
        time.sleep(t / 10000)
        soundMappings[note].stop()
