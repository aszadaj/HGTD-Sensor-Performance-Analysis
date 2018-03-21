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

    peak_times_th1d = dict()
    peak_values_th1d = dict()
    rise_times_th1d = dict()
    
    xbins_amplitude = 120
    
    xbins_rise_time = 400
    
    xbins_times = 200
    
    channels = peak_times.dtype.names
    
    channels = ["chan5"]

    for chan in channels:

        peak_times_th1d[chan] = ROOT.TH1D("Time location", "peak_time" + chan, xbins_times, 30, 70)
        peak_values_th1d[chan] = ROOT.TH1D("Max amplitude", "peak_value" + chan, xbins_amplitude, 0, 350)
        rise_times_th1d[chan] = ROOT.TH1D("Rise time", "rise_time" + chan, xbins_rise_time, 0, 3)

        for entry in range(0, len(peak_times[chan])):
   
            if peak_times[chan][entry] != 0:
                peak_times_th1d[chan].Fill(peak_times[chan][entry])
            
            if peak_values[chan][entry] != 0:
                peak_values_th1d[chan].Fill(peak_values[chan][entry])
            
            if rise_times[chan][entry] != 0:
                rise_times_th1d[chan].Fill(rise_times[chan][entry])
    
        # Choose the range for the fits, rise time fit
        N = 2
        xMin = rise_times_th1d[chan].GetMean() - N * rise_times_th1d[chan].GetStdDev()
        xMax = rise_times_th1d[chan].GetMean() + N * rise_times_th1d[chan].GetStdDev()
        
        # Perform the fit for rise time
        rise_times_th1d[chan].Fit("gaus", "Q", "", xMin, xMax)
        
        N = 4
        xMin = rise_times_th1d[chan].GetMean() - N * rise_times_th1d[chan].GetStdDev()
        xMax = rise_times_th1d[chan].GetMean() + N * rise_times_th1d[chan].GetStdDev()
        
        rise_time_fit = rise_times_th1d[chan].GetFunction("gaus")
        rise_times_th1d[chan].SetAxisRange(xMin, xMax)
        rise_time_fit.SetRange(xMin, xMax)
        
        
        # Create convoluted fit for max amplitude
        
        bin_max = peak_values_th1d[chan].GetMaximumBin()
        most_prob_value = int(peak_values_th1d[chan].GetBinCenter(bin_max))
        mean_value = peak_values_th1d[chan].GetMean()
        std_dev = peak_values_th1d[chan].GetStdDev()
        amplitude = peak_values_th1d[chan].GetMaximum()
        integral = peak_values_th1d[chan].Integral()


        fit_function_convolution = ROOT.TF1("gaus_landau", "landau(0) + gaus(3)", 0, 300)
        fit_function_convolution.SetParameters(integral, most_prob_value, 6, amplitude, mean_value, std_dev)
        fit_function_convolution.SetParNames("LConstant", "L\mu", "LScale","GConstant", "GMean", "G\sigma")
        peak_values_th1d[chan].Fit("gaus_landau", "Q")
        
        ROOT.gStyle.SetOptFit()
    
        
        # Print maximum amplitude plots
        headTitle = "Maximum amplitudes, "+md.getNameOfSensor(chan)+", B"+str(md.getBatchNumber())
        xAxisTitle = "Max amplitude (mV)"
        yAxisTitle = "Number of entries (N)"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_value_plots/pulse_amplitude_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(peak_values_th1d[chan], titles)
        
        
        # Print rise time plots
        headTitle = "Rise time, "+md.getNameOfSensor(chan)+", B"+str(md.getBatchNumber())
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Number of entries (N)"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/rise_time_plots/rise_time_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        #exportHistogram(rise_times_th1d[chan], titles)


        ROOT.gStyle.SetOptFit(0)

        # Print time location plot
        headTitle = "Time at peak location, "+md.getNameOfSensor(chan)+", B"+str(md.getBatchNumber())
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Number (N)"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_time_plots/time_reference_peak_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        #exportHistogram(peak_times_th1d[chan], titles)


# Produce histograms
def exportHistogram(graphList, titles):
    
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    
    graphList.Draw()
  
    canvas.Update()
    canvas.Print(titles[3])
