import ROOT
import root_numpy as rnm
import numpy as np

import pulse_calculations as p_calc
import metadata as md
import data_management as dm

from pathos.multiprocessing import ProcessingPool as Pool

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def pulseAnalysis():

    dm.checkIfRepositoryOnStau()
    startTime = md.dm.getTime()
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    
    print "\nStart PULSE analysis, batches:", md.batchNumbers
    
    for runLog in runLog_batch:
    
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers] # Restrict to some run numbers
    
        startTimeBatch = md.dm.getTime()
        dm.getTime()
    
        print "Batch:", runLog[0][5], len(runLog), "run files.\n"
      
        for index in range(0, len(runLog)):
        
            md.defineGlobalVariableRun(runLog[index])
            
            print "Run", md.getRunNumber()
            
            [peak_time, peak_value, rise_time, cfd05, point_count] = pulseAnalysisPerRun()
            dm.exportPulseData(peak_time, peak_value, rise_time, cfd05, point_count)
                        
            print "Done with run", md.getRunNumber(), "\n"

        print "Done with batch", runLog[0][5], "Time analysing: "+str(md.dm.getTime()-startTimeBatch)+"\n"

    print "Done with PULSE analysis. Time analysing: "+str(md.dm.getTime()-startTime)+"\n"


# Perform noise, pulse and telescope analysis
def pulseAnalysisPerRun():
    
    # Configure inputs for multiprocessing
    max = md.getNumberOfEvents()
    step = 10000

    # Quick Analysis
    if md.maxEntries != 0:
        max = step = md.maxEntries
        dm.setNumberOfThreads(1)
    
    p = Pool(dm.threads)
    ranges = range(0, max, step)
    
    dataPath = dm.getDataPath()
    pedestal = dm.importNoiseFile("pedestal")
    noise     = dm.importNoiseFile("noise")
    results = p.map(lambda chunk: multiProcess(dataPath, pedestal, noise, chunk, chunk+step), ranges)
    
    # results change form, now each element is a variable
    results_variables = p_calc.concatenateResults(results)

    return results_variables


# Multiprocessing
def multiProcess(dataPath, pedestal, noise, begin, end):

    data = rnm.root2array(dataPath, start=begin, stop=end)
    
    return p_calc.pulseAnalysis(data, pedestal, noise)




