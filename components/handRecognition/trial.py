import sys
from . import RandomForest
import os
import dill


sys.modules['RandomForest'] = RandomForest

# RH
load_path = os.path.join('/s/red/a/nobackup/vision/jason/forest', 'RH_forest.pickle')
f = open(load_path, 'rb')
forest = dill.load(f)
f.close()
f = open(load_path, 'wb')
dill.dump(forest, f)

# LH
load_path = os.path.join('/s/red/a/nobackup/vision/jason/forest', 'LH_forest.pickle')
f = open(load_path, 'rb')
forest = dill.load(f)
f.close()
f = open(load_path, 'wb')
dill.dump(forest, f)

