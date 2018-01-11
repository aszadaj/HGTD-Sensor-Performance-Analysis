import ROOT
import numpy as np
import root_numpy as rnm
from datetime import datetime

import metadata as md
import data_management as dm
import timing_plot as t_plot


ROOT.gROOT.SetBatch(True)

# Start analysis of selected run numbers
def timingAnalysis(batchNumbers):

    dm.checkIfRepositoryOnStau()
    
    startTime = md.getTime()
    runLog_batch = md.getRunLogBatches(batchNumbers)
    print "\nStart timing analysis, batches:", batchNumbers

    for runLog in runLog_batch:
    
        #time_difference_batch = np.empty(0)
        ### NEW
        
        peak_time_batch = np.empty(0)
        peak_value_batch = np.empty(0)
      
        if md.limitRunNumbers != 0:
            runLog = runLog[0:md.limitRunNumbers]
    
        startTimeBatch = md.getTime()
        md.printTime()
        print "Analysing batch:", runLog[0][5], "with", len(runLog),"run files.\n"
      
        for index in range(0, len(runLog)):
            
            row = runLog[index]
            md.defineGlobalVariableRun(row)
            runNumber = md.getRunNumber()
            
            if (md.isTimingDataFilesAvailable()):
                
                print "Run", md.getRunNumber()
                peak_time_run = dm.importPulseFile("peak_time")
                peak_value_run = dm.importPulseFile("peak_value")
                
                #time_difference_run = timingAnalysisPerRun(peak_time_run, peak_value_run)
                
                if len(peak_time_batch) == 0:
                #if len(time_difference_batch) == 0:
                    #time_difference_batch = time_difference_batch.astype(time_difference_run.dtype)
                    
                    peak_time_batch = peak_time_batch.astype(peak_time_run.dtype)
                    peak_value_batch = peak_time_batch.astype(peak_value_run.dtype)
          
                # Export per run number
                
                #dm.exportTimingData(time_difference_run)
                
                # Concatenate to plot all results
                #time_difference_batch = np.concatenate((time_difference_batch, time_difference_run))
                
                # NEW
                peak_time_batch = np.concatenate((peak_time_batch, peak_time_run))
                peak_value_batch = np.concatenate((peak_value_batch, peak_value_run))
                
                print "Done with run", md.getRunNumber(), "\n"
        
            else:
                print "WARNING! There is no root file for run number: " + str(runNumber) + "\n"
    
        # Done with the for loop and appending results, produce plots
        print "Done with batch", md.getBatchNumber(),"producing plots and exporting file.\n"
        
#        if len(time_difference_batch) != 0:
#            t_plot.produceTimingDistributionPlots(time_difference_batch)

        if len(peak_time_batch) != 0:
            t_plot.produceTimingDistributionPlots(timingAnalysisPerRun(peak_time_batch, peak_value_batch), peak_value_batch)
    
        print "\nDone with final analysis and export. Time analysing: "+str(md.getTime()-startTimeBatch)+"\n"

    print "Done with batch",runLog[0][5],"\n"



def timingAnalysisPerRun(data, peak_value):

    times_2d = dict()
    time_diff_2d_lgad = dict()
    time_diff_2d_sipm = dict()
    canvas = dict()
    canvas_lgad = dict()
    canvas_sipm = dict()

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    W4RD01_chan = md.getChannelNameForSensor("W4-RD01")
    
    time_difference = np.zeros(len(data), dtype = data.dtype)
    
    channels = data.dtype.names
    channels = ["chan4"]

    for chan in channels:
    
        times_2d[chan] = ROOT.TH2F("telescope_"+chan,"Times channel "+str(int(chan[-1:])+1),500,-14,0,500,5,80)
        
        
        time_diff_2d_lgad[chan] = ROOT.TH2F("telescope_1"+chan,"Time difference, lgad channel "+str(int(chan[-1:])+1), 500,-18,3,500,-50,500)
        
        time_diff_2d_sipm[chan] = ROOT.TH2F("telescope_2"+chan,"Time diffence, sipm channel "+str(int(chan[-1:])+1),500,-18,3,500,-50,500)
        
        if chan != SiPM_chan:
        
            canvas[chan] = ROOT.TCanvas("Telescope"+chan, "telescope")
            canvas_lgad[chan] = ROOT.TCanvas("Telescope2"+chan, "telescope")
            canvas_sipm[chan] = ROOT.TCanvas("Telescope3"+chan, "telescope")
        
            for event in range (0, len(data)):
                
                # Here, this is adapted especially for 
                if data[chan][event] != 0 and data[SiPM_chan][event] != 0 and peak_value[chan][event] > 200:
#                if data[chan][event] != 0 and data[SiPM_chan][event] != 0 and peak_value[chan][event] > 200:

                    # Here calculate the time difference
                    time_difference[chan][event] = data[event][chan] - data[event][SiPM_chan]
                    
                    # Plot 2D plots
                    times_2d[chan].Fill(time_difference[chan][event], data[chan][event], 1)
                    
                    time_diff_2d_lgad[chan].Fill(time_difference[chan][event], peak_value[chan][event], 1)
               
                    time_diff_2d_sipm[chan].Fill(time_difference[chan][event], peak_value[SiPM_chan][event], 1)


            headTitle = "Time difference vs time position 2D plot "
            fileName = ".pdf"
            produceTH2Plot(times_2d[chan], headTitle, fileName, chan, canvas[chan], 1)
    
            headTitle = "Time difference LGAD 2d plot  "
            fileName = ".pdf"
            produceTH2Plot(time_diff_2d_sipm[chan], headTitle, fileName, chan, canvas_lgad[chan], 2)

            headTitle = "Time difference SIPM 2d plot "
            fileName = ".pdf"
            produceTH2Plot(time_diff_2d_lgad[chan], headTitle, fileName, chan, canvas_sipm[chan], 3)



    return time_difference


# Get actual time
def getTime():

    return datetime.now().replace(microsecond=0)


# Print time stamp
def printTime():

    time = str(datetime.now().time())
    print  "\nTime: " + str(time[:-7])


def produceTH2Plot(graph, headTitle, fileName, chan, canvas, num):

    title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan)) + "; " + "\Delta t_{LGAD-SIPM} (ns)" + "; " + "t_{SiPM} (ns)"

    if num == 2:
        title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan)) + "; " + "\Delta t_{LGAD-SIPM} (ns)" + "; " + "SiPM Amplitude (mV)"
    
    elif num == 3:
        title = headTitle + ", Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan)) + "; " + "\Delta t_{LGAD-SIPM} (ns)" + "; " + "LGAD Amplitude (mV)"

    graph.SetTitle(title)
    
    canvas.cd()
    graph.Draw("COLZ")
    canvas.Update()
    
    if num == 2:
        canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_2d_diff_sipm_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    elif num == 3:
        canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_2d_diff_lgad_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    else:
        canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_2d_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)

    #canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_2d_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    canvas.Clear()

