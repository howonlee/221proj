CS221 final project
=============

To actually play this:

* python player.py: you can set your own data file if you want to
* Use the asdfjkl;wruo keys, you should be able to hear them properly. To show predictions, press 0. To switch models, use the 1234 keys.
* There is a kolmogorov-smirnov tester which is fairly intuitive to use
* All the graphs are fairly conveniently autogenerated for you, so you can have your own graphs.
* The confusion matrix plotters are in the qFeature branch
* I was going to have to tell you the Byzantine process for going over a previously recorded node played sequence and do over the q-learning with a different state config or the hmm with a different state config, but now you can use the script instead (altstates.py)
* There is a KMeans module that is not used which uses a bunch of numpy stuff. K-S test is not implemented by me: I just took it from scipy.stats
* There is another readme.md in the /usr/ folder, that is about the data
