
import ROOT
import numpy as np
import root_numpy as rnm
import pickle
import pandas as pd

from telescope_plot import *


##########################################
#                                        #
#                                        #
#             MAIN FUNCTION              #
#                                        #
#                                        #
##########################################


def main():

    runInfo = getRunInfo()
    selectedRuns = [3656]
    runInfo = selectRuns(runInfo, selectedRuns)
    
    for runNumber in runInfo.keys():
        analyseTelescopeDataForRunNumber(runNumber, runInfo[runNumber])

    exit()


##########################################
#                                        #
#                                        #
#              FUNCTIONS                 #
#                                        #
#                                        #
##########################################

#   For future notice, the max and min values for each dimension in the telescope data
#   xMin -5092.44
#   xMax 7053.56
#
#   yMin 6046.8
#   yMax 15174.8


def analyseTelescopeDataForRunNumber(runNumber, timeStamp):
    
    print "Import telescope data"
    data_telescope = importTelescopeData(timeStamp)
    print "Import pulse properties"
    amplitude, risetime, small_amplitude, criticalValues = importPulseInfo(runNumber, len(data_telescope))
    
    for chan in amplitude.dtype.names:
        print np.count_nonzero(amplitude[chan])

    produceTelescopeGraphs(amplitude, data_telescope, runNumber)


# Note, the file have only 200K entries
def importTelescopeData(timeStamp):
  
    dataFileName = "~/cernbox/SH203X/HGTD_material/telescope_data_sep_2017/tracking"+str(timeStamp)+".root"
    data = rnm.root2array(dataFileName)
  
    return data


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
def getRunInfo():
    
    fileName = "~/cernbox/SH203X/HGTD_material/oscilloscope_data_sep_2017/runlist.csv"
    df = pd.read_csv(fileName, header=None, sep="\t")
    
    runInfo = dict()
    
    for index in range(0,len(df)):
        runInfo[df.iloc[index,0]] = df.iloc[index,1]
   
    return runInfo


# Choose run numbers with corresponding time stamp to be run
def selectRuns(runInfo, selectedRuns):

    selectedRunInfo = dict()

    for key in selectedRuns:
        selectedRunInfo[key] = runInfo[key]

    return selectedRunInfo



##########################################
#                                        #
#                                        #
#               MAIN()                   #
#                                        #
#                                        #
##########################################

main()

