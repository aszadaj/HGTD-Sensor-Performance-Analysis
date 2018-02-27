import ROOT
import metadata as md
import numpy as np

import data_management as dm

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
        
        availableRunNumbersPeakTimes = md.readFileNames("pulse_peak_time")
        
        numberOfEventPerRun = [0]
        
        for runNumber in runNumbers:
        
            print runNumber
            if runNumber in availableRunNumbersPeakTimes:
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
    global chan

    canvas = ROOT.TCanvas("Timing", "timing")
    
    #channels = ["chan0"]
    
    xbins = 6000
 
    print peak_time.dtype
 
    for chan in channels:
        if chan != SiPM_chan and chan != "chan0":
            
            index = int(chan[-1:])

            # 1D PLOTS
            time_diff[chan] = ROOT.TH1D("Time difference "+md.getNameOfSensor(chan), "time_difference" + chan, xbins, -15000, 15000)
            

            # Fill TH1 object and cut the noise for the DUT and SiPM < 200 mV, specified in run log
            for entry in range(0, len(time_difference[chan])):
                if time_difference[chan][entry] != 0 and peak_value[chan][entry] < md.getPulseAmplitudeCut(chan) and peak_value[SiPM_chan][entry] < md.getPulseAmplitudeCut(SiPM_chan):
                    time_diff[chan].Fill(time_difference[chan][entry]*1000)
        

            # Choose the range for the fit
            N = 1
            xMin = time_diff[chan].GetMean() - N * time_diff[chan].GetStdDev()
            xMax = time_diff[chan].GetMean() + N * time_diff[chan].GetStdDev()
 
            # Perform the fit
            time_diff[chan].Fit("gaus", "0", "", xMin, xMax)
            fit_function = time_diff[chan].GetFunction("gaus")
            fitted_parameters = [fit_function.GetParameter(0), fit_function.GetParameter(1), fit_function.GetParameter(2)]
            
            # Rescale the range of the plot
            N = 4
            xMin = time_diff[chan].GetMean() - N * time_diff[chan].GetStdDev()
            xMax = time_diff[chan].GetMean() + N * time_diff[chan].GetStdDev()
            

            # Print the fit function with the extracted parameters
            fit_function_adapted = ROOT.TF1("fit_peak_1", "gaus", xMin, xMax)
            fit_function_adapted.SetParameters(fitted_parameters[0], fitted_parameters[1], fitted_parameters[2])
    
            time_diff[chan].SetAxisRange(xMin, xMax)
            
            # Calculate the time resolution given that the SiPM is in the same oscilloscope as the DUT.
            
            # Need source for this!
            sigma_SiPM = 30
            sigma_fit = fitted_parameters[2]
            
            sigma_DUT = np.sqrt( np.power(sigma_fit,2) - np.power(sigma_SiPM, 2)  )
            
            
            # Print 1D plot time difference distribution
            headTitle = "Time difference SiPM and "+md.getNameOfSensor(chan)+", Sep 2017, B"+str(md.getBatchNumber())
            xAxisTitle = "\Delta t_{SiPM-LGAD} (ps)"
            yAxisTitle = "Number (N)"
            fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_distribution/timing_distribution_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
            exportTHPlot(time_diff[chan], titles, "", fit_function_adapted, sigma_DUT)



def exportTHPlot(graphList, titles, drawOption, fit, sigma=0):
 
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    

    ROOT.gStyle.SetOptFit(0002)
    ROOT.gStyle.SetOptStat("ne")

    graphList.Draw(drawOption)
    fit.Draw("SAME")
  
    canvas.Update()
    
    
    ## Remove text from stats box
    statsBox = canvas.GetPrimitive("stats")
    statsBox.SetName("Mystats")
    
    graphList.SetStats(0)

    linesStatsBox = statsBox.GetListOfLines()
    
    textMean = statsBox.GetLineWith("Mean")
    linesStatsBox.Remove(textMean)
    textConstant = statsBox.GetLineWith("Constant")
    linesStatsBox.Remove(textConstant)
    textSigma = statsBox.GetLineWith("Sigma")
    linesStatsBox.Remove(textSigma)
    
    statsBox.AddText("\sigma_{"+md.getNameOfSensor(chan)+"} = "+str(sigma)[0:6])
    canvas.Modified()
    canvas.Update()
    

    canvas.Print(titles[3])
    canvas.Clear()

