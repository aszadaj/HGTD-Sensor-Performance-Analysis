
import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import telescope_plot as tplot
import data_management as dm

#md.setupATLAS()

ROOT.gROOT.SetBatch(True)


def telescopeAnalysis(batchNumbers):
    
    startTime = getTime()
    printTime()

    print "Start telescope analysis, batch",batchNumbers[0],"\n"

    dm.checkIfRepositoryOnStau()
   
    runLogs = md.getRunLogBatches(batchNumbers)
    
    for runLog in runLogs:
        telescopeAnalysisPerBatch(runLog)

    print "\nDone analysing, time analysing: " + str(getTime()-startTime) + "\n"


def telescopeAnalysisPerBatch(runLog):
    
    md.defineGlobalVariableRun(runLog[0])
    
    telescope_data_batch, peak_value_batch = dm.importFilesForTracking()
    
    if len(telescope_data_batch) == len(peak_value_batch):
        tplot.produceTelescopeGraphs(telescope_data_batch, peak_value_batch)

    else:
        print "This should not occur, check importFilesForTracking()"


# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)

# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])

