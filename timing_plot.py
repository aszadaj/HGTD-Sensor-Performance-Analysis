import ROOT
import metadata as md
import numpy as np

import data_management as dm

ROOT.gStyle.SetOptFit()

def timingPlots():

    print "\nStart producing TIMING plots, batches:", md.batchNumbers
    
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
        
        numberOfEventPerRun = [0]
        
        for runNumber in runNumbers:
        
            if runNumber in availableRunNumbersTiming:
                md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
                
                print "Importing run", md.getRunNumber(), "\n"

                if time_difference.size == 0:
          
                    time_difference  = dm.importTimingFile()
                    peak_values = dm.importPulseFile("peak_value")
                    peak_times  = dm.importPulseFile("peak_time")
                
                else:

                    time_difference = np.concatenate((time_difference, dm.importTimingFile()), axis = 0)
                    peak_values = np.concatenate((peak_values, dm.importPulseFile("peak_value")), axis = 0)
                    peak_times = np.concatenate((peak_times, dm.importPulseFile("peak_time")), axis = 0)
                    
                # Since the values are concatenated, number of events are tracked
                
                numberOfEventPerRun.append(len(time_difference))
        
        if len(peak_times) != 0:
        
            print "Done with importing files for", batchNumber, "producing plots.\n"

            produceTimingDistributionPlots(time_difference, peak_values, peak_times, numberOfEventPerRun)

    print "Done with producing TIMING plots.\n"


def produceTimingDistributionPlots(time_difference, peak_value, peak_time, numberOfEventPerRun):
    
    time_diff = dict()
    time_diff_t_lgad = dict()
    time_diff_V_lgad = dict()
    time_diff_V_sipm = dict()
    time_diff_event_no = dict()

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    
    channels = time_difference.dtype.names
    
    #channels = ["chan5", "chan6", "chan7"]
    channels = ["chan1"]
    global canvas

    canvas = ROOT.TCanvas("Timing", "timing")
    
    for chan in channels:
        if chan != SiPM_chan:
            
            index = int(chan[-1:])

            time_diff_mean_numpy = np.average(time_difference[chan][np.nonzero(time_difference[chan])])
            
            # Used for shifting the center of the distribution plots
            plot_shift = 1.5
            
            # Shift for gauss fit
            distribution_shift = 2
   
            # 1D PLOTS
            time_diff[chan] = ROOT.TH1D("Time Difference channel "+str(index), "time_difference" + chan, 1000, time_diff_mean_numpy-plot_shift, time_diff_mean_numpy+plot_shift)
            
            # Automatized constants for plotting right event number (the results were earlier concatenated)
            maxNumber = 0
            
            for index in reversed(range(0, len(numberOfEventPerRun)-1)):
                if maxNumber < numberOfEventPerRun[index]-numberOfEventPerRun[index-1]:
                    maxNumber = numberOfEventPerRun[index]-numberOfEventPerRun[index-1]
        
            
            # 2D PLOTS
            time_diff_t_lgad[chan] = ROOT.TH2F("time_diff_t_lgad_"+chan,"Time difference vs peak time lgad, channel "+str(int(chan[-1:])+1),500,time_diff_mean_numpy-plot_shift,time_diff_mean_numpy+plot_shift,500,5,80)

            time_diff_V_lgad[chan] = ROOT.TH2F("time_diff_V_lgad_"+chan,"Time difference vs max amplitude lgad, channel "+str(int(chan[-1:])+1), 500,time_diff_mean_numpy-plot_shift,time_diff_mean_numpy+plot_shift,500,-50,500)
            
            time_diff_V_sipm[chan] = ROOT.TH2F("time_diff_V_sipm_"+chan,"Time difference vs max amplitude SiPM, channel "+str(int(chan[-1:])+1),500,time_diff_mean_numpy-plot_shift,time_diff_mean_numpy+plot_shift,500,-50,500)
            
            time_diff_event_no[chan] = ROOT.TH2F("time_diff_event_no_"+chan,"Time difference vs event no, channel "+str(int(chan[-1:])+1),100,time_diff_mean_numpy-plot_shift,time_diff_mean_numpy+plot_shift,100,0, maxNumber)
            
           
            entry_count = 0
    
            for entry in range(0, len(time_difference[chan])):
                
                # If statement to keep track of correct event number
                if entry+1 == numberOfEventPerRun[entry_count+1]:
                    entry_count += 1
                
                if time_difference[chan][entry] != 0:
                    time_diff[chan].Fill(time_difference[chan][entry])
                

                if peak_time[chan][entry] != 0 and peak_time[SiPM_chan][entry] != 0 and time_difference[chan][entry] != 0 and peak_value[chan][entry] < md.getPulseAmplitudeCut(chan) and peak_value[SiPM_chan][entry] < md.getPulseAmplitudeCut(SiPM_chan):
                    
                    # 2D plot time difference vs time peak in event
                    time_diff_t_lgad[chan].Fill(time_difference[chan][entry], peak_time[chan][entry], 1)

                    # 2D plot time difference, vs amplitude for LGAD
                    time_diff_V_lgad[chan].Fill(time_difference[chan][entry], peak_value[chan][entry]*-1000, 1)
                    
                    # 2D plot time difference vs amplitude for SiPM
                    time_diff_V_sipm[chan].Fill(time_difference[chan][entry], peak_value[SiPM_chan][entry]*-1000, 1)
             
                    # 2D plot time difference vs event number
                    time_diff_event_no[chan].Fill(time_difference[chan][entry], entry - numberOfEventPerRun[entry_count], 1)
            

            # GAUSS FIT for TH1D
            time_diff[chan].Fit("gaus","","", time_diff_mean_numpy-distribution_shift, time_diff_mean_numpy+distribution_shift)
            
    
            # Print 1D plot time difference distribution
            headTitle = "Distribution of time difference in each event, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan))
            xAxisTitle = "\Delta t_{LGAD-SiPM} (ns)"
            yAxisTitle = "Number (N)"
            fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_distribution/timing_distribution_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
            exportTHPlot(time_diff[chan], titles, "")


            # Print 2D plot time difference vs time peak in event
            headTitle = "Time difference vs peak time, Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan))
            xAxisTitle = "\Delta t_{LGAD-SIPM} (ns)"
            yAxisTitle = "t_{Peak, LGAD} (ns"
            fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_2d/timing_2d_"+str(md.getBatchNumber())+"_"+str(chan)  + "_"+str(md.getNameOfSensor(chan))+".pdf"
            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
            exportTHPlot(time_diff_t_lgad[chan], titles, "COLZ")
            
            
            # Print 2D plot time difference vs amplitude for LGAD
            headTitle = "Time difference vs peak value LGAD, Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan))
            xAxisTitle = "\Delta t_{LGAD-SiPM} (ns)"
            yAxisTitle = "LGAD Amplitude (mV)"
            fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_2d_diff_lgad/timing_2d_diff_lgad_"+str(md.getBatchNumber())+"_"+str(chan)  + "_"+str(md.getNameOfSensor(chan))+".pdf"
            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
            exportTHPlot(time_diff_V_lgad[chan], titles, "COLZ")
            
            
            # Print 2D plot time difference vs amplitude for SiPM
            headTitle = "Time difference vs peak value, SiPM Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan))
            xAxisTitle = "\Delta t_{LGAD-SiPM} (ns)"
            yAxisTitle = "SiPM Amplitude (mV)"
            fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_2d_diff_sipm/timing_2d_diff_sipm_"+str(md.getBatchNumber())+"_"+str(chan) + "_"+str(md.getNameOfSensor(chan))+".pdf"
            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
            exportTHPlot(time_diff_V_sipm[chan], titles, "COLZ")
            
            
            # Print 2D plot time difference vs event number
            headTitle = "Time difference vs entry number, Sep 2017 batch " + str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan))
            xAxisTitle = "\Delta t_{LGAD-SiPM} (ns)"
            yAxisTitle = "Event number"
            fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_2d_diff_event/timing_2d_diff_event_"+str(md.getBatchNumber())+"_"+str(chan) + "_"+str(md.getNameOfSensor(chan))+".pdf"
            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
            exportTHPlot(time_diff_event_no[chan], titles, "COLZ")


def exportTHPlot(graphList, titles, drawOption):
 
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    graphList.Draw(drawOption)
    canvas.Update()
    canvas.Print(titles[3])
    canvas.Clear()

