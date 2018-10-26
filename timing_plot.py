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
window_range = 1000 # default 1000

# Between each combination of LGADs, require to have at least 200 entries
min_entries_per_run = 200

def timingPlots():

    print "\nStart producing TIMING RESOLUTION plots, batches:", md.batchNumbers

    global var_names
    
    for batchNumber in md.batchNumbers:

        runNumbers = md.getAllRunNumbers(batchNumber)
        # Create numpy arrays for linear time difference (one element per "channel")
        numpy_arrays = [np.empty(0, dtype = dm.getDTYPE(batchNumber)) for _ in range(2)]

        # Create numpy arrays for system of equations (three elements per "channel")
        numpy_arrays.append(np.empty(0, dtype = t_calc.getDTYPESysEq()))
        numpy_arrays.append(np.empty(0, dtype = t_calc.getDTYPESysEq()))

        var_names = ["normal_peak", "normal_cfd", "system_peak", "system_cfd"]
    
        for runNumber in runNumbers:
        
            md.defineRunInfo(md.getRowForRunNumber(runNumber))
            
            if runNumber not in md.getRunsWithSensor() or runNumber in [3697, 3698, 3701]:
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

    group = "timing"

    if category.find("system") != -1:

        # Comment this function if you want to omit producing plots for system of equations
        produceTimingDistributionPlotsSysEq(time_difference, category)
        return 0

    text = "\nLINEAR PEAK PLOTS BATCH " + str(md.getBatchNumber()) + "\n"

    if category.find("cfd") != -1:
        text = text.replace("PEAK", "CFD")

    print text
    
    time_diff_TH1F = dict()

    for chan in time_difference.dtype.names:
        
        md.setChannelName(chan)

        # Omit sensors which are not analyzed (defined in main.py)
        if (md.getSensor() != md.sensor and md.sensor != "") or md.getSensor() == "SiPM-AFP":
            continue
        
        print md.getSensor(), "\n"
        th_name = "_" + str(md.getBatchNumber()) + "_" + md.chan_name
        time_diff_TH1F[chan] = ROOT.TH1F(category+th_name, category, xbins, -bin_range, bin_range)
     
        # Fill the objects, without cuts on the SiPM
        for entry in range(0, len(time_difference[chan])):
            
            if time_difference[chan][entry] != 0:
                time_diff_TH1F[chan].Fill(time_difference[chan][entry])

        # Get fit function with width of the distributions
        # Check if the filled object have at least 200 entries per run
        
        if time_diff_TH1F[chan].GetEntries() < min_entries_per_run * len(md.getAllRunNumbers(md.getBatchNumber())):
            
            if category.find("cfd") != -1:
                type = "cfd reference"
            
            else:
                type = "peak reference"
                
            print "Omitting sensor", md.getSensor(), "for", type, "due to low statistics. \n"
            
            continue
            
        sigma_DUT, sigma_fit_error = t_calc.getSigmasFromFit(time_diff_TH1F[chan], window_range, chan)

        exportTHPlot(time_diff_TH1F[chan], [sigma_DUT, sigma_fit_error], category)


############## SYSTEM OF EQUATIONS ###############


# Use this method to calculate the linear system of equations solution
# If one of the functions have less than 1000 entries, remove it from the calculation!
def produceTimingDistributionPlotsSysEq(time_difference, category):
    
    text = "\nSYS. OF. EQS. PEAK PLOTS BATCH " + str(md.getBatchNumber()) + "\n"
  
    if category.find("cfd") != -1:
        text = text.replace("PEAK", "CFD")
    
    print text
    
    
    # TH1 objects
    time_diff_TH1F = dict()
    
    omit_batch = False

    channels_1st_oscilloscope   = ["chan0", "chan1", "chan2", "chan3"]

    sigma_convoluted            = np.zeros((4,4))
    sigma_convoluted_error      = np.zeros((4,4))
    
    # First loop, calculate the sigmas for each combination of time differences
    for chan in channels_1st_oscilloscope:
        
        md.setChannelName(chan)
    
        print md.getSensor(), "\n"
        
        # Do not consider the same channel when comparing two
        chan2_list = list(channels_1st_oscilloscope)
        chan2_list.remove(chan)
        
        # Create TH1 object
        time_diff_TH1F[chan] = dict()
        for chan2 in chan2_list:
            th_name = "_" + str(md.getBatchNumber()) + "_" + md.chan_name+chan2
            time_diff_TH1F[chan][chan2] = ROOT.TH1F(category+th_name, category, xbins, -bin_range, bin_range)
        
        # Fill TH1 object between channels in first oscilloscope
        for entry in range(0, len(time_difference[chan])):
            for index in range(0, len(chan2_list)):
                chan2 = chan2_list[index]

                if time_difference[chan][entry][0][index] != 0:
                    time_diff_TH1F[chan][chan2].Fill(time_difference[chan][entry][0][index])
    
    

        # Get sigma and adapt distribution curve
        for chan2 in chan2_list:
      
            # Find the maximal value
            MPV_bin = time_diff_TH1F[chan][chan2].GetMaximumBin()
            MPV_time_diff = int(time_diff_TH1F[chan][chan2].GetXaxis().GetBinCenter(MPV_bin))

            
            xMin = MPV_time_diff - window_range
            xMax = MPV_time_diff + window_range
            time_diff_TH1F[chan][chan2].SetAxisRange(xMin, xMax)

            # Redefine range for the fit
            N = 3
            sigma_window = time_diff_TH1F[chan][chan2].GetStdDev()
            mean_window = time_diff_TH1F[chan][chan2].GetMean()
            xMin = mean_window - N * sigma_window
            xMax = mean_window + N * sigma_window
          
            # Obtain the parameters
            time_diff_TH1F[chan][chan2].Fit("gaus", "Q", "", xMin, xMax)
            fit_function = time_diff_TH1F[chan][chan2].GetFunction("gaus")
          
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

            if time_diff_TH1F[chan][chan2].GetEntries() < min_entries_per_run * len(md.getAllRunNumbers(md.getBatchNumber())):
            
                if category.find("cfd") != -1:
                    type = "cfd reference"
                else:
                    type = "peak reference"
                
                print "Omitting batch", md.getBatchNumber(), "for", type, "time difference system plot for", md.getSensor(), "and", md.getSensor(chan2), "due to low statistics \n"
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


        # Loop through the combinations
        for chan2 in chan2_list:

            index = int(chan[-1]) % 4
            sigma_DUT = sigmas_chan[index]
            sigma_DUT_error = sigmas_error[index]

            exportTHPlot(time_diff_TH1F[chan][chan2], [sigma_DUT, sigma_DUT_error], category, chan2)


############## EXPORT PLOT ###############

def exportTHPlot(graphList, sigma, category, chan2 = ""):
    
    canvas.Clear()
    
    titles = getPlotAttributes(chan2)
 
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
    statsBox.AddText("\sigma_{"+md.getSensor()+"} = "+str(sigma[0])[0:6] + " \pm " + str(sigma[1])[0:4])
    canvas.Modified()
    canvas.Update()
    
    category, subcategory = getCategorySubcategory(category)
    
    fileName = dm.getFileNameForHistogram("timing", category, subcategory, chan2)
    
    canvas.Print(fileName)

    dm.exportImportROOTHistogram("timing", category, subcategory, chan2, graphList)


def getPlotAttributes(chan2=""):

    # Set titles and export file
    headTitle = "Time difference "+md.getSensor()+" and SiPM, T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage()) + " V"
    xAxisTitle = "\Deltat [ps]"
    yAxisTitle = "Entries"


    if chan2 != "":
        # Create titles and print the graph
        headTitle = "Time difference "+md.getSensor()+" and "+md.getSensor(chan2)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage()) + " V"


    return [headTitle, xAxisTitle, yAxisTitle]


def getCategorySubcategory(category_subcategory):
    
    subcategory = "peak"
    
    if category_subcategory.find("cfd") != -1:
        category = category_subcategory[:-4]
        subcategory = "cfd"
    else:
        category = category_subcategory[:-5]

    return category, subcategory
