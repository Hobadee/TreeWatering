# TreeWatering
A Python program designed to run on a RPi with the Adafruit motor HAT.  This will keep the water level in my Christmas tree full.  When the water level drops, it will turn on a pump to add more water to the tree.

This is a pretty messy repo at the moment.  The best version to use right now is `tree2022MT.py`.  This is currently working for me, although I'm missing a resevoir water level sensor at the moment, so I can run my pump dry if I'm not paying attention to the resevoir.  (Right now I've hardcoded the resevoir status to `True`, ie: it's full)