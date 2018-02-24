import ROOT
import metadata as md
import numpy as np

import data_management as dm

ROOT.gStyle.SetOptFit()

def timingPlots():

    print "\nStart producing TIMING plots, batches:", md.batchNumbers
    
    for batchNumber in md.batchNumbers:
        
        print "\nBatch", batchNumber,"\n"
        
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
    
    # FOR 2D PLOTS #
    time_diff_t_lgad = dict()
    time_diff_V_lgad = dict()
    time_diff_V_sipm = dict()
    time_diff_event_no = dict()
    fit_function = dict()

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    
    channels = time_difference.dtype.names

    global canvas

    canvas = ROOT.TCanvas("Timing", "timing")
    
    channels = ["chan0"]
    
    xbins = 6000
 
    for chan in channels:
        if chan != SiPM_chan:

            index = int(chan[-1:])
            
            # 1D PLOTS
            time_diff[chan] = ROOT.TH1D("Time difference "+md.getNameOfSensor(chan), "time_difference" + chan, xbins, -15, 15)
            
            # Fill TH1 object
            for entry in range(0, len(time_difference[chan])):
                if time_difference[chan][entry] != 0:
                    time_diff[chan].Fill(time_difference[chan][entry])
        
#            # Remove bins with less than some entries
#            count = 0
#            minEntries = 5 * md.getNumberOfRunsPerBatch()
#            for bin in range(1, xbins):
#                num = time_diff[chan].GetBinContent(bin)
#                if num < minEntries:
#                    time_diff[chan].SetBinContent(bin, 0)
#                    count += 1
#
#            # SetBinContent(bin, 0) increases an entry by 1.
#            time_diff[chan].SetEntries((int(time_diff[chan].GetEntries()) - count))

            N = 4
            xMin = time_diff[chan].GetMean() - N * time_diff[chan].GetStdDev()
            xMax = time_diff[chan].GetMean() + N * time_diff[chan].GetStdDev()

            # GAUSS FIT for TH1D
            time_diff[chan].Fit("gaus", "0", "", -12.45, -12.42) # Adapt fit to region only
            fit_function = time_diff[chan].GetFunction("gaus")
            fitted_parameters = [fit_function.GetParameter(0), fit_function.GetParameter(1), fit_function.GetParameter(2)]
            
            print "first peak", fitted_parameters
            fitted_peak = ROOT.TF1("fit_peak_1", "gaus", xMin, xMax)
            fitted_peak.SetParameters(fitted_parameters[0], fitted_parameters[1], fitted_parameters[2])
            
            time_diff[chan].Fit("gaus", "0", "", -12.55, -12.48) # Adapt fit to region only
            fit_function = time_diff[chan].GetFunction("gaus")
            fitted_parameters = [fit_function.GetParameter(0), fit_function.GetParameter(1), fit_function.GetParameter(2)]
            print "second peak", fitted_parameters
            fitted_peak2 = ROOT.TF1("fit_peak_1", "gaus", xMin, xMax)
            fitted_peak2.SetParameters(fitted_parameters[0], fitted_parameters[1], fitted_parameters[2])
        
            
            time_diff[chan].SetAxisRange(xMin, xMax)
            
            # Print 1D plot time difference distribution
            headTitle = "Time difference SiPM and "+md.getNameOfSensor(chan)+", Sep 2017, B"+str(md.getBatchNumber())
            xAxisTitle = "\Delta t_{SiPM-LGAD} (ns)"
            yAxisTitle = "Number (N)"
            fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_distribution/timing_distribution_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
            exportTHPlot(time_diff[chan], titles, "", fitted_peak, fitted_peak2)


#            ### 2D PLOTS ###
#
#              # Automatized constants for plotting right event number (the results were earlier concatenated)
#            maxNumber = 0
#
#            for index in reversed(range(0, len(numberOfEventPerRun)-1)):
#                if maxNumber < numberOfEventPerRun[index]-numberOfEventPerRun[index-1]:
#                    maxNumber = numberOfEventPerRun[index]-numberOfEventPerRun[index-1]
#
#
#            time_diff_t_lgad[chan] = ROOT.TH2F(md.getNameOfSensor(chan),"time_diff_t_lgad_"+chan,500,xMin,xMax,500,5,80)
#
#            time_diff_V_lgad[chan] = ROOT.TH2F(md.getNameOfSensor(chan),"time_diff_V_lgad_"+chan, 500,xMin,xMax,500,-50,500)
#
#            time_diff_V_sipm[chan] = ROOT.TH2F(md.getNameOfSensor(chan),"time_diff_V_sipm_"+chan,500,xMin,xMax,500,-50,500)
#
#            time_diff_event_no[chan] = ROOT.TH2F(md.getNameOfSensor(chan),"time_diff_event_no_"+chan,100,xMin,xMax,100,0, maxNumber)
#
#
#            entry_count = 0
#
#            # Fill TH2D objects
#            for entry in range(0, len(time_difference[chan])):
#
#                # If statement to keep track of correct event number
#                if entry+1 == numberOfEventPerRun[entry_count+1]:
#                    entry_count += 1
#
#
#                if peak_time[chan][entry] != 0 and peak_time[SiPM_chan][entry] != 0 and time_difference[chan][entry] != 0:
#
#                    # 2D plot time difference vs time peak in event
#                    time_diff_t_lgad[chan].Fill(time_difference[chan][entry], peak_time[chan][entry], 1)
#
#                    # 2D plot time difference, vs amplitude for LGAD
#                    time_diff_V_lgad[chan].Fill(time_difference[chan][entry], peak_value[chan][entry]*-1000, 1)
#
#                    # 2D plot time difference vs amplitude for SiPM
#                    time_diff_V_sipm[chan].Fill(time_difference[chan][entry], peak_value[SiPM_chan][entry]*-1000, 1)
#
#                    # 2D plot time difference vs event number
#                    time_diff_event_no[chan].Fill(time_difference[chan][entry], entry - numberOfEventPerRun[entry_count], 1)
#
#
#            # Print 2D plot time difference vs time peak in event
#            headTitle = "Time difference vs reference time "+md.getNameOfSensor(chan)+", Sep 2017 B" + str(md.getBatchNumber())
#            xAxisTitle = "\Delta t_{SIPM-LGAD} (ns)"
#            yAxisTitle = "t_{LGAD} (ns)"
#            fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_2d/timing_t_diff_vs_t_LGAD_"+str(md.getBatchNumber())+"_"+str(chan)  + "_"+str(md.getNameOfSensor(chan))+".pdf"
#            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
#            exportTHPlot(time_diff_t_lgad[chan], titles, "COLZ")
#
#
#            # Print 2D plot time difference vs amplitude for LGAD
#            headTitle = "Time difference vs LGAD pulse amplitude  "+md.getNameOfSensor(chan)+", Sep 2017 B" + str(md.getBatchNumber())
#            xAxisTitle = "\Delta t_{SiPM-LGAD} (ns)"
#            yAxisTitle = "LGAD Amplitude (mV)"
#            fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_2d_diff_lgad/timing_t_diff_vs_V_LGAD_"+str(md.getBatchNumber())+"_"+str(chan)  + "_"+str(md.getNameOfSensor(chan))+".pdf"
#            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
#            exportTHPlot(time_diff_V_lgad[chan], titles, "COLZ")
#
#
#            # Print 2D plot time difference vs amplitude for SiPM
#            headTitle = "Time difference vs SiPM pulse amplitude "+md.getNameOfSensor(chan)+", Sep 2017 B" + str(md.getBatchNumber())
#            xAxisTitle = "\Delta t_{SiPM-LGAD} (ns)"
#            yAxisTitle = "SiPM Amplitude (mV)"
#            fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_2d_diff_sipm/timing_t_diff_vs_V_SiPM_"+str(md.getBatchNumber())+"_"+str(chan) + "_"+str(md.getNameOfSensor(chan))+".pdf"
#            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
#            exportTHPlot(time_diff_V_sipm[chan], titles, "COLZ")
#
#
#            # Print 2D plot time difference vs event number
#            headTitle = "Time difference vs entry number "+md.getNameOfSensor(chan)+", Sep 2017 B" + str(md.getBatchNumber())
#            xAxisTitle = "\Delta t_{SiPM-LGAD} (ns)"
#            yAxisTitle = "Event number"
#            fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_2d_diff_event/timing_t_diff_vs_event_"+str(md.getBatchNumber())+"_"+str(chan) + "_"+str(md.getNameOfSensor(chan))+".pdf"
#            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
#            exportTHPlot(time_diff_event_no[chan], titles, "COLZ")


def exportTHPlot(graphList, titles, drawOption, fit, fit2):
 
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])

    graphList.Draw(drawOption)
    fit.Draw("SAME")
    fit2.Draw("SAME")
  
    canvas.Update()
    canvas.Print(titles[3])
    canvas.Clear()

