
import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import telescope_plot as tplot
import data_management as dm

#md.setupATLAS()
ROOT.gROOT.SetBatch(True)


def telescopeAnalysis(numberOfBatches):
    
    startTime = getTime()
    printTime()
    print "Start telescope analysis, " +str(numberOfBatches)+" batch(es).\n"

    dm.checkIfRepositoryOnStau()
    
    runLog_telescope = md.getRunLogForTelescopeAnalysis(numberOfBatches)
    data_batch = [np.empty(0), np.empty(0)]

    for row_number in range(0,len(runLog_telescope)): data_batch = telescopeAnalysisPerBatch(row_number, runLog_telescope, data_batch)
    print "\nDone analysing, time analysing: " + str(getTime()-startTime) + "\n"



def telescopeAnalysisPerBatch(row_number, runLog, data_batch):
    
    row = runLog[row_number]

    [telescope_data_batch, amplitudes_batch] = [i for i in data_batch]

    md.defineGlobalVariableRun(row)
    telescope_data_run = dm.importTelescopeData()
    amplitudes_run = dm.importPulseFile("amplitudes")
    amplitudes_run = amplitudes_run[0:len(telescope_data_run)]
    
    if telescope_data_batch.size == 0:
    
        print "Start analysing batch " + str(row[5]) + "...\n"
        telescope_data_batch = np.empty(0, dtype = telescope_data_run.dtype)
        amplitudes_batch = np.empty(0, dtype = amplitudes_run.dtype)
    

    if row[5] != runLog[row_number-1][5] and row_number > 0:
    
        print "All runs in batch " + str(runLog[row_number-1][5]) + " considered, producing plots...\n"
        
        md.defineGlobalVariableRun(runLog[row_number-1])
        tplot.produceTelescopeGraphs(telescope_data_batch, amplitudes_batch)
        
        md.defineGlobalVariableRun(runLog[row_number])

        printTime()
        print "Start analysing batch " + str(row[5]) + "...\n"
        telescope_data_batch = np.empty(0, dtype = telescope_data_run.dtype)
        amplitudes_batch = np.empty(0, dtype = amplitudes_run.dtype)


    # Last row
    if row[3] == runLog[-1][3]:
    
        printTime()
        print "All runs in batch " + str(row[5]) + " considered, producing plots...\n"
        
        telescope_data_batch = np.append(telescope_data_batch, telescope_data_run)
        amplitudes_batch = np.append(amplitudes_batch, amplitudes_run)
        
        tplot.produceTelescopeGraphs(telescope_data_batch, amplitudes_batch)

    else:
        
        telescope_data_batch = np.append(telescope_data_batch, telescope_data_run)
        amplitudes_batch = np.append(amplitudes_batch, amplitudes_run)
    
    
    return [telescope_data_batch, amplitudes_batch]


# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)

# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])

