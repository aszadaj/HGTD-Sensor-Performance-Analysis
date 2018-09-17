import ROOT
import numpy as np

import data_management as dm
import run_log_metadata as md
import timing_calculations as t_calc

ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")

# TCanvas object for all TH1 objects
canvas = ROOT.TCanvas("Timing", "timing")

# Range and bins for the window for TH1 objects
xbins = 2000
bin_range = 15000

def timingPlots():

    print "\nStart producing TIMING plots, batches:", md.batchNumbers
    

    for batchNumber in md.batchNumbers:
    
        dm.defineDataFolderPath()
        
        time_difference_linear = np.empty(0)
        time_difference_sys_eq = np.empty(0)
        
        time_difference_linear_cfd = np.empty(0)
        time_difference_sys_eq_cfd = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers
    
        for runNumber in runNumbers:
        
            md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
            
            if runNumber not in md.getRunsWithSensor(md.sensor):
                continue
                    
            if time_difference_linear.size == 0:
      
                time_difference_linear  = dm.exportImportROOTData("timing", "linear", False)
                time_difference_linear_cfd  = dm.exportImportROOTData("timing", "linear_cfd", False)
                
                if md.getBatchNumber()/100 != 6:
                    time_difference_sys_eq  = dm.exportImportROOTData("timing", "sys_eq", False)
                    time_difference_sys_eq_cfd  = dm.exportImportROOTData("timing", "sys_eq_cfd", False)

            
            else:

                time_difference_linear = np.concatenate((time_difference_linear, dm.exportImportROOTData("timing", "linear", False)), axis = 0)
                time_difference_linear_cfd = np.concatenate((time_difference_linear_cfd, dm.exportImportROOTData("timing", "linear_cfd", False)), axis = 0)
                
                if md.getBatchNumber()/100 != 6:
                
                    time_difference_sys_eq = np.concatenate((time_difference_sys_eq, dm.exportImportROOTData("timing", "sys_eq", False)), axis = 0)
                    time_difference_sys_eq_cfd = np.concatenate((time_difference_sys_eq_cfd, dm.exportImportROOTData("timing", "sys_eq_cfd", False)), axis = 0)


        if time_difference_linear.size != 0:

            # Differences between two sensors, wrt peak time and cfd reference

            print "\nTIMING RESOLUTION NORMAL PEAK PLOTS", "Batch", md.getBatchNumber()
            produceTimingDistributionPlots(time_difference_linear)

            print "\nTIMING RESOLUTION NORMAL CFD PLOTS", "Batch", md.getBatchNumber()
            produceTimingDistributionPlots(time_difference_linear_cfd, True)

            # System of linear equations between sensors, wrt peak time and cfd reference
            # Batch 6 is omitted the calculation of system of equations
            if md.getBatchNumber()/100 != 6:

                print "\nTIMING RESOLUTION SYSTEM PEAK PLOTS", "Batch", md.getBatchNumber()
                produceTimingDistributionPlotsSysEq(time_difference_sys_eq)

                print "\nTIMING RESOLUTION SYSTEM CFD PLOTS", "Batch", md.getBatchNumber()
                produceTimingDistributionPlotsSysEq(time_difference_sys_eq_cfd, True)


    print "\nDone with producing TIMING RESOLUTION plots.\n"


############## LINEAR TIME DIFFERENCE ###############

def produceTimingDistributionPlots(time_difference, cfd=False):
    
    time_diff_th1d = dict()

    for chan in time_difference.dtype.names:
    
        if md.getNameOfSensor(chan) == "SiPM-AFP":
            continue
        
        if md.getNameOfSensor(chan) != md.sensor and md.sensor != "":
            continue
    
        print "\n", md.getNameOfSensor(chan), "\n"

        time_diff_th1d[chan] = ROOT.TH1D("Time difference "+md.getNameOfSensor(chan), "time_difference" + chan, xbins, -bin_range, bin_range)
     
        # Fill the objects, without cuts on the SiPM
        for entry in range(0, len(time_difference[chan])):
            if time_difference[chan][entry] != 0:
                time_diff_th1d[chan].Fill(time_difference[chan][entry])

        # Get fit function with width of the distributions
        # Check if the filled object have at least 1000 entries
        
        if time_diff_th1d[chan].GetEntries() < 1000:
            
            if cfd:
                type = "cfd reference"
            
            else:
                type = "peak reference"
                
            print "Omitting sensor", md.getNameOfSensor(chan), "for", type, "due to low statistics. \n"
            
            continue
            
        sigma_DUT, sigma_fit_error = t_calc.getSigmasFromFit(time_diff_th1d[chan], chan)

        # Set titles and export file
        headTitle = "Time difference SiPM and "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"
        xAxisTitle = "\Deltat [ps]"
        yAxisTitle = "Entries"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/normal/peak/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+"_diff_osc_peak.pdf"

        if md.checkIfSameOscAsSiPM(chan):
            fileName = fileName.replace("diff_osc", "same_osc")

        if cfd:
            fileName = fileName.replace("peak", "cfd")



        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportTHPlot(time_diff_th1d[chan], titles, chan, [sigma_DUT, sigma_fit_error] )


        # Export the result together with its error
        type = "timing_normal"
        if cfd:
            type += "_cfd"
        dt = (  [(type, '<f8') ])
        timing_results = np.empty(2, dtype = dt)
        timing_results[type][0] = sigma_DUT
        timing_results[type][1] = sigma_fit_error
        sensor_info = [md.getNameOfSensor(chan), chan]
        dm.exportImportROOTData("results", "timing_normal", True, timing_results, sensor_info, md.checkIfSameOscAsSiPM(chan), cfd)


############## SYSTEM OF EQUATIONS TIME DIFFERENCE ###############


# Use this method to calculate the linear system of equations solution
# If one of the functions have less than 1000 entries, remove it from the calculation!
def produceTimingDistributionPlotsSysEq(time_difference, cfd=False):
    
    # TH1 objects
    time_diff_th1d = dict()
    
    omit_batch = False
    
    osc1 = ["chan0", "chan1", "chan2", "chan3"]
    sigma_convoluted = np.zeros((4,4))
    sigma_error      = np.zeros((4,4))
    
    # First loop, calculate the sigmas for each combination of time differences
    for chan in osc1:
    
        print md.getNameOfSensor(chan), "\n"
        
        # Do not consider the same channel when comparing two
        chan2_list = list(osc1)
        chan2_list.remove(chan)
        
        # Create TH1 object
        time_diff_th1d[chan] = dict()
        for chan2 in chan2_list:
            time_diff_th1d[chan][chan2] = ROOT.TH1D("System of equations \sigma_{"+chan[-1]+chan2[-1]+"}", "time_difference" + chan, xbins, -bin_range, bin_range)
        
        # Fill TH1 object between channels in first oscilloscope
        for entry in range(0, len(time_difference[chan])):
            for index in range(0, len(chan2_list)):
                chan2 = chan2_list[index]
                
                if time_difference[chan][entry][index] != 0:
                    time_diff_th1d[chan][chan2].Fill(time_difference[chan][entry][index])
    
    

        # Get sigma and adapt distribution curve
        for chan2 in chan2_list:
      
            # Find the maximal value
            MPV_bin = time_diff_th1d[chan][chan2].GetMaximumBin()
            MPV_time_diff = int(time_diff_th1d[chan][chan2].GetXaxis().GetBinCenter(MPV_bin))

            # Change the window
            window_range = 2000
            
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
            
            # set a condition to set less than 1500 entries, since the function will not work, check will not work
            
            i = int(chan[-1]) % 4
            j = int(chan2[-1]) % 4
            
            try:
           
                # Get sigma between two channels
                sigma_convoluted[i][j] = sigma_convoluted[j][i] = fit_function.GetParameter(2)
                sigma_error[i][j] = sigma_error[j][i] = fit_function.GetParError(2)
            
            except:
            
                sigma_convoluted[i][j] = sigma_convoluted[j][i] = 0
                sigma_error[i][j] = sigma_error[j][i] = 0

    # Second loop, check if all combined plots have at least 1000 entries
    
    for chan in osc1:
        if omit_batch:
            break
        
        # Do not consider the same channel when comparing two
        chan2_list = list(osc1)
        chan2_list.remove(chan)
        
        for chan2 in chan2_list:
            if time_diff_th1d[chan][chan2].GetEntries() < 1000:
            
                if cfd:
                    type = "cfd reference"
                else:
                    type = "peak reference"
                
                print "Omitting batch", md.getBatchNumber(), "for", type, "time difference plot for", md.getNameOfSensor(chan), "and", md.getNameOfSensor(chan2), "have less than 1000 entries! \n"
                omit_batch = True
                break
                

    # Solve the system
    if not omit_batch:
        sigmas_chan, sigmas_error = t_calc.solveLinearEq(sigma_convoluted, sigma_error)

    # Third loop, print the graphs together with the solutions
    for chan in osc1:
        
        # This is in case the condition of requiring at least 1000 entries for each plots is not fulfilled
        if omit_batch:
            break
    
        chan2_list = list(osc1)
        chan2_list.remove(chan)
        
        # Create numpy array to export the results
        type = "timing_system"
        
        if cfd:
            type += "_cfd"
        
        dt = ([(type, '<f8')])
        timing_results_sys_eq = np.empty(2, dtype = dt)
        
        # Loop through the combinations
        for chan2 in chan2_list:

            # Create titles and print the graph
            headTitle = "Time difference "+md.getNameOfSensor(chan)+" and "+md.getNameOfSensor(chan2)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"
            xAxisTitle = "\Deltat [ps]"
            yAxisTitle = "Entries"
            fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/system/peak/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+"_and_"+str(md.getNameOfSensor(chan2))+"_peak.pdf"

            if cfd:
                fileName = fileName.replace("peak", "cfd")
        

            index = int(chan[-1]) % 4
            sigma_DUT = sigmas_chan.item((0, index))
            sigma_DUT_error = sigmas_error.item((0, index))

            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
            exportTHPlot(time_diff_th1d[chan][chan2], titles, chan, [sigma_DUT, sigma_DUT_error])

            timing_results_sys_eq[type][0] = sigma_DUT
            timing_results_sys_eq[type][1] = sigma_DUT_error
            
        # Export the results
        sensor_info = [md.getNameOfSensor(chan), chan]

        dm.exportImportROOTData("results", "timing_system", True, timing_results_sys_eq, sensor_info, False, cfd)


############## EXPORT PLOT ###############

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
    
    # Remove text from stats box
    statsBox = canvas.GetPrimitive("stats")
    statsBox.SetName("Mystats")
    graphList.SetStats(0)
    statsBox.AddText("\sigma_{"+md.getNameOfSensor(chan)+"} = "+str(sigma[0])[0:6] + " \pm " + str(sigma[1])[0:4])
    canvas.Modified()
    canvas.Update()
    

    canvas.Print(titles[3])
    dm.exportImportROOTHistogram(titles[3], True, graphList)


