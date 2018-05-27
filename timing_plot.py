import ROOT
import metadata as md
import numpy as np

import data_management as dm
import timing_calculations as t_calc

ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")

# TCanvas object for all TH1 objects
canvas = ROOT.TCanvas("Timing", "timing")

# Range and bins for the window for TH1 objects
xbins = 1800
bin_range = 15000

def timingPlots():

    print "\nStart producing TIMING plots, batches:", md.batchNumbers
    
    for batchNumber in md.batchNumbers:
    
        dm.defineDataFolderPath()
        
        time_difference_linear = np.empty(0)
        time_difference_sys_eq = np.empty(0)
        
        time_difference_linear_cfd05 = np.empty(0)
        time_difference_sys_eq_cfd05 = np.empty(0)
        
        peak_value = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers
        
        for runNumber in runNumbers:
        
            md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
            

            if time_difference_linear.size == 0:
      
                time_difference_linear  = dm.importTimingFile("linear")
                time_difference_linear_cfd05  = dm.importTimingFile("linear_cfd05")
                
                if md.getBatchNumber()/100 != 6:
                    time_difference_sys_eq  = dm.importTimingFile("sys_eq")
                    time_difference_sys_eq_cfd05  = dm.importTimingFile("sys_eq_cfd05")
                
                peak_value = dm.importPulseFile("peak_value")
            
            else:

                time_difference_linear = np.concatenate((time_difference_linear, dm.importTimingFile("linear")), axis = 0)
                time_difference_linear_cfd05 = np.concatenate((time_difference_linear_cfd05, dm.importTimingFile("linear_cfd05")), axis = 0)
                
                if md.getBatchNumber()/100 != 6:
                
                    time_difference_sys_eq = np.concatenate((time_difference_sys_eq, dm.importTimingFile("sys_eq")), axis = 0)
                    time_difference_sys_eq_cfd05 = np.concatenate((time_difference_sys_eq_cfd05, dm.importTimingFile("sys_eq_cfd05")), axis = 0)


                peak_value = np.concatenate((peak_value, dm.importPulseFile("peak_value")), axis = 0)

        
        if len(peak_value) != 0:
            
            # Differences between two sensors, wrt peak time and cfd05 reference
            produceTimingDistributionPlots(time_difference_linear, peak_value)
            produceTimingDistributionPlots(time_difference_linear_cfd05, peak_value, True)

            # System of linear equations between sensors, wrt peak time and cfd05 reference
            # Batch 6 is omitted the calculation of system of equations
            if md.getBatchNumber()/100 != 6:
                produceTimingDistributionPlotsSysEq(time_difference_sys_eq, peak_value)
                produceTimingDistributionPlotsSysEq(time_difference_sys_eq_cfd05, peak_value, True)


    print "\nDone with producing TIMING plots.\n"


def produceTimingDistributionPlots(time_difference, peak_value, cfd05=False):
    
    time_diff_th1d = dict()
    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    
    for chan in time_difference.dtype.names:
    
        if SiPM_chan == chan:
            continue
    
        print "\nTIMING NORMAL PLOTS: Batch", md.getBatchNumber(),"sensor", md.getNameOfSensor(chan), chan, "\n"

        time_diff_th1d[chan] = ROOT.TH1D("Time difference "+md.getNameOfSensor(chan), "time_difference" + chan, xbins, -bin_range, bin_range)
     
        # Fill the objects, without cuts on the SiPM
        for entry in range(0, len(time_difference[chan])):
            if time_difference[chan][entry] != 0:
                time_diff_th1d[chan].Fill(time_difference[chan][entry])

        # Get fit function with width of the distributions
        sigma_DUT, sigma_fit_error = t_calc.getSigmasFromFit(time_diff_th1d[chan], chan)

        # Set titles and export file
        headTitle = "Time difference SiPM and "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
        xAxisTitle = "\Deltat [ps]"
        yAxisTitle = "Entries"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/normal/cfd05/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+"_diff_osc_cfd05.pdf"

        if md.checkIfSameOscAsSiPM(chan):
            fileName = fileName.replace("diff_osc", "same_osc")

        if cfd05:
                fileName = fileName.replace("cfd05", "peak")

        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportTHPlot(time_diff_th1d[chan], titles, chan, [sigma_DUT, sigma_fit_error] )


        # Export the result together with its error
        type = "timing_normal"
        if cfd05:
            type += "_cfd05"
        dt = (  [(type, '<f8') ])
        timing_results = np.empty(2, dtype = dt)
        timing_results[type][0] = sigma_DUT
        timing_results[type][1] = sigma_fit_error
        sensor_info = [md.getNameOfSensor(chan), chan]
        dm.exportTimingResults(timing_results, sensor_info, md.checkIfSameOscAsSiPM(chan), cfd05)


# Use this method to calculate the linear system of equations solution
def produceTimingDistributionPlotsSysEq(time_difference, peak_value, cfd05=False):
    
    # TH1 objects
    time_diff_th1d = dict()
    
    osc1 = ["chan0", "chan1", "chan2", "chan3"]
    sigma_convoluted = np.zeros((4,4))
    sigma_error      = np.zeros((4,4))
    
    # First loop, calculate the sigmas for each combination of time differences
    for chan in osc1:
    
        print "\nTIMING SYSTEM PLOTS: Batch", md.getBatchNumber(),"sensor", md.getNameOfSensor(chan), chan, "\n"
        
        # Do not consider the same channel when comparing two
        chan2_list = list(osc1)
        chan2_list.remove(chan)
        
        # Create TH1 object
        time_diff_th1d[chan] = dict()
        for chan2 in chan2_list:
            time_diff_th1d[chan][chan2] = ROOT.TH1D("System of equations \sigma_{"+chan[-1]+chan2[-1]+"}", "time_difference" + chan, xbins, -bin_range, bin_range)
        
        # Fill TH1 object between channels in oscilloscope
        for entry in range(0, len(time_difference[chan])):
            for index in range(0, len(chan2_list)):
                chan2 = chan2_list[index]
                
                # No amplitude cuts here!
                if time_difference[chan][entry][index] != 0:
                    time_diff_th1d[chan][chan2].Fill(time_difference[chan][entry][index])

        # Get sigma and adapt distribution curve
        for chan2 in chan2_list:
      
            # Find the maximal value
            MPV_bin = time_diff_th1d[chan][chan2].GetMaximumBin()
            MPV_time_diff = int(time_diff_th1d[chan][chan2].GetXaxis().GetBinCenter(MPV_bin))
            MPV_entries = time_diff_th1d[chan][chan2].GetMaximum()

            # Change the window
            window_range = 1000
            xMin = MPV_time_diff - window_range
            xMax = MPV_time_diff + window_range
            time_diff_th1d[chan][chan2].SetAxisRange(xMin, xMax)

            # Redefine range for the fit
            N = 2
            sigma_window = time_diff_th1d[chan][chan2].GetStdDev()
            mean_window = time_diff_th1d[chan][chan2].GetMean()
            xMin = mean_window - N * sigma_window
            xMax = mean_window + N * sigma_window
          
            # Obtain the parameters
            time_diff_th1d[chan][chan2].Fit("gaus", "Q", "", xMin, xMax)
            fit_function = time_diff_th1d[chan][chan2].GetFunction("gaus")
            
            i = int(chan[-1]) % 4
            j = int(chan2[-1]) % 4
            
            try:
           
                # Get sigma between two channels
                sigma_convoluted[i][j] = sigma_convoluted[j][i] = fit_function.GetParameter(2)
                sigma_error[i][j] = sigma_error[j][i] = fit_function.GetParError(2)
                
            except:
            
                sigma_convoluted[i][j] = sigma_convoluted[j][i] = 0
                sigma_error[i][j] = sigma_error[j][i] = 0

    # Solve the system
    sigmas_chan, sigmas_error = t_calc.solveLinearEq(sigma_convoluted, sigma_error)

    # Second loop, print the graphs together with the solutions
    for chan in osc1:
        chan2_list = list(osc1)
        chan2_list.remove(chan)
        
        # Create numpy array to export the results
        type = "timing_system"
        if cfd05:
            type += "_cfd05"
        dt = ([(type, '<f8')])
        timing_results_sys_eq = np.empty(2, dtype = dt)
        
        # Loop through the combinations
        for chan2 in chan2_list:

            # Create titles and print the graph
            headTitle = "Time difference "+md.getNameOfSensor(chan)+" and "+md.getNameOfSensor(chan2)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
            xAxisTitle = "\Deltat [ps]"
            yAxisTitle = "Entries"
            fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/system/cfd05/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+"_and_"+str(md.getNameOfSensor(chan2))+"_cfd05.pdf"

            if cfd05:
                fileName = fileName.replace("cfd05", "peak")
        
            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]

            sigma_DUT = sigmas_chan.item((0, index))
            sigma_DUT_error = sigmas_error.item((0, index))
            index = int(chan[-1]) % 4
            exportTHPlot(time_diff_th1d[chan][chan2], titles, chan,[sigma_DUT, sigma_DUT_error])

            timing_results_sys_eq[type][0] = sigma_DUT
            timing_results_sys_eq[type][1] = sigma_DUT_error

        # Export results
        sensor_info = [md.getNameOfSensor(chan), chan]
        dm.exportTimingResultsSysEq(timing_results_sys_eq, sensor_info, cfd05)


def exportTHPlot(graphList, titles, chan, sigma):

    canvas.Clear()
 
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    ROOT.gStyle.SetOptFit(0012)
    ROOT.gStyle.SetOptStat("ne")

    graphList.Draw()
    canvas.Update()
    
    ## Remove text from stats box
    statsBox = canvas.GetPrimitive("stats")
    statsBox.SetName("Mystats")
    graphList.SetStats(0)
    statsBox.AddText("\sigma_{"+md.getNameOfSensor(chan)+"} = "+str(sigma[0])[0:6] + " \pm " + str(sigma[1])[0:4])
    canvas.Modified()
    canvas.Update()
    

    canvas.Print(titles[3])
    dm.exportROOTHistogram(graphList, titles[3])


