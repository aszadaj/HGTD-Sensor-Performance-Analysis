import ROOT
import metadata as md
import numpy as np
import data_management as dm


# Concatenate all runs for each batch. When the files are concatenated, produce plots for that batch until
# all batches are considered.

def pulsePlots():

    print "\nStart producing PULSE plots, batches:", md.batchNumbers
    
    for batchNumber in md.batchNumbers:
        
        print "Batch", batchNumber,"\n"
        
        dm.checkIfRepositoryOnStau()
        
        peak_times = np.empty(0)
        peak_values = np.empty(0)
        rise_times = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers
        
        availableRunNumbersPeakTimes    = md.readFileNames("pulse_peak_time")
        availableRunNumbersPeakValues   = md.readFileNames("pulse_peak_value")
        availableRunNumbersRiseTimes    = md.readFileNames("pulse_rise_time")
    
        for runNumber in runNumbers:
            
            if runNumber in availableRunNumbersPeakTimes:
                md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
          
                print "Importing run", md.getRunNumber(), "\n"

                if peak_times.size == 0:
          
                    peak_times  = dm.importPulseFile("peak_time")
                    peak_values = dm.importPulseFile("peak_value")
                    rise_times  = dm.importPulseFile("rise_time")

                else:

                    peak_times = np.concatenate((peak_times, dm.importPulseFile("peak_time")), axis = 0)
                    peak_values = np.concatenate((peak_values, dm.importPulseFile("peak_value")), axis = 0)
                    rise_times = np.concatenate((rise_times, dm.importPulseFile("rise_time")), axis = 0)
                    
        if len(peak_times) != 0:
        
            print "Done with importing files for", batchNumber, "producing plots.\n"

            producePulsePlots(peak_times, peak_values, rise_times, batchNumber)

    print "Done with producing PULSE plots.\n"


# Fill TH1 objects
def producePulsePlots(peak_times, peak_values, rise_times, batchNumber):

    global canvas
    
    peak_values = dm.convertPulseData(peak_values)
    
    canvas = ROOT.TCanvas("Pulse", "pulse")

    peak_times_graph = dict()
    peak_values_graph = dict()
    rise_times_graph = dict()
    
    xbins = 300
    
    channels = peak_times.dtype.names
    
    #channels = ["chan0"]

    for chan in channels:

        peak_times_graph[chan] = ROOT.TH1D("Time location " + md.getNameOfSensor(chan), "peak_time" + chan, 800, 30, 70)
        peak_values_graph[chan] = ROOT.TH1D("Max amplitude " + md.getNameOfSensor(chan), "peak_value" + chan, 500, 0, 400)
        rise_times_graph[chan] = ROOT.TH1D("Rise time " + md.getNameOfSensor(chan), "rise_time" + chan, xbins, 0, 1.5)
        

        for entry in range(0, len(peak_times[chan])):
   
            if peak_times[chan][entry] != 0:
                peak_times_graph[chan].Fill(peak_times[chan][entry])
            
            if peak_values[chan][entry] != 0:
                peak_values_graph[chan].Fill(peak_values[chan][entry])
            
            if rise_times[chan][entry] != 0:
                rise_times_graph[chan].Fill(rise_times[chan][entry])
    
        # Choose the range for the fit (rise time plots)
        N = 2
        xMin = rise_times_graph[chan].GetMean() - N * rise_times_graph[chan].GetStdDev()
        xMax = rise_times_graph[chan].GetMean() + N * rise_times_graph[chan].GetStdDev()
        
        
        # Create a gaus distribution for rise time
        rise_times_graph[chan].Fit("gaus","0","", xMin, xMax)
        fit_function = rise_times_graph[chan].GetFunction("gaus")
        fitted_parameters = [fit_function.GetParameter(0), fit_function.GetParameter(1), fit_function.GetParameter(2)]
        
        # Rescale the ranges to plot along them
        N = 5
        xMin = rise_times_graph[chan].GetMean() - N * rise_times_graph[chan].GetStdDev()
        xMax = rise_times_graph[chan].GetMean() + N * rise_times_graph[chan].GetStdDev()
        
        # Print the fit function with the extracted parameters
        fit_function_adapted = ROOT.TF1("fit_peak_1", "gaus", xMin, xMax)
        fit_function_adapted.SetParameters(fitted_parameters[0], fitted_parameters[1], fitted_parameters[2])
        

        rise_times_graph[chan].SetAxisRange(xMin, xMax)

        # Print peak time, peak value and rise time graphs and export them
        headTitle = "Time at peak location "+md.getNameOfSensor(chan)+" B"+str(md.getBatchNumber())
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Number (N)"
        fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_time_plots/time_reference_peak_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(peak_times_graph[chan], titles)
        
        headTitle = "Maximum amplitudes "+md.getNameOfSensor(chan)+" B"+str(md.getBatchNumber())
        xAxisTitle = "Max amplitude (mV)"
        yAxisTitle = "Number of entries (N)"
        fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_value_plots/pulse_amplitude_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(peak_values_graph[chan], titles)
        
        headTitle = "Rise times "+md.getNameOfSensor(chan)+" B"+str(md.getBatchNumber())
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Number of entries (N)"
        fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/rise_time_plots/rise_time_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        ranges = [xMin, xMax]
        exportHistogram(rise_times_graph[chan], titles, ranges, fit_function_adapted)


# Produce histograms
def exportHistogram(graphList, titles, ranges=[], fit_function = False):
    
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    
    if ranges:
        graphList.SetAxisRange(ranges[0], ranges[1])
    
    graphList.Draw()
    
    if fit_function:
        ROOT.gStyle.SetOptStat("e")
        ROOT.gStyle.SetOptFit(0002)
        fit_function.Draw("SAME")
    else:
        ROOT.gStyle.SetOptStat("em")

    canvas.Update()
    canvas.Print(titles[3])
