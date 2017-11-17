
import ROOT
import numpy as np
import root_numpy as rnm
import pickle
import pandas as pd

from telescope_plot import *


def telescopeAnalysisPerFile(data, runNumber, timeStamp, sensors):
    print "\nDone with pulse analysis. Start telescope analysis.\n"
    
    amplitude, risetime, small_amplitude, criticalValues = importPulseInfo(runNumber, len(data))

    produceTelescopeGraphs(data, amplitude, runNumber, sensors)


# Import dictionaries amplitude and risetime with channel names from a .pkl file
def importPulseInfo(runNumber, length_telescope_file):

    # Note: amplitude values are corrected with a pedestal (from the noise analysis) and the critical values are not
    with open("/Users/aszadaj/cernbox/SH203X/Gitlab/HGTD-Efficiency-analysis/resources/pulse_info_"+str(runNumber)+".pkl","rb") as input:
        
        amplitude = pickle.load(input)
        risetime = pickle.load(input)
        small_amplitude = pickle.load(input)
        criticalValues = pickle.load(input)


    return amplitude, risetime, small_amplitude, criticalValues
    

# Generates which runs are considered located in runlist.csv with corresponding time stamps.

#####################RunLog-Table1
#
# Replace the file in HG Material which comes from run log. Import .csv file
# /Users/aszadaj/cernbox/SH203X/HGTD_material/runlist_HGTD_September_2017/tb_sep17_run_log/RunLog-Table1.csv
#
###############


##########################################
#                                        #
#                                        #
#               MAIN()                   #
#                                        #
#                                        #
##########################################

#main()

