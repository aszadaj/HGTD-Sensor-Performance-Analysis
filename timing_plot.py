import ROOT
import metadata as md
import numpy as np

import data_management as dm
import timing_calculations as t_calc

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
    
    # TH1 objects
    time_diff = dict()
    fit_function = dict()

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    
    channels = time_difference.dtype.names

    global canvas
    global chan

    canvas = ROOT.TCanvas("Timing", "timing")
    
    #channels = ["chan0"]
    
    xbins = 6000
    
    osc1 = ["chan0", "chan1", "chan2", "chan3"]
    osc2 = ["chan4", "chan5", "chan6", "chan7"]
    
    if int(md.getBatchNumber()/100) == 3:
        osc2 = ["chan4", "chan5", "chan6"]
    
    oscilloscope_chan = [osc1, osc2]

    for channels_part in oscilloscope_chan:
        s = (4,4)
        sigmas_mix = np.zeros(s)
        
        for chan in channels_part:
            
            # Do not consider the same channel when comparing two
            chan2_list = list(channels_part)
            chan2_list.remove(chan)
            
            # Create TH1 object
            time_diff[chan] = dict()
            for chan2 in chan2_list:
                time_diff[chan][chan2] = ROOT.TH1D("TD \sigma_{"+chan[-1]+chan2[-1]+"}", "time_difference" + chan, xbins, -15000, 15000)
            
            # Fill TH1 object between channels in oscilloscope
            for entry in range(0, len(time_difference[chan])):
                for index in range(0, len(chan2_list)):
                    chan2 = chan2_list[index]
                    if time_difference[chan][entry][index] != 0 and peak_value[chan][entry] < md.getPulseAmplitudeCut(chan) and peak_value[chan2][entry] < md.getPulseAmplitudeCut(chan2):
                        time_diff[chan][chan2].Fill(time_difference[chan][entry][index])
        
            # Get sigma and adapt distribution curve
            for chan2 in chan2_list:
                
                i = int(chan[-1]) % 4
                j = int(chan2[-1]) % 4
                
                # Choose the range for the fit
                N = 1
                xMin = time_diff[chan][chan2].GetMean() - N * time_diff[chan][chan2].GetStdDev()
                xMax = time_diff[chan][chan2].GetMean() + N * time_diff[chan][chan2].GetStdDev()
                
                # Obtain the parameters
                time_diff[chan][chan2].Fit("gaus", "0", "", xMin, xMax)
                fit_function = time_diff[chan][chan2].GetFunction("gaus")
                fitted_parameters = [fit_function.GetParameter(0), fit_function.GetParameter(1), fit_function.GetParameter(2)]
                
                # Get sigma between two channels
                sigmas_mix[i][j] = fit_function.GetParameter(2)
                sigmas_mix[j][i] = fit_function.GetParameter(2)
                

        # Obtain the sigmas for each channel

        sigmas_chan = t_calc.solveLinearEq(sigmas_mix)
        print sigmas_chan
        
        for chan in channels_part:
            chan2_list = list(channels_part)
            chan2_list.remove(chan)
        
            for chan2 in chan2_list:

                index = int(chan[-1]) % 4
                
                # Rescale the range of the plot, to make the plot look better
                N = 4
                xMin = time_diff[chan][chan2].GetMean() - N * time_diff[chan][chan2].GetStdDev()
                xMax = time_diff[chan][chan2].GetMean() + N * time_diff[chan][chan2].GetStdDev()
                
                # Obtain the parameters
                time_diff[chan][chan2].Fit("gaus", "N", "", xMin, xMax)
                fit_function = time_diff[chan][chan2].GetFunction("gaus")
                fitted_parameters = [fit_function.GetParameter(0), fit_function.GetParameter(1), fit_function.GetParameter(2)]
                
                # Add the fit function
                fit_function_adapted = ROOT.TF1("fit_peak_1", "gaus", xMin, xMax)
                fit_function_adapted.SetParameters(fitted_parameters[0], fitted_parameters[1], fitted_parameters[2])
                time_diff[chan][chan2].SetAxisRange(xMin, xMax)

                # Print 1D plot time difference distribution
                headTitle = "Time difference "+md.getNameOfSensor(chan)+" and "+md.getNameOfSensor(chan2)+", Sep 2017, B"+str(md.getBatchNumber())
                xAxisTitle = "\Delta t_{DUT1 - DUT2} (ps)"
                yAxisTitle = "Number (N)"
                fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/time_diff_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+"_and_"+str(md.getNameOfSensor(chan2))+".pdf"
                titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
                print sigmas_chan.item((0, index))
                exportTHPlot(time_diff[chan][chan2], titles, "", fit_function_adapted, sigmas_chan.item((0, index)))



def exportTHPlot(graphList, titles, drawOption, fit, sigma):
 
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
    
    statsBox.AddText("\sigma_{"+md.getNameOfSensor(chan)+"} = "+str(sigma)[0:6])
    canvas.Modified()
    canvas.Update()
    

    canvas.Print(titles[3])
    canvas.Clear()

