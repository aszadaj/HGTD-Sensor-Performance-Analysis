import ROOT
import root_numpy as rnm
import numpy as np

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
        
        runLog = [runLog[0], runLog[1]] # restrict to two files
    
        startTimeBatch = md.getTime()
        md.printTime()
        print "Analysing batch:", runLog[0][5], "with", len(runLog),"run files.\n"
      
        for index in range(0, len(runLog)):
            
            row = runLog[index]
            md.defineGlobalVariableRun(row)
            runNumber = md.getRunNumber()
            
            if (md.isRootFileAvailable(md.getTimeStamp())):
                
                print "Run", md.getRunNumber()
                results_batch.append(pulseAnalysisPerRun(sigma))
                print "Done with run", md.getRunNumber(),"\n"
        
            else:
                print "WARNING! There is no root file for run number: " + str(runNumber) + "\n"
    
        # Done with the for loop and appending results, export and produce files
        
        print "Done with batch", md.getBatchNumber(),"producing plots and exporting file.\n"
        
        amplitudes = np.empty(0, dtype=results_batch[0][0].dtype)
        rise_times = np.empty(0, dtype=results_batch[0][1].dtype)
        half_max_times = np.empty(0, dtype=results_batch[0][2].dtype)
        criticalValues = np.empty(0, dtype=results_batch[0][3].dtype) # This should be length 1 per channel!
        pulse_points = np.empty(0, dtype=results_batch[0][4].dtype)
        deleted_amplitudes = np.zeros(1, dtype=results_batch[0][5].dtype) # This should be length 1 per channel!
    
        for results in results_batch:
            amplitudes = np.concatenate((amplitudes, results[0]), axis = 0)
            rise_times = np.concatenate((rise_times, results[1]), axis = 0)
            half_max_times = np.concatenate((half_max_times, results[2]), axis = 0)
            criticalValues = np.concatenate((criticalValues, results[3]), axis = 0)
            pulse_points = np.concatenate((pulse_points, results[4]), axis = 0)
            
            for chan in amplitudes.dtype.names:
                deleted_amplitudes[chan] += results[5][chan]

        for chan in criticalValues.dtype.names:
        
            criticalValues[chan] = np.amax(criticalValues[chan])
            deleted_amplitudes[chan] = float(deleted_amplitudes[chan])/float(len(amplitudes[chan]))
        
        dm.exportPulseData(amplitudes, rise_times, half_max_times, criticalValues, pulse_points)

        p_plot.producePulseDistributionPlots(amplitudes, rise_times, pulse_points, deleted_amplitudes)
    
        print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-startTimeBatch)+"\n"

    print "Done with batch",runLog[0][5],".\n"

# Perform noise, pulse and telescope analysis
def pulseAnalysisPerRun(sigma):
    
    startTimeRun = md.getTime()
    
    # Configure inputs for multiprocessing
    p = Pool(dm.threads) #dm.threads
    #max = md.getNumberOfEvents()
    max = 20000 # This is adapted to match the number of telescope files
    #max = 5000
    step = 5000
    ranges = range(0, max, step)
    
    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    pedestal    = dm.importNoiseFile("pedestal")
    noise       = dm.importNoiseFile("noise")
    
    results = p.map(lambda chunk: multiProcess(dataPath, pedestal, noise, chunk, chunk+step, sigma), ranges)
 
    # Note, here the function receives the results from multiprocessing
    results = p_calc.removeUnphyscialQuantities(results, noise, sigma)
    
    return results


# Start multiprocessing analysis of noises and pulses in ROOT considerOnlyRunsfile
def multiProcess(dataPath, pedestal, noise, begin, end, sigma):
    
    data = rnm.root2array(dataPath, start=begin, stop=end)
    amplitudes, rise_times, half_max_times, pulse_points = p_calc.pulseAnalysis(data, pedestal, noise, sigma)
    
    return amplitudes, rise_times, half_max_times, pulse_points




