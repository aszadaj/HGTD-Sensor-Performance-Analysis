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
xbins = 2000 # default 2000
bin_range = 15000
window_range = 1000

# Between each combination of LGADs, require to have at least 200 entries
min_entries_per_run = 200

def timingPlots():

    print "\nStart producing TIMING plots, batches:", md.batchNumbers

    for batchNumber in md.batchNumbers:
    
        dm.defineDataFolderPath()
        
        runNumbers = md.getAllRunNumbers(batchNumber)
        # Create numpy arrays for linear time difference (one element per "channel")
        numpy_arrays = [np.empty(0, dtype = dm.getDTYPE(batchNumber)) for _ in range(2)]

        # Create numpy arrays for system of equations (three elements per "channel")
        numpy_arrays.append(np.empty(0, dtype = t_calc.getDTYPESysEq()))
        numpy_arrays.append(np.empty(0, dtype = t_calc.getDTYPESysEq()))

        var_names = ["linear", "linear_cfd", "system", "system_cfd"]
    
        for runNumber in runNumbers:
        
            md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
            
            if runNumber not in md.getRunsWithSensor(md.sensor) or runNumber in [3697, 3698, 3701]:
                continue
        
            for index in range(0, len(var_names)):
            
                # omit batch 60X for solving system of equations
                if var_names[index].find("system") != -1 and md.getBatchNumber()/100 == 6:
                    continue
                
                else:
                    numpy_arrays[index] = np.concatenate((numpy_arrays[index], dm.exportImportROOTData("timing", var_names[index])), axis = 0)

        if numpy_arrays[0].size != 0:
            
            for index in range(0, len(var_names)):
            
                # omit batch 60X for solving system of equations
                if var_names[index].find("system") != -1 and md.getBatchNumber()/100 == 6:
                    continue
                
                else:
                    produceTimingDistributionPlots(numpy_arrays[index], var_names[index])


    print "\nDone with producing TIMING RESOLUTION plots.\n"


############## LINEAR TIME DIFFERENCE ###############

def produceTimingDistributionPlots(time_difference, category):

    if category.find("system") != -1:
    
        # Comment this function if you want to omit producing plots for system of equations
        produceTimingDistributionPlotsSysEq(time_difference, category)
        return 0

    text = "\nTIMING RESOLUTION NORMAL PEAK PLOTS Batch " + str(md.getBatchNumber()) + "\n"

    if category.find("cfd") != -1:
        text = text.replace("PEAK", "CFD")

    print text
    
    time_diff_th1d = dict()

    for chan in time_difference.dtype.names:
        md.setChannelName(chan)

        # Omit sensors which are not analyzed (defined in main.py)
        if (md.getNameOfSensor(chan) != md.sensor and md.sensor != "") or md.getNameOfSensor(chan) == "SiPM-AFP":
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
            
            if category.find("cfd") != -1:
                type = "cfd reference"
            
            else:
                type = "peak reference"
                
            print "Omitting sensor", md.getNameOfSensor(chan), "for", type, "due to low statistics. \n"
            
            continue
            
        sigma_DUT, sigma_fit_error, time_diff_mean = t_calc.getSigmasFromFit(time_diff_th1d[chan], window_range, chan)

        # Set titles and export file
        headTitle = "Time difference SiPM and "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"
        xAxisTitle = "\Deltat [ps]"
        yAxisTitle = "Entries"
        fileName = dm.getSourceFolderPath() + dm.getPlotsSourceFolder()+"/"+md.getNameOfSensor(chan)+"/timing/normal/peak/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+"_diff_osc_peak.pdf"

        if md.checkIfSameOscAsSiPM(chan):
            fileName = fileName.replace("diff_osc", "same_osc")

        if category.find("cfd") != -1:
            fileName = fileName.replace("peak", "cfd")



        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportTHPlot(time_diff_th1d[chan], titles, chan, [sigma_DUT, sigma_fit_error] )


        # Export the result together with its error
        dt = (  [(category, '<f8') ])
        timing_results = np.empty(3, dtype = dt)
        timing_results[category][0] = sigma_DUT
        timing_results[category][1] = sigma_fit_error
        timing_results[category][2] = time_diff_mean
        
        dm.exportImportROOTData("results", category, timing_results)



############## SYSTEM OF EQUATIONS ###############


# Use this method to calculate the linear system of equations solution
# If one of the functions have less than 1000 entries, remove it from the calculation!
def produceTimingDistributionPlotsSysEq(time_difference, category):
    
    text = "\nTIMING RESOLUTION SYSTEM PEAK PLOTS Batch " + str(md.getBatchNumber()) + "\n"
  
    if category.find("cfd") != -1:
        text = text.replace("PEAK", "CFD")
    
    print text
    
    
    # TH1 objects
    time_diff_th1d = dict()
    
    omit_batch = False
    
    channels_1st_oscilloscope   = ["chan0", "chan1", "chan2", "chan3"]
    sigma_convoluted            = np.zeros((4,4))
    sigma_convoluted_error      = np.zeros((4,4))
    
    # First loop, calculate the sigmas for each combination of time differences
    for chan in channels_1st_oscilloscope:
        md.setChannelName(chan)
    
        print md.getNameOfSensor(chan), "\n"
        
        # Do not consider the same channel when comparing two
        chan2_list = list(channels_1st_oscilloscope)
        chan2_list.remove(chan)
        
        # Create TH1 object
        time_diff_th1d[chan] = dict()
        for chan2 in chan2_list:
            time_diff_th1d[chan][chan2] = ROOT.TH1D("System of equations \sigma_{"+chan[-1]+chan2[-1]+"}", "time_difference" + chan, xbins, -bin_range, bin_range)
        
        # Fill TH1 object between channels in first oscilloscope
        for entry in range(0, len(time_difference[chan])):
            for index in range(0, len(chan2_list)):
                chan2 = chan2_list[index]

                if time_difference[chan][entry][0][index] != 0:
                    time_diff_th1d[chan][chan2].Fill(time_difference[chan][entry][0][index])
    
    

        # Get sigma and adapt distribution curve
        for chan2 in chan2_list:
      
            # Find the maximal value
            MPV_bin = time_diff_th1d[chan][chan2].GetMaximumBin()
            MPV_time_diff = int(time_diff_th1d[chan][chan2].GetXaxis().GetBinCenter(MPV_bin))

            
            xMin = MPV_time_diff - window_range
            xMax = MPV_time_diff + window_range
            time_diff_th1d[chan][chan2].SetAxisRange(xMin, xMax)

            # Redefine range for the fit
            N = 3
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
                sigma_convoluted[i][j]  = fit_function.GetParameter(2)
                sigma_convoluted_error[i][j] = fit_function.GetParError(2)
            
            except:
            
                sigma_convoluted[i][j] = sigma_convoluted[j][i] = 0
                sigma_convoluted_error[i][j] = sigma_convoluted_error[j][i] = 0

    # Second loop, check if all combined plots have at least 1000 entries
    
    for chan in channels_1st_oscilloscope:
    
        md.setChannelName(chan)
        
        if omit_batch:
            break
        
        # Do not consider the same channel when comparing two
        chan2_list = list(channels_1st_oscilloscope)
        chan2_list.remove(chan)
        
        for chan2 in chan2_list:

            if time_diff_th1d[chan][chan2].GetEntries() < min_entries_per_run * len(md.getAllRunNumbers(md.getBatchNumber())):
            
                if category.find("cfd") != -1:
                    type = "cfd reference"
                else:
                    type = "peak reference"
                
                print "Omitting batch", md.getBatchNumber(), "for", type, "time difference system plot for", md.getNameOfSensor(chan), "and", md.getNameOfSensor(chan2), "due to low statistics \n"
                omit_batch = True
                break
                

    # Solve the system
    if not omit_batch:
        sigmas_chan, sigmas_error = t_calc.solveSystemOfEqs(sigma_convoluted, sigma_convoluted_error)

    # Third loop, print the graphs together with the solutions
    for chan in channels_1st_oscilloscope:
    
        md.setChannelName(chan)
        
        # This is in case the condition of requiring at least 1000 entries for each plots is not fulfilled
        if omit_batch:
            break
    
        chan2_list = list(channels_1st_oscilloscope)
        chan2_list.remove(chan)
        
        dt = ([(category, '<f8')])
        timing_results_sys_eq = np.empty(2, dtype = dt)
        
        # Loop through the combinations
        for chan2 in chan2_list:

            # Create titles and print the graph
            headTitle = "Time difference "+md.getNameOfSensor(chan)+" and "+md.getNameOfSensor(chan2)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"
            xAxisTitle = "\Deltat [ps]"
            yAxisTitle = "Entries"
            fileName = dm.getSourceFolderPath() + dm.getPlotsSourceFolder()+"/"+md.getNameOfSensor(chan)+"/timing/system/peak/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+"_and_"+str(md.getNameOfSensor(chan2))+"_peak.pdf"

            if category.find("cfd") != -1:
                fileName = fileName.replace("peak", "cfd")
        

            index = int(chan[-1]) % 4
            sigma_DUT = sigmas_chan[index]
            sigma_DUT_error = sigmas_error[index]

            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
            exportTHPlot(time_diff_th1d[chan][chan2], titles, chan, [sigma_DUT, sigma_DUT_error])

            timing_results_sys_eq[category][0] = sigma_DUT
            timing_results_sys_eq[category][1] = sigma_DUT_error

        # Export the results
        dm.exportImportROOTData("results", category, timing_results_sys_eq)


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
    dm.exportImportROOTHistogram(titles[3], graphList)


