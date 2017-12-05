import ROOT
import root_numpy as rnm
import numpy as np

import pulse_calculations as p_calc
import pulse_plot as p_plot
import metadata as md
import data_management as dm

from pathos.multiprocessing import ProcessingPool as Pool

#md.setupATLAS()
ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def printWaveform(timeStamp, entry, channel):

    dm.checkIfRepositoryOnStau()

    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+timeStamp+".tree.root"

    data = rnm.root2array(dataPath, start=entry, stop=entry+1)

    graph = dict()



