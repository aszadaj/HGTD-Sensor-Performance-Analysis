import ROOT
import root_numpy as rnm
import time
import numpy as np
import pickle

import pulse as ps
import noise as ns
import pulse_plot as p_plot
import noise_plot as n_plot
import metadata as md

from pathos.multiprocessing import ProcessingPool as Pool
from datetime import datetime

#setupATLAS()
ROOT.gROOT.SetBatch(True)

# When running on lxplus, remember to run 'setupATLAS' and after 'asetup --restore'

# Comment: There are files which do have only selected number of channels
# this should be taken care of. Another aspect is that the there is a possibility
# to restrict amount of entries depending on the file, can be setup in metadata if
# needed.

def main():

    numberOfRuns = 40 # 88 max
    threads = 4
    step = 10000
    max = "" # "" all entries
    sigma = 10
   
    startAnalysis(numberOfRuns, threads, step, sigma, max)
    
    exit()


########## MAIN ANALYSIS ##########

def startAnalysis(numberOfRuns, threads, step, sigma, max):
    
    totalNumberOfRuns = numberOfRuns
    startTime = getTime()
    
    print "\n"
    printTime()
    print "Start analysis, " + str(numberOfRuns) + " files."
    print "Threads: " + str(threads)
    print "Sigma: " + str(sigma)
    
    runLog = md.restrictToUndoneRuns(md.getRunLog())
    
    ps.defineSigmaConstant(sigma)
    
    for row in runLog:
    
        if numberOfRuns == 0:
            break
        
        md.defineGlobalVariableRun(row)
        runNumber = md.getRunNumber()
        
        if (md.isRootFileAvailable(md.getTimeStamp())):
            
            analyseDataForRunNumber(threads, step, max)
            
            printTime()
            print "Done with run " + str(runNumber) + ".\n"
            
        else:
        
            print "There is no root file for run number: " + str(runNumber)
        
        numberOfRuns -= 1


    print "\nFinished with analysis of " + str(totalNumberOfRuns) + " files."

    print "Time analysing: " + str(getTime() - startTime) +"\n"


# Perform noise, pulse and telescope analysis
def analyseDataForRunNumber(threads, step, max):
    
    startTime = getTime()
    
    # Start multiprocessing
    p = Pool(threads)
    max = md.getNumberOfEvents()
    max = 10000
    ranges = range(0, max, step)
    dataPath = "../../HGTD_material/oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    dataPath = "/Volumes/500 1/data_"+str(md.getTimeStamp())+".tree.root"
    
    printTime()
    print "Start analysing run number: " + str(md.getRunNumber()) + " with "+str(max)+" entries ...\n"
    
    results = p.map(lambda chunk: oscilloscopeAnalysis(dataPath,chunk,chunk+step),ranges)
    
    endTime = getTime()
    printTime()
    print "Done with multiprocessing. Time analysing: "+str(endTime-startTime)+"\n"
    
    print "Start with final analysis and exporting...\n"
    
    exportFilesAndPlots(getResultsFromMultiProcessing(results))
    
    print "\nDone with final analysis and export. Time analysing: "+str(getTime()-endTime)+"\n"



def oscilloscopeAnalysis(dataPath, begin, end):
    
    data = rnm.root2array(dataPath, start=begin, stop=end)
    
    noise_average, noise_std = ns.noiseAnalysis(data)
    amplitudes, rise_times = ps.pulseAnalysis(data, noise_average, noise_std)
    
    return noise_average, noise_std, amplitudes, rise_times



def getResultsFromMultiProcessing(results):

    noise_average = np.zeros(0, dtype=results[-1][0].dtype)
    noise_std = np.zeros(0, dtype=results[-1][0].dtype)
    amplitudes = np.zeros(0, dtype=results[-1][0].dtype)
    rise_times = np.zeros(0, dtype=results[-1][0].dtype)
    
    for i in range(0,len(results)):
        noise_average = np.append(noise_average, results[i][0])
        noise_std = np.append(noise_std, results[i][1])
        amplitudes = np.append(amplitudes, results[i][2])
        rise_times = np.append(rise_times, results[i][3])
    
    
    # Final analysis
    pedestal, noise = ns.getPedestalAndNoisePerChannel(noise_average, noise_std)

    return [noise_average, noise_std, amplitudes, rise_times, pedestal, noise]


# Note! The code first exports amplitude and noise values before producing plots.
def exportFilesAndPlots(results):

    # Export and produce distribution plots
    [noise_average, noise_std, amplitudes, rise_times, pedestal, noise] = [i for i in results]
    
    noise_average, noise_std, pedestal, noise, amplitudes, rise_times = convertData(noise_average, noise_std, pedestal, noise, amplitudes, rise_times)
    
    
    ns.exportNoiseInfo(pedestal, noise, noise_average, noise_std)
    ps.exportPulseData(amplitudes, rise_times)
    
    amplitudes, rise_times, criticalValues = ps.removeUnphyscialAmplitudes(amplitudes, rise_times, pedestal, noise)

    ps.exportCriticalValues(criticalValues)
    n_plot.produceNoiseDistributionPlots(noise_average, noise_std)
    p_plot.producePulseDistributionPlots(amplitudes, rise_times, pedestal)


# Convert to positive values in mV
def convertData(noise_average, noise_std, pedestal, noise, amplitudes, rise_times):
  
    channels = noise_average.dtype.names
  
    # Invert minus sign and change from V to mV
    for chan in channels:
    
        noise_average[chan] = np.multiply(noise_average[chan],-1000)
        noise_std[chan] = np.multiply(noise_std[chan],1000)
        pedestal[chan] *= -1000
        noise[chan] *= 1000
        amplitudes[chan] = np.multiply(amplitudes[chan],-1000)
    
    return noise_average, noise_std, pedestal, noise, amplitudes, rise_times


########## OTHER ##########

def printTime():

    time = str(datetime.now().time())
    print  "Time: " + str(time[:-7])

# Function for setting up ATLAS style plots
def setupATLAS():

    ROOT.gROOT.SetBatch()
    ROOT.gROOT.LoadMacro("./style/AtlasStyle.C")
    ROOT.SetAtlasStyle()


def getTime():

    return datetime.now().replace(microsecond=0)


########## MAIN ###########

main()

##########################

