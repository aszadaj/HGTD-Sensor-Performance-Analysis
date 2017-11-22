
import ROOT
import numpy as np
import root_numpy as rnm
import pickle
import metadata as md
import telescope_plot as tplot
import pulse as ps


ROOT.gROOT.SetBatch(True)


def main():
    
    numberOfRuns = 1
    runLog, runs = md.getRunsForTelescopeAnalysis(md.getRunLog())
    
    for row in runLog:
        md.defineGlobalVariableRun(row)
        
        telescopeAnalysis()
        
        numberOfRuns -= 1
        
        #if numberOfRuns == 0 break
    
    exit()


def telescopeAnalysis():

    amplitudes, rise_times, criticalValues = ps.importPulseInfo()
    data = importTelescopeData()
    tplot.produceTelescopeGraphs(data, amplitudes)


# Note, the file have only 200K entries
def importTelescopeData():
  
    dataFileName = "../../HGTD_material/forAntek/tracking"+str(md.getTimeStamp())+".root"
    # Define the batch here
    data = rnm.root2array(dataFileName)
    
    # Convert into mm
    for dimension in data.dtype.names:
        data[dimension] = np.multiply(data[dimension], 0.001)
  
    return data


##########################################
#                                        #
#                                        #
#               MAIN()                   #
#                                        #
#                                        #
##########################################

main()

