# get location of the example mesh
from os.path import dirname, join, realpath
pth = dirname(realpath(__file__))
bunny_scan = join(pth, 'StanfordBunny.ply')

from pymeshfix.examples.fix import *
