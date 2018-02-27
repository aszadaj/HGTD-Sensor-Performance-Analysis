import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import data_management as dm
import timing_plot as t_plot
import timing_calculations as t_calc
import graph_double_peak as gdp


ROOT.gROOT.SetBatch(True)

# Start analysis of selected run numbers
def doublePeak():

    print "\nStart DOUBLE PEAK analysis, batches:", md.batchNumbers
    
    timeDiffRangesBatches = dict()
    
    # Selection based on smaller peaks for selected distributions
    ifSmallPeak = True
    timeDiffRangesBatches[108] = [["chan7", [0.76, 0.78]]]
#    timeDiffRangesBatches[306] = [["chan0", [-12.54, -12.52]], ["chan1", [-12.42, -12.4]], ["chan2", [-12.14, -12.12]], ]
#    timeDiffRangesBatches[507] = [["chan1", [-8.66, -8.64]], ["chan2", [-8.46, -8.44]], ["chan3", [-8.44, -8.42]]]

    # Selection based on larger peaks for selected distributions
#    ifSmallPeak = False
#    timeDiffRangesBatches[108] = [["chan7", [0.68, 0.7]]]
#    timeDiffRangesBatches[306] = [["chan0", [-12.44, -12.43]], ["chan1", [-12.34, -12.32]], ["chan2", [-12.05, -12.02]], ]
#    timeDiffRangesBatches[507] = [["chan1", [-8.58, -8.56]], ["chan2", [-8.38, -8.36]], ["chan3", [-8.36, -8.35]]]

    
    for batchNumber in md.batchNumbers:
        
        print "Batch", batchNumber,"\n"
        
        dm.checkIfRepositoryOnStau()
        
        time_difference = np.empty(0)
        peak_values = np.empty(0)
        peak_times = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers
    
        availableRunNumbersTiming = md.readFileNames("timing")

        for runNumber in runNumbers:
        
            if runNumber in availableRunNumbersTiming:
                md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
                
                print "Importing run", md.getRunNumber(), "\n"

                if time_difference.size == 0:
          
                    time_difference  = dm.importTimingFile()
                    peak_values = dm.importPulseFile("peak_value")
                    peak_times  = dm.importPulseFile("peak_time")
                    
                    # Select events and print them
                    
                    for info in timeDiffRangesBatches[batchNumber]:
                        
                        chan = info[0]
                        timeRanges = info[1]
                
                        events = np.argwhere((time_difference[chan] > timeRanges[0]) & (time_difference[chan] < timeRanges[1]))
                        np.random.shuffle(events)
                        events = events[:1]
                        
                        SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
                 
                        for index in range(0, len(events)):
                            event = events[index][0]
                            gdp.printWaveform(md.getRunNumber(), event, peak_times[chan][event], peak_times[SiPM_chan][event], peak_values[chan][event], chan, ifSmallPeak)

                else:
                    
                    time_difference_run = dm.importTimingFile()
                    peak_value_run = dm.importPulseFile("peak_value")
                    peak_times_run = dm.importPulseFile("peak_time")
                    

                    time_difference = np.concatenate((time_difference, time_difference_run ), axis = 0)
                    peak_values = np.concatenate((peak_values, peak_value_run ), axis = 0)
                    peak_times = np.concatenate((peak_times, peak_times_run), axis = 0)
                    
                    for info in timeDiffRangesBatches[batchNumber]:
                        
                        chan = info[0]
                        timeRanges = info[1]
                
                        events = np.argwhere((time_difference_run[chan] > timeRanges[0]) & (time_difference_run[chan] < timeRanges[1]))
                        np.random.shuffle(events)
                        events = events[:1]
                        
                        SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
                 
                        for index in range(0, len(events)):
                            event = events[index][0]
                            gdp.printWaveform(md.getRunNumber(), event, peak_times_run[chan][event], peak_times_run[SiPM_chan][event], peak_value_run[chan][event], chan, ifSmallPeak)
        
        
        if len(peak_times) != 0:
        
            print "Done with importing files for", batchNumber, "producing plots.\n"
            
            for info in timeDiffRangesBatches[batchNumber]:
                produceTimingDistributionPlots(time_difference, peak_values, peak_times, info[0], info[1], ifSmallPeak)

    print "Done with DOUBLE PEAK analysis.\n"


def produceTimingDistributionPlots(time_difference, peak_value, peak_time, channel, time_selections, ifSmallPeak):
    
    time_diff = dict()

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    
    channels = time_difference.dtype.names

    global canvas

    canvas = ROOT.TCanvas("Timing", "timing")
    
    channels = [channel]
    
    for chan in channels:
        if chan != SiPM_chan:
            
            index = int(chan[-1:])

            time_diff_mean_numpy = np.average(time_difference[chan][np.nonzero(time_difference[chan])])
            
            # Used for shifting the center of the distribution plots
            plot_shift = 0.7
            
            # Shift for gauss fit
            distribution_shift = 0.3
   
            # 1D PLOTS
            time_diff[chan] = ROOT.TH1D("Time Difference channel "+str(index), "time_difference" + chan, 1000, time_diff_mean_numpy-plot_shift, time_diff_mean_numpy+plot_shift)

    
            for entry in range(0, len(time_difference[chan])):
     
                
                if time_difference[chan][entry] != 0:
                    time_diff[chan].Fill(time_difference[chan][entry])
        
        
            maxHistogram = time_diff[chan].GetMaximum()
        
            time_diff_selection_1 = ROOT.TLine(time_selections[0],0,time_selections[0],maxHistogram)
            time_diff_selection_2 = ROOT.TLine(time_selections[1],0,time_selections[1],maxHistogram)
            
            time_diff_selection_1.SetLineColor(4)
            time_diff_selection_2.SetLineColor(4)
            
            lines = [time_diff_selection_1, time_diff_selection_2]
            

            # GAUSS FIT for TH1D
            time_diff[chan].Fit("gaus","","", time_diff_mean_numpy-distribution_shift, time_diff_mean_numpy+distribution_shift)
            
            textSmallOrLarge = "_large_peak"
            folderSmallOrLarge = "/large_peak"
            
            if ifSmallPeak:
                textSmallOrLarge = "_small_peak"
                folderSmallOrLarge = "/small_peak"
    
            # Print 1D plot time difference distribution
            headTitle = "Distribution of time difference in each event, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan))
            xAxisTitle = "\Delta t_{LGAD-SiPM} (ns)"
            yAxisTitle = "Number (N)"
            fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/double_peak/"+str(md.getNameOfSensor(channel))+folderSmallOrLarge+"/timing_distribution_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+textSmallOrLarge+".pdf"
            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
            exportTHPlot(time_diff[chan], titles, "", lines)




def exportTHPlot(graphList, titles, drawOption, lines):
 
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    graphList.Draw(drawOption)
    lines[0].Draw()
    lines[1].Draw()
    #graphList.Rebin(5)
    canvas.Update()
    canvas.Print(titles[3])
    canvas.Clear()

