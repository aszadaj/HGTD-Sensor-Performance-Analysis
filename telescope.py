
import ROOT
import numpy as np
import root_numpy as rnm
import pickle
import metadata as md
import telescope_plot as tplot

ROOT.gROOT.SetBatch(True)

def main():
    #setupATLAS()
    
    numberOfRuns = 1
    runLog, runs = md.getRunsForTelescopeAnalysis(md.getRunLog())

    for row in runLog:
        md.defineGlobalVariableRun(row)
        telescopeAnalysis()
        numberOfRuns -= 1
        if numberOfRuns == 0:
            break
    exit()


def telescopeAnalysis():

    amplitudes, rise_times, criticalValues = importPulseInfo()
    data = importTelescopeData()
    tplot.produceTelescopeGraphs(data, amplitudes)


# Import dictionaries amplitude and risetime with channel names from a .pkl file
def importPulseInfo():

    # Note: amplitude values are corrected with a pedestal (from the noise analysis) and the critical values are not
    with open("pickle_files/pulse_files/pulse_data_"+str(md.getRunNumber())+".pkl","rb") as input:
        
        amplitude = pickle.load(input)
        risetime = pickle.load(input)
    
    with open("pickle_files/pulse_files/pulse_critical_values_"+str(md.getRunNumber())+".pkl","rb") as input:
    
        criticalValues = pickle.load(input)


    return amplitude, risetime, criticalValues
    

# Generates which runs are considered located in runlist.csv with corresponding time stamps.

# Function for setting up ATLAS style plots
def setupATLAS():

    ROOT.gROOT.SetBatch()
    ROOT.gROOT.LoadMacro("resources/style/AtlasStyle.C")
    ROOT.SetAtlasStyle()



# Note, the file have only 200K entries
def importTelescopeData():
  
    dataFileName = "../../HGTD_material/telescope_data_sep_2017/tracking"+str(md.getTimeStamp())+".root"
    data = rnm.root2array(dataFileName)
    
    # Convert into mm
    for dimension in data.dtype.names:
        data[dimension] = np.multiply(data[dimension], 0.001)
  
    return data, dataFileName


##########################################
#                                        #
#                                        #
#               MAIN()                   #
#                                        #
#                                        #
##########################################

main()

