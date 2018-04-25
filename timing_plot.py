import ROOT
import metadata as md
import numpy as np

import data_management as dm
import timing_calculations as t_calc

def timingPlots():

    print "\nStart producing TIMING plots, batches:", md.batchNumbers
    
    for batchNumber in md.batchNumbers:
    
        if batchNumber in [405, 406, 705, 706]:
            continue
        
        print "\nBatch", batchNumber,"\n"
        
        dm.defineDataFolderPath()
        
        time_difference_linear = np.empty(0)
        time_difference_sys_eq = np.empty(0)
        
        time_difference_linear_cfd05 = np.empty(0)
        time_difference_sys_eq_cfd05 = np.empty(0)
        
        peak_values = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers
        
        availableRunNumbersPeakTimes = md.readFileNames("pulse_peak_time")
        
        
        for runNumber in runNumbers:
        
            if runNumber in availableRunNumbersPeakTimes:
                md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
                
                print "Importing run", md.getRunNumber(), "\n"

                if time_difference_linear.size == 0:
          
                    time_difference_linear  = dm.importTimingFile("linear")
                    time_difference_sys_eq  = dm.importTimingFile("sys_eq")
                    
                    time_difference_linear_cfd05  = dm.importTimingFile("linear_cfd05")
                    time_difference_sys_eq_cfd05  = dm.importTimingFile("sys_eq_cfd05")
                    
                    peak_values = dm.importPulseFile("peak_value")
                
                else:

                    time_difference_linear = np.concatenate((time_difference_linear, dm.importTimingFile("linear")), axis = 0)
                    time_difference_sys_eq = np.concatenate((time_difference_sys_eq, dm.importTimingFile("sys_eq")), axis = 0)
                    
                    time_difference_linear_cfd05 = np.concatenate((time_difference_linear_cfd05, dm.importTimingFile("linear_cfd05")), axis = 0)
                    time_difference_sys_eq_cfd05 = np.concatenate((time_difference_sys_eq_cfd05, dm.importTimingFile("sys_eq_cfd05")), axis = 0)
                    
                    peak_values = np.concatenate((peak_values, dm.importPulseFile("peak_value")), axis = 0)

        
        if len(peak_values) != 0:
        
            print "Done with importing files for", batchNumber
            print "Producing plots.\n"
            
            # Differences between two sensors, wrt peak time and cfd05 reference
            produceTimingDistributionPlots(time_difference_linear, peak_values)
            produceTimingDistributionPlots(time_difference_linear_cfd05, peak_values, True)

            # System of linear equations between sensors, wrt peak time and cfd05 reference
            #produceTimingDistributionPlotsSysEq(time_difference_sys_eq, peak_values)
            #produceTimingDistributionPlotsSysEq(time_difference_sys_eq_cfd05, peak_values, True)


    print "Done with producing TIMING plots.\n"


def produceTimingDistributionPlots(time_difference, peak_value, cfd05=False):

    time_diff = dict()
    fit_function = dict()

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    
    chans = time_difference.dtype.names

    global canvas
    global chan

    canvas = ROOT.TCanvas("Timing", "timing")
    
    xbins = 3300
    xbin_low = -15000
    xbin_high = 15000
    
    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    channels = [x for x in chans if x != SiPM_chan]

    #channels = ["chan1"]
    
    
    if md.getBatchNumber() == 102:
        channels = [x for x in chans if md.getNameOfSensor(x) in ["W9-LGA35", "50D-GBGR2", "W4-LG12", "W4-S215"]]
    
    if md.getBatchNumber() == 302:
        channels = [x for x in chans if md.getNameOfSensor(x) in ["W4-S203", "W4-S1061", "W4-S1022", "W4-RD01"]]
    
    if md.getBatchNumber() == 502:
        channels = [x for x in chans if md.getNameOfSensor(x) in ["W4-S204_6e14"]]

    for chan in channels:

        same_osc = md.checkIfSameOscAsSiPM(chan)
    
        index = int(chan[-1:])

        # TH1 object
        time_diff[chan] = ROOT.TH1D("Time difference "+md.getNameOfSensor(chan), "time_difference" + chan, xbins, xbin_low, xbin_high)
     
        # Fill TH1 object and cut the noise for the DUT and SiPM < -200 mV, specified in run log
        for entry in range(0, len(time_difference[chan])):
            if time_difference[chan][entry] != 0 and peak_value[chan][entry] < md.getPulseAmplitudeCut(chan) and peak_value[SiPM_chan][entry] < md.getPulseAmplitudeCut(SiPM_chan):
                time_diff[chan].Fill(time_difference[chan][entry]*1000)
    
        # Remove bins with less than 4 entries
        for bin in range(1, xbins+1):

            num = time_diff[chan].GetBinContent(bin)

            if num < 5:
                time_diff[chan].SetBinContent(bin, 0)

        time_diff[chan].ResetStats()
        
        fit_function, sigma_DUT, sigma_fit_error = t_calc.getFitFunction(time_diff[chan], chan, same_osc)

        # Print 1D plot time difference distribution
        headTitle = "Time difference SiPM and "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
        xAxisTitle = "\Deltat [ps]"
        yAxisTitle = "Entries"
        #fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/normal/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"

        fileName = "/Users/aszadaj/cernbox/SH203X/Logs/22042018/TRY1/"+md.getNameOfSensor(chan)+"_debug/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        

        if same_osc:
            fileName = fileName.replace(".pdf", "_same_osc.pdf")

        else:
            fileName = fileName.replace(".pdf", "_diff_osc.pdf")


        if cfd05:
            fileName = fileName.replace(".pdf", "_cfd05.pdf")

        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportTHPlot(time_diff[chan], titles, "", fit_function, sigma_DUT)

#
#
#        dt = (  [('timing_normal', '<f8') ])
#        timing_results = np.empty(2, dtype = dt)
#
#        timing_results["timing_normal"][0] = sigma_DUT
#        timing_results["timing_normal"][1] = sigma_fit_error
#        sensor_info = [md.getNameOfSensor(chan), chan]
#
#
#        # Export results
#        # Array structure:
#        # time_resolution_DUT with one sigma value from adapted fit
#
#        dm.exportTimingResults(timing_results, sensor_info, same_osc, cfd05)


# Use this method to calculate the linear system of equations solution
def produceTimingDistributionPlotsSysEq(time_difference, peak_value, cfd05 = False):
    
    # TH1 objects
    time_diff = dict()
    fit_function = dict()

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    
    channels = time_difference.dtype.names

    global canvas
    global chan

    canvas = ROOT.TCanvas("Timing", "timing")
    
    xbins = 6000
    
    osc1 = ["chan0", "chan1", "chan2", "chan3"]
    s = (4,4)
    sigmas_mix = np.zeros(s)
    
    for chan in osc1:
        
        # Do not consider the same channel when comparing two
        chan2_list = list(osc1)
        chan2_list.remove(chan)
        
        # Create TH1 object
        time_diff[chan] = dict()
        for chan2 in chan2_list:
        
            time_diff[chan][chan2] = ROOT.TH1D("System of equations \sigma_{"+chan[-1]+chan2[-1]+"}", "time_difference" + chan, xbins, -15000, 15000)
        
        # Fill TH1 object between channels in oscilloscope
        for entry in range(0, len(time_difference[chan])):
            for index in range(0, len(chan2_list)):
                chan2 = chan2_list[index]
                if time_difference[chan][entry][index] != 0 and peak_value[chan][entry] < md.getPulseAmplitudeCut(chan) and peak_value[chan2][entry] < md.getPulseAmplitudeCut(chan2):
                    time_diff[chan][chan2].Fill(time_difference[chan][entry][index])
        
        for chan2 in chan2_list:
            for bin in range(1, xbins+1):
        
                num = time_diff[chan][chan2].GetBinContent(bin)

                if num < 2:
                    time_diff[chan][chan2].SetBinContent(bin, 0)
            
            time_diff[chan][chan2].ResetStats()

        # Get sigma and adapt distribution curve
        for chan2 in chan2_list:
            
            i = int(chan[-1]) % 4
            j = int(chan2[-1]) % 4
            
            # Choose the range for the fit
            N = 4
            xMin = time_diff[chan][chan2].GetMean() - N * time_diff[chan][chan2].GetStdDev()
            xMax = time_diff[chan][chan2].GetMean() + N * time_diff[chan][chan2].GetStdDev()
          
            # Obtain the parameters
            time_diff[chan][chan2].Fit("gaus", "Q0", "", xMin, xMax)
            fit_function = time_diff[chan][chan2].GetFunction("gaus")
            fitted_parameters = [fit_function.GetParameter(0), fit_function.GetParameter(1), fit_function.GetParameter(2)]
            
            # Get sigma between two channels
            sigmas_mix[i][j] = fit_function.GetParameter(2)
            sigmas_mix[j][i] = fit_function.GetParameter(2)

    # Obtain the sigmas for each channel


    sigmas_chan = t_calc.solveLinearEq(sigmas_mix)


    for chan in osc1:
        chan2_list = list(osc1)
        chan2_list.remove(chan)
        
        dt = (  [('timing_system', '<f8') ])
        timing_results_sys_eq = np.empty(1, dtype = dt)
        
        for chan2 in chan2_list:
        
            if md.getNameOfSensor(chan) != md.getNameOfSensor(chan2):

                index = int(chan[-1]) % 4
                
                # Rescale the range of the plot, to make the plot look better
                N = 4
                xMin = time_diff[chan][chan2].GetMean() - N * time_diff[chan][chan2].GetStdDev()
                xMax = time_diff[chan][chan2].GetMean() + N * time_diff[chan][chan2].GetStdDev()
                
                # Obtain the parameters
                time_diff[chan][chan2].Fit("gaus", "Q0", "", xMin, xMax)
                fit_function = time_diff[chan][chan2].GetFunction("gaus")
                fitted_parameters = [fit_function.GetParameter(0), fit_function.GetParameter(1), fit_function.GetParameter(2)]
                
                # Add the fit function
                fit_function_adapted = ROOT.TF1("fit_peak_1", "gaus", xMin, xMax)
                fit_function_adapted.SetParameters(fitted_parameters[0], fitted_parameters[1], fitted_parameters[2])
                time_diff[chan][chan2].SetAxisRange(xMin, xMax)


                # Print 1D plot time difference distribution
                headTitle = "Time difference "+md.getNameOfSensor(chan)+" and "+md.getNameOfSensor(chan2)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
                xAxisTitle = "\Deltat [ps]"
                yAxisTitle = "Entries"
                #fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/system/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+"_and_"+str(md.getNameOfSensor(chan2))+".pdf"
                
                fileName = "/Users/aszadaj/cernbox/SH203X/Logs/22042018/TRY1/"+md.getNameOfSensor(chan)+"_debug/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+"_and_"+str(md.getNameOfSensor(chan2))+".pdf"
                
                if cfd05:
                    fileName = fileName.replace(".pdf", "_cfd05.pdf")
            
                titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
                exportTHPlot(time_diff[chan][chan2], titles, "", fit_function_adapted, sigmas_chan.item((0, index)))

            timing_results_sys_eq["timing_system"] =  sigmas_chan.item((0, index))

        # Export results
        # Array structure:
        # time_resolution_DUT_sys_eq with one sigma value

        sensor_info = [md.getNameOfSensor(chan), chan]

        dm.exportTimingResultsSysEq(timing_results_sys_eq, sensor_info, cfd05)


def exportTHPlot(graphList, titles, drawOption, fit, sigma=0):
 
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    ROOT.gStyle.SetOptFit(0012)
    ROOT.gStyle.SetOptStat("ne")

    graphList.Draw()
    fit.Draw("SAME")
  
    canvas.Update()
    
    ## Remove text from stats box
    statsBox = canvas.GetPrimitive("stats")
    statsBox.SetName("Mystats")
    
    graphList.SetStats(0)

    linesStatsBox = statsBox.GetListOfLines()


    statsBox.AddText("\sigma_{"+md.getNameOfSensor(chan)+"} = "+str(sigma)[0:6])
    canvas.Modified()
    canvas.Update()
    

    canvas.Print(titles[3])
    #dm.exportROOTHistogram(graphList, titles[3])
    canvas.Clear()

