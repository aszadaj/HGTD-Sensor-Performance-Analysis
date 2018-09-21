import ROOT
import numpy as np

import data_management as dm
import run_log_metadata as md
import timing_calculations as t_calc

ROOT.gROOT.SetBatch(True)
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")

# TCanvas object for all TH1 objects
canvas = ROOT.TCanvas("Timing", "timing")

# Range and bins for the window for TH1 objects
xbins = 500
bin_range = 15000

# Between each combination of LGADs, require to have at least 200 entries
min_entries_per_run = 200

def timingPlots():

    print "\nStart producing TIMING plots, batches:", md.batchNumbers

    for batchNumber in md.batchNumbers:
    
        dm.defineDataFolderPath()
        
        runNumbers = md.getAllRunNumbers(batchNumber)
        numpy_arrays = [np.empty(0, dtype = dm.getDTYPE(batchNumber)) for _ in range(4)]
        
        # have to redefine two of the numpy arrays, since they are three-dim!
        # A futurewarning is set here, which is not taken care of!
        numpy_arrays[2] = numpy_arrays[2].astype(t_calc.getDTYPESysEq())
        numpy_arrays[3] = numpy_arrays[3].astype(t_calc.getDTYPESysEq())
        
        var_names = ["linear", "linear_cfd", "sys_eq", "sys_eq_cfd"]
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers
    
        for runNumber in runNumbers:
        
            md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
            
            if runNumber not in md.getRunsWithSensor(md.sensor):
                continue
        
            for index in range(0, len(var_names)):
                if var_names[index].find("sys") != -1 and md.getBatchNumber()/100 == 6:
                    continue
                else:
                    numpy_arrays[index] = np.concatenate((numpy_arrays[index], dm.exportImportROOTData("timing", var_names[index], False)), axis = 0)

        if numpy_arrays[0].size != 0:
        
            for index in range(0, len(var_names)):
                if var_names[index].find("sys") != -1 and md.getBatchNumber()/100 == 6:
                    continue
                else:
                    cfd = True if var_names[index].find("cfd") != -1 else False
                    sys = True if var_names[index].find("sys") != -1 else False

                    produceTimingDistributionPlots(numpy_arrays[index], cfd, sys)



    print "\nDone with producing TIMING RESOLUTION plots.\n"


############## LINEAR TIME DIFFERENCE ###############

def produceTimingDistributionPlots(time_difference, cfd=False, sys=False):
    
    if sys:
        produceTimingDistributionPlotsSysEq(time_difference, cfd)
        return 0
    
    text = "\nTIMING RESOLUTION NORMAL PEAK PLOTS Batch " + str(md.getBatchNumber())
    if cfd:
        text.replace("PEAK", "CFD")

    print text
    
    time_diff_th1d = dict()

    for chan in time_difference.dtype.names:
    
        # Omit SiPM, since the time difference is between the SiPM and DUT
        if md.getNameOfSensor(chan) == "SiPM-AFP":
            continue
        
        # Omit sensors which are not analyzed (defined in main.py)
        if md.getNameOfSensor(chan) != md.sensor and md.sensor != "":
            continue
        
        print "\n", md.getNameOfSensor(chan), "\n"

        time_diff_th1d[chan] = ROOT.TH1D("Time difference "+md.getNameOfSensor(chan), "time_difference" + chan, xbins, -bin_range, bin_range)
     
        # Fill the objects, without cuts on the SiPM
        for entry in range(0, len(time_difference[chan])):
            if time_difference[chan][entry] != 0:
                time_diff_th1d[chan].Fill(time_difference[chan][entry])

        # Get fit function with width of the distributions
        # Check if the filled object have at least 200 entries per run
        
        if time_diff_th1d[chan].GetEntries() < min_entries_per_run * len(md.getAllRunNumbers(md.getBatchNumber())):
            
            if cfd:
                type = "cfd reference"
            
            else:
                type = "peak reference"
                
            print "Omitting sensor", md.getNameOfSensor(chan), "for", type, "due to low statistics. \n"
            
            continue
            
        sigma_DUT, sigma_fit_error, time_diff_mean = t_calc.getSigmasFromFit(time_diff_th1d[chan], chan)

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
        timing_results = np.empty(3, dtype = dt)
        timing_results[type][0] = sigma_DUT
        timing_results[type][1] = sigma_fit_error
        timing_results[type][2] = time_diff_mean
        
        dm.exportImportROOTData("results", "timing_normal", True, timing_results, chan, md.checkIfSameOscAsSiPM(chan), cfd)

        del time_diff_th1d[chan]


############## SYSTEM OF EQUATIONS ###############


# Use this method to calculate the linear system of equations solution
# If one of the functions have less than 1000 entries, remove it from the calculation!
def produceTimingDistributionPlotsSysEq(time_difference, cfd=False):
    
    text = "\nTIMING RESOLUTION SYSTEM PEAK PLOTS Batch " + str(md.getBatchNumber())
    if cfd:
        text.replace("PEAK", "CFD")
    
    print text
    
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
            window_range = 3000
            
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

            if time_diff_th1d[chan][chan2].GetEntries() < min_entries_per_run * len(md.getAllRunNumbers(md.getBatchNumber())):
            
                if cfd:
                    type = "cfd reference"
                else:
                    type = "peak reference"
                
                print "Omitting batch", md.getBatchNumber(), "for", type, "time difference system plot for", md.getNameOfSensor(chan), "and", md.getNameOfSensor(chan2), "due to low statistics \n"
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

            del time_diff_th1d[chan][chan2]
            
        # Export the results

        dm.exportImportROOTData("results", "timing_system", True, timing_results_sys_eq, chan, False, cfd)


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


