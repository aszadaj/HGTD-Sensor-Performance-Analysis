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


def main():

    numberOfRuns = 10
    threads = 4
    step = 10000
    max = ""
    sigma = 10
   
    startAnalysis(numberOfRuns, threads, step, sigma, max)
    
    exit()


########## MAIN ANALYSIS ##########

def startAnalysis(numberOfRuns, threads, step, sigma, max):

    runLog = md.restrictToUndoneRuns(md.getRunLog())
    ps.defineSigmaConstant(sigma)
    #runLog_telescope, runList = md.getRunsForTelescopeAnalysis(runLog)
    
    for row in runLog:
    
        if numberOfRuns == 0:
            break
        
        md.defineGlobalVariableRun(row)
        runNumber = md.getRunNumber()
        
        if (md.isRootFileAvailable(md.getTimeStamp())):
        
            print "Run number: " + str(runNumber)
            analyseDataForRunNumber(threads, step, max)
            
            print "\nDone with run " + str(runNumber) + ".\n"
            
        else:
        
            print "There is no root file for run number: " + str(runNumber)
        
        numberOfRuns -= 1


# Perform noise, pulse and telescope analysis
def analyseDataForRunNumber(threads, step, max):
    
    # Start multiprocessing
    p = Pool(threads)
    max = md.getNumberOfEvents() if max=="" else max
    ranges = range(0, max, step)
    dataPath = "../../HGTD_material/oscilloscope_data_sep_2017/data_"+str(md.getTimeStamp())+".tree.root"
    
    printTime()
    print "Threads: " + str(threads) + "\n"
    print "Entries: " + str(max) + "\n"
    print "\nStart multiprocessing... \n"
    
    results = p.map(lambda chunk: oscilloscopeAnalysis(dataPath,chunk,chunk+step),ranges)
    #results = p.apply_async(lambda chunk: oscilloscopeAnalysis(dataPath,chunk,chunk+step),ranges)
    
    printTime()
    print "\nDone with multiprocessing \n"
    exportFilesAndPlots(getResultsFromMultiProcessing(results))



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
    
    
    # Some final analysis
    pedestal, noise = ns.getPedestalAndNoisePerChannel(noise_average, noise_std)

    amplitudes, rise_times, criticalValues = ps.removeUnphyscialAmplitudes(amplitudes, rise_times, pedestal, noise)
    
    printTime()
    print "Done with final analysis. \n"

    return [noise_average, noise_std, amplitudes, rise_times, pedestal, noise, criticalValues]


def exportFilesAndPlots(results):
    # Export and produce distribution plots
    [noise_average, noise_std, amplitudes, rise_times, pedestal, noise, criticalValues] = [i for i in results]
    
    noise_average, noise_std, pedestal, noise, amplitudes, rise_times, criticalValues = convertData(noise_average, noise_std, pedestal, noise, amplitudes, rise_times, criticalValues)


    ns.exportNoiseInfo(pedestal, noise, noise_average, noise_std)
    ns.produceNoiseDistributionPlots(noise_average, noise_std)

    ps.exportPulseInfo(amplitudes, rise_times, criticalValues)
    p_plot.producePulseDistributionPlots(amplitudes, rise_times, pedestal)

    printTime()
    print "Done with export data and plots. \n"


# Convert to positive values in mV
def convertData(noise_average, noise_std, pedestal, noise, amplitudes, rise_times, criticalValues):
  
    channels = noise_average.dtype.names
  
    # Invert minus sign and change from V to mV
    for chan in channels:
    
        noise_average[chan] = np.multiply(noise_average[chan],-1000)
        noise_std[chan] = np.multiply(noise_std[chan],1000)
        pedestal[chan] *= -1000
        noise[chan] *= 1000
        amplitudes[chan] = np.multiply(amplitudes[chan],-1000)
        criticalValues[chan] *= -1000
    
    return noise_average, noise_std, pedestal, noise, amplitudes, rise_times, criticalValues


########## OTHER ##########

def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])

# Function for setting up ATLAS style plots
def setupATLAS():

    ROOT.gROOT.SetBatch()
    ROOT.gROOT.LoadMacro("./style/AtlasStyle.C")
    ROOT.SetAtlasStyle()


########## MAIN ###########

main()

##########################

