import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md
import telescope_plot as tplot
import pulse as ps


ROOT.gROOT.SetBatch(True)


def telescopeAnalysis():

    md.defineDataFolderPath()
    
    numberOfRunsPerBatch = 2 # 12 runs in batch 301
    numberOfBatches = 2
    runLog = md.getRunsForTelescopeAnalysis(md.getRunLog())
   
    data_batch = ""
    amplitudes_batch = ""
    batchNumbers = md.getBatchNumbers(runLog, numberOfBatches)
    
    for batch in batchNumbers:
    
        print "Analysing batch " + str(batch) + " ...\n"
        runLog = md.getRunLogForBatch(runLog, batch)
        
        firstRunForBatch = True
        
        for row in runLog:
            
            md.defineGlobalVariableRun(row)
    
            if numberOfRunsPerBatch == 0:

                print "All runs in batch " + str(batch) + " considered, producing plots...\n"
                
                tplot.produceTelescopeGraphs(data_batch, amplitudes_batch, batch)
                
                break
        
            else:

                data_run = importTelescopeData()
                amplitudes_run = ps.importPulseInfo()
                
                if firstRunForBatch:
            
                    data_batch = np.empty(0, dtype=data_run.dtype)
                    amplitudes_batch = np.empty(0, dtype=amplitudes_run.dtype)
            
                    firstRunForBatch = False
                
                numberOfRunsPerBatch -= 1

            


    exit()


# Note, the file have only 200K entries
def importTelescopeData():
    
    dataFileName = md.getSourceFolderPath() + "forAntek/tracking"+str(md.getTimeStamp())+".root"
    data = rnm.root2array(dataFileName)
    
    # Convert into mm
    for dimension in data.dtype.names:
        data[dimension] = np.multiply(data[dimension], 0.001)
  
    return data



telescopeAnalysis()

