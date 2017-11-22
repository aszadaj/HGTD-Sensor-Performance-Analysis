import ROOT
import root_numpy as rnm
import time
import numpy as np
import pickle
from os import listdir
from os.path import isfile, join

import pulse as ps
import noise as ns
import pulse_plot as p_plot
import noise_plot as n_plot
import metadata as md

from pathos.multiprocessing import ProcessingPool as Pool
from datetime import datetime

#setupATLAS()
ROOT.gROOT.SetBatch(True)

# When running on lxplus, remember to run 'setupATLAS' and after 'asetup --restore'

# Comment: There are files which do have only selected number of channels
# this should be taken care of. Another aspect is that the there is a possibility
# to restrict amount of entries depending on the file, can be setup in metadata if
# needed.

def main_debug():
    
    runLog = md.getRunLog()
    restrictToUndoneRuns(runLog)
    
    
    exit()


def restrictToUndoneRuns(metaData):
    
    folderPath = "/Volumes/500 1/" #data_1505070204.tree.root
    availableFiles = [int(f[5:15]) for f in listdir(folderPath) if isfile(join(folderPath, f)) and f != '.DS_Store']
    availableFiles.sort()
    
    print len(availableFiles)
    
    runLog = []

    for index in range(0, len(metaData)):
        if int(metaData[index][4]) not in availableFiles:
            print "combinedNtuple(\"/eos/atlas/atlascerngroupdisk/det-hgtd/testbeam/September2017_A/RAW_oscilloscope/data_"+str(metaData[index][4])+".txt\");"

########## MAIN ANALYSIS ##########

########## MAIN ###########

main_debug()

##########################

