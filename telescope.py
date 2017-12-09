
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

    for row in runLog:
        print row[3]
    
    md.defineGlobalVariableRun(runLog[0])
    
    telescope_data_batch = dm.importTelescopeDataBatch()

    amplitudes_batch = dm.importPulseFile("amplitudes")
    
    print "telescope data", len(telescope_data_batch)
    print "amplitude data", len(amplitudes_batch)
    
    if len(amplitudes_batch) == len(amplitudes_batch):
        tplot.produceTelescopeGraphs(telescope_data_batch, amplitudes_batch)
    else:
        print "Mismatch! Must be the same!"


# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)

# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])

