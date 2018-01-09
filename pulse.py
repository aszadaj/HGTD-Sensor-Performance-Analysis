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
def pulseAnalysis(batchNumbers):

    sigma = 5

    dm.checkIfRepositoryOnStau()
    
    startTime = md.getTime()
    runLog_batch = md.getRunLogBatches(batchNumbers)
    print "\nStart pulse analysis, batches:", batchNumbers

    for runLog in runLog_batch:
    
        results_batch = []
        
        # DEBUG # Comment out this line to consider all files in batch
        runLog = runLog[0:2] # Restrict to some run numbers
    
        startTimeBatch = md.getTime()
        md.printTime()
        print "Analysing batch:", runLog[0][5], "with", len(runLog),"run files.\n"
      
        for index in range(0, len(runLog)):
            
            row = runLog[index]
            md.defineGlobalVariableRun(row)
            runNumber = md.getRunNumber()
            
            if (md.isRootFileAvailable(md.getTimeStamp())):
                
                print "Run", md.getRunNumber()
                [peak_values, peak_times, rise_times] = pulseAnalysisPerRun(sigma)
                results_batch.append([peak_values, peak_times, rise_times])
                
                # Export per run number
                dm.exportPulseData(peak_values, peak_times, rise_times)
                print "Done with run", md.getRunNumber(), "\n"
        
            else:
                print "WARNING! There is no root file for run number: " + str(runNumber) + "\n"
    
        # Done with the for loop and appending results, produce plots
        print "Done with batch", md.getBatchNumber(),"producing plots and exporting file.\n"
        
        peak_values = np.empty(0, dtype=results_batch[0][0].dtype)
        peak_times  = np.empty(0, dtype=results_batch[0][1].dtype)
        rise_times  = np.empty(0, dtype=results_batch[0][2].dtype)
    
        for results_run in results_batch:
            peak_values = np.concatenate((peak_values, results_run[0]), axis = 0)
            peak_times  = np.concatenate((peak_times,  results_run[1]), axis = 0)
            rise_times  = np.concatenate((rise_times,  results_run[2]), axis = 0)
     
        p_plot.producePulseDistributionPlots(peak_values, peak_times, rise_times)
    
        print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-startTimeBatch)+"\n"

    print "Done with batch",runLog[0][5],".\n"


# Perform noise, pulse and telescope analysis
def pulseAnalysisPerRun(sigma):
    
    startTimeRun = md.getTime()
    
    # Configure inputs for multiprocessing
    p = Pool(dm.threads)
    max = md.getNumberOfEvents()
    step = 8000

##    # DEBUG #
#    p = Pool(1)
#    max = 1000
#    step = 1000

    ranges = range(0, max, step)
    
    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    pedestal    = dm.importNoiseFile("pedestal")
    noise       = dm.importNoiseFile("noise")

    results = p.map(lambda chunk: multiProcess(dataPath, pedestal, noise, chunk, chunk+step, sigma), ranges)
    
    # results change form, now each element is a variable
    results_variables = p_calc.convertPulseData(results)

    return results_variables


# Start multiprocessing analysis of noises and pulses in ROOT considerOnlyRunsfile
def multiProcess(dataPath, pedestal, noise, begin, end, sigma):

    data = rnm.root2array(dataPath, start=begin, stop=end)
    peak_values, peak_times, rise_times = p_calc.pulseAnalysis(data, pedestal, noise, sigma)
    
    return peak_values, peak_times, rise_times




