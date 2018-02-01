import ROOT
import numpy as np
import root_numpy as rnm

import pulse_calculations as p_calc
import pulse_plot as p_plot
import metadata as md
import data_management as dm

from pathos.multiprocessing import ProcessingPool as Pool

ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def pulseAnalysis():

    # Define sigma variable
    md.setSigma(5)

    dm.checkIfRepositoryOnStau()
    
    startTime = md.getTime()
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    print "\nStart PULSE analysis, batches:", md.batchNumbers

    for runLog in runLog_batch:
    
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers] # Restrict to some run numbers
    
        startTimeBatch = md.getTime()
        
        print "Analysing batch:", runLog[0][5], "with", len(runLog),"run files.\n"
      
        for index in range(0, len(runLog)):
            
            row = runLog[index]
            md.defineGlobalVariableRun(row)
            runNumber = md.getRunNumber()
            
            if (md.isRootFileAvailable()):
            
                md.printTime()
                print "Run", md.getRunNumber()
                [peak_values, peak_times, rise_times] = pulseAnalysisPerRun()
                
                # Export per run number
                dm.exportPulseData(peak_values, peak_times, rise_times)
                print "Done with run", md.getRunNumber(), "\n"
    

            print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-startTimeBatch)+"\n"

    print "Done with batch",runLog[0][5],".\n"


# Perform noise, pulse and telescope analysis
def pulseAnalysisPerRun():
    
    startTimeRun = md.getTime()
    
    # Configure inputs for multiprocessing
    p = Pool(dm.threads)
    max = md.getNumberOfEvents()
    step = 8000

    # Quick Analysis
    if md.maxEntries != 0:
        max = step = md.maxEntries

    ranges = range(0, max, step)
    
    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    # NOTE! Now pedestal and noise are event and channel dependent
    pedestal    = dm.importNoiseFile("pedestal")
    noise       = dm.importNoiseFile("noise")

    results = p.map(lambda chunk: multiProcess(dataPath, pedestal, noise, chunk, chunk+step), ranges)
    
    # results change form, now each element is a variable
    results_variables = p_calc.concatenateResults(results)

    return results_variables


# Start multiprocessing analysis of noises and pulses in ROOT considerOnlyRunsfile
def multiProcess(dataPath, pedestal, noise, begin, end):

    data = rnm.root2array(dataPath, start=begin, stop=end)
    peak_values, peak_times, rise_times = p_calc.pulseAnalysis(data, pedestal, noise)
    
    return peak_values, peak_times, rise_times




