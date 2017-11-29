import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import telescope_plot as tplot
import pulse as ps


ROOT.gROOT.SetBatch(True)

# Log: there is a problem when the code runs again through the same batch.


def telescopeAnalysis(numberOfRunsPerBatch, numberOfBatches):
    startTime = getTime()
    printTime()
    print "Start telescope analysis, " +str(numberOfBatches)+" batch(es), " + str(numberOfRunsPerBatch) + " run(s) per batch.\n"

    md.defineDataFolderPath()
    
    runLog_telescope = md.getRunLogForTelescopeAnalysis(md.getRunLog(), numberOfBatches, numberOfRunsPerBatch)
    
    currentBatch = int(runLog_telescope[0][5])
    last_row = runLog_telescope[-1][3]
    data_batch = [np.empty(0), np.empty(0), currentBatch]
    
    for row in runLog_telescope:
        data_batch = telescopeAnalysisPerBatch(row, last_row, data_batch)

    print "\nDone analysing, time analysing: " + str(getTime()-startTime) + "\n"
    exit()


def telescopeAnalysisPerBatch(row, last_row, data_batch):

    [telescope_data_batch, amplitudes_batch, currentBatch] = [i for i in data_batch]

    md.defineGlobalVariableRun(row)
   
    telescope_data_run = importTelescopeData()
    amplitudes_run = ps.importPulseInfo()
    
    if telescope_data_batch.size == 0:
    
        print "Start analysing batch " + str(currentBatch) + "\n"
        telescope_data_batch = np.empty(0, dtype = telescope_data_run.dtype)
        amplitudes_batch = np.empty(0, dtype = amplitudes_run.dtype)


    if currentBatch != md.getBatchNumber():

        print "All runs in batch " + str(currentBatch) + " considered, producing plots...\n"
        
        tplot.produceTelescopeGraphs(telescope_data_batch, amplitudes_batch, currentBatch)
        
        currentBatch = md.getBatchNumber()
        
        printTime()
        print "Start analysing batch " + str(currentBatch) + "\n"
        
        telescope_data_batch = np.empty(0, dtype = telescope_data_run.dtype)
        amplitudes_batch = np.empty(0, dtype = amplitudes_run.dtype)
        
        telescope_data_batch = np.append(telescope_data_batch, telescope_data_run)
        amplitudes_batch = np.append(amplitudes_batch, amplitudes_run)
        
        if row[3] == last_row:
            
            printTime()
            print "All runs in batch " + str(currentBatch) + " considered, producing plots...\n"
            
            tplot.produceTelescopeGraphs(telescope_data_batch, amplitudes_batch, currentBatch)
    
    else:
        telescope_data_batch = np.append(telescope_data_batch, telescope_data_run)
        amplitudes_batch = np.append(amplitudes_batch, amplitudes_run)

    return [telescope_data_batch, amplitudes_batch, currentBatch]

# Note, the file have only 200K entries
def importTelescopeData():
    
    dataFileName = md.getSourceFolderPath() + "forAntek/tracking"+str(md.getTimeStamp())+".root"
    data = rnm.root2array(dataFileName)
    
    # Convert into mm
    for dimension in data.dtype.names:
        data[dimension] = np.multiply(data[dimension], 0.001)
  
    return data


# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)

# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])


