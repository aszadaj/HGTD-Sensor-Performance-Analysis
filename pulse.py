import ROOT
import root_numpy as rnm
import numpy as np

import pulse_calculations as p_calc
import pulse_plot as p_plot
import metadata as md
import data_management as dm

from pathos.multiprocessing import ProcessingPool as Pool

#md.setupATLAS()
ROOT.gROOT.SetBatch(True)


# Start analysis of selected run numbers
def pulseAnalysis(numberOfRuns, step, sigma):
    
    p_calc.defineSigmaConstant(sigma)
    dm.checkIfRepositoryOnStau()
    totalNumberOfRuns = numberOfRuns
    startTime = md.getTime()
    
    print "\n"
    md.printTime()
    print "\nStart pulse analysis, " + str(numberOfRuns) + " file(s)."
    print "Sigma: " + str(p_calc.getSigmaConstant()) + "\n"
   
    runLog = md.restrictToUndoneRuns(md.getRunLog(), "pulse")
 
 
    for row in runLog:
    
        md.defineGlobalVariableRun(row)
        runNumber = md.getRunNumber()
        
        if (md.isRootFileAvailable(md.getTimeStamp())):
            
            results = pulseAnalysisPerRun(step)
            md.printTime()
            print "Done with run " + str(runNumber) + ".\n"
    
        else:
            print "There is no root file for run number: " + str(runNumber) + "\n"
        
        numberOfRuns -= 1
        
        if numberOfRuns == 0:
        
            print "\nFinished with analysis of " + str(totalNumberOfRuns) + " files."
            print "Time analysing: " + str(md.getTime() - startTime) +"\n"
            break

    if not runLog:
        print "All files are already converted. Remove first pickle file from: \n/Users/aszadaj/cernbox/SH203X/HGTD_material/data_hgtd_efficiency_sep_2017/pulse_files/pulse_amplitudes"

        
# Perform noise, pulse and telescope analysis
def pulseAnalysisPerRun(step):
    
    startTimeRun = md.getTime()
    
    p = Pool(dm.threads) #Change
    max = md.getNumberOfEvents()
    ranges = range(0, max, step)

    md.printTime()
    print "Start analysing run number: " + str(md.getRunNumber()) + " with "+str(max)+ " events ...\n"
    
    dataPath = md.getSourceFolderPath() + "oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    pedestal    = dm.importNoiseFile("pedestal")
    noise       = dm.importNoiseFile("noise")
    
    results = p.map(lambda chunk: multiProcess(dataPath, pedestal, noise, chunk, chunk+step), ranges)

    endTime = md.getTime()
    
    md.printTime()
    print "Done with multiprocessing. Time analysing: "+str(endTime-startTimeRun)+"\n"
    print "Start with final analysis and exporting...\n"
 
    # Note, here the function receives the results from multiprocessing
    results = p_calc.removeUnphyscialQuantities(results, noise)

    return results
    
#
#    [amplitudes, rise_times, peak_times, criticalValues] = [i for i in results]
#
#    dm.exportPulseData(amplitudes, rise_times, peak_times, criticalValues)
#    p_plot.producePulseDistributionPlots(amplitudes, rise_times)
#
#    print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-endTime)+"\n"


# Start multiprocessing analysis of noises and pulses in ROOT considerOnlyRunsfile
def multiProcess(dataPath, pedestal, noise, begin, end):
    
    data = rnm.root2array(dataPath, start=begin, stop=end)
    amplitudes, rise_times, peak_times = p_calc.pulseAnalysis(data, pedestal, noise)
    
    return amplitudes, rise_times, peak_times


