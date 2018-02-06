import ROOT
import metadata as md
import numpy as np

import data_management as dm

ROOT.gStyle.SetOptFit()

def timingPlots():

    print "Start producing TIMING plots... \n"
    
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

                else:

                    time_difference = np.concatenate((time_difference, dm.importTimingFile()), axis = 0)
                    peak_values = np.concatenate((peak_values, dm.importPulseFile("peak_value")), axis = 0)
                    peak_times = np.concatenate((peak_times, dm.importPulseFile("peak_time")), axis = 0)
        
        if len(peak_times) != 0:
        
            print "Done with importing files for", batchNumber, "producing plots.\n"

            produceTimingDistributionPlots(time_difference, peak_values, peak_times)

    print "Done with producing TIMING plots.\n"


def produceTimingDistributionPlots(time_difference, peak_value, peak_time):
    
    time_difference_graph = dict()
    times_2d = dict()
    time_diff_2d_lgad = dict()
    time_diff_2d_sipm = dict()
    
    canvas = dict()
    canvas_lgad = dict()
    canvas_sipm = dict()
    
    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    
    channels = time_difference.dtype.names
    
    for chan in channels:
        if chan != SiPM_chan:
            
            index = int(chan[-1:])
            
            constant_sigma = 2
            
            timing_mean = np.average(time_difference[chan][np.nonzero(time_difference[chan])])
            
            timing_std = np.std(time_difference[chan][np.nonzero(time_difference[chan])])
            
            timing_min = timing_mean - constant_sigma * timing_std
            
            timing_max = timing_mean + constant_sigma * timing_std
            

            time_difference_graph[chan] = ROOT.TH1D("Time Difference channel "+str(index), "time_difference" + chan, 1000, timing_min, timing_max)
            
            times_2d[chan] = ROOT.TH2F("tracking_"+chan,"Times channel "+str(int(chan[-1:])+1),500,-14,0,500,5,80)

            time_diff_2d_lgad[chan] = ROOT.TH2F("tracking_1"+chan,"Time difference, lgad channel "+str(int(chan[-1:])+1), 500,-18,3,500,-50,500)
            
            time_diff_2d_sipm[chan] = ROOT.TH2F("tracking_2"+chan,"Time diffence, sipm channel "+str(int(chan[-1:])+1),500,-18,3,500,-50,500)
            
            canvas[chan] = ROOT.TCanvas("Tracking "+chan, "tracking")
            canvas_lgad[chan] = ROOT.TCanvas("Tracking 2 "+chan, "tracking2")
            canvas_sipm[chan] = ROOT.TCanvas("Tracking 3 "+chan, "tracking3")

            for entry in range(0, len(time_difference[chan])):

                if time_difference[chan][entry] != 0:
                    
                    time_difference_graph[chan].Fill(time_difference[chan][entry])
                

                if peak_time[chan][entry] != 0 and peak_time[SiPM_chan][entry] != 0:
                    
                    times_2d[chan].Fill(time_difference[chan][entry], peak_time[chan][entry], 1)
                    
                    time_diff_2d_lgad[chan].Fill(time_difference[chan][entry], peak_value[chan][entry]*-1000, 1)
               
                    time_diff_2d_sipm[chan].Fill(time_difference[chan][entry], peak_value[SiPM_chan][entry]*-1000, 1)

            constant_sigma = 1

            timing_min = timing_mean - constant_sigma * timing_std
    
            timing_max = timing_mean + constant_sigma * timing_std


            time_difference_graph[chan].Fit("gaus","","", timing_min, timing_max)
    
    
            produceTH1Plot(time_difference_graph[chan], canvas[chan], chan)

            headTitle = "Time difference vs time position 2D plot "
            fileName = ".pdf"
            produceTH2Plot(times_2d[chan], headTitle, fileName, chan, canvas[chan], 1)
    
            headTitle = "Time difference LGAD 2d plot "
            fileName = ".pdf"
            produceTH2Plot(time_diff_2d_sipm[chan], headTitle, fileName, chan, canvas_lgad[chan], 2)

            headTitle = "Time difference SIPM 2d plot "
            fileName = ".pdf"
            produceTH2Plot(time_diff_2d_lgad[chan], headTitle, fileName, chan, canvas_sipm[chan], 3)


# Produce TH1 plots and export them as a PDF file
def produceTH1Plot(graphList, canvas, chan):

    headTitle = "Distribution of time difference in each event, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan))
    xAxisTitle = "\Delta t_{LGAD-SiPM}"
    yAxisTitle = "Number (N)"
    fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_distribution/timing_distribution_"+str(md.getBatchNumber())+"_"+chan+".pdf"


    graphList.SetLineColor(1)
    graphList.SetMarkerColor(1)
    graphList.GetYaxis().SetTitle(yAxisTitle)
    graphList.GetXaxis().SetTitle(xAxisTitle)
    
    graphList.SetTitle(headTitle)
    
    canvas.cd()
    graphList.Draw()
    canvas.Update()
    canvas.Print(fileName)


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
        canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_2d_diff_sipm/timing_2d_diff_sipm_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    elif num == 3:
        canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_2d_diff_lgad/timing_2d_diff_lgad_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)
    else:
        canvas.Print(md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/timing/timing_2d/timing_2d_"+str(md.getBatchNumber())+"_"+str(chan) + fileName)

    canvas.Clear()
