import ROOT
import metadata as md
import numpy as np
import data_management as dm

ROOT.gStyle.SetOptFit(1)
ROOT.gStyle.SetOptStat(1)

# Concatenate all runs for each batch. When the files are concatenated, produce plots for that batch until
# all batches are considered.

def pulsePlots():

    print "\nStart producing PULSE plots, batches:", md.batchNumbers
    
    for batchNumber in md.batchNumbers:
        
        print "Batch", batchNumber,"\n"
        
        dm.checkIfRepositoryOnStau()
        
        peak_values = np.empty(0)
        rise_times = np.empty(0)
        peak_time = np.empty(0)
        cfd05 = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers
        
        availableRunNumbersPeakValues   = md.readFileNames("pulse_peak_value")
        availableRunNumbersRiseTimes    = md.readFileNames("pulse_rise_time")
    
        for runNumber in runNumbers:
            
            if runNumber in availableRunNumbersPeakValues:
                md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
          
                print "Importing run", md.getRunNumber(), "\n"

                if peak_values.size == 0:
          
                    peak_values = dm.importPulseFile("peak_value")
                    rise_times  = dm.importPulseFile("rise_time")
                    peak_time  = dm.importPulseFile("peak_time")
                    cfd05  = dm.importPulseFile("cfd05")
                

                else:

                    peak_values = np.concatenate((peak_values, dm.importPulseFile("peak_value")), axis = 0)
                    rise_times = np.concatenate((rise_times, dm.importPulseFile("rise_time")), axis = 0)
                    peak_time = np.concatenate((peak_time, dm.importPulseFile("peak_time")), axis = 0)
                    cfd05 = np.concatenate((cfd05, dm.importPulseFile("cfd05")), axis = 0)
                
                    
        if len(peak_values) != 0:
        
            print "Done with importing files for", batchNumber, "producing plots.\n"

            producePulsePlots(peak_values, rise_times, peak_time, cfd05, batchNumber)

    print "Done with producing PULSE plots.\n"


# Fill TH1 objects
def producePulsePlots(peak_values, rise_times, peak_time, cfd05, batchNumber):

    global canvas
    
    peak_values = dm.convertPulseData(peak_values)
    rise_times = dm.convertRiseTimeData(rise_times)
    
    # Continue investigating the rise time plot
    
    
    canvas = ROOT.TCanvas("Pulse", "pulse")

    peak_values_th1d = dict()
    rise_times_th1d = dict()
    peak_time_th1d = dict()
    cfd05_th1d = dict()
    
    xbins_amplitude = 120
    
    xbins_rise_time = 400
    
    xbins_cfd05 = 400
    
    xbins_peak_time = 400
    
    channels = peak_values.dtype.names
    
    
    #channels = ["chan3","chan5"]

    for chan in channels:
    
        amplitude_average = np.average(peak_values[chan][np.nonzero(peak_values[chan])])+500
        
        xbin_max_rise_time = 1200
        
        peak_values_th1d[chan] = ROOT.TH1D("Max amplitude", "peak_value" + chan, xbins_amplitude, 0, amplitude_average)
        rise_times_th1d[chan] = ROOT.TH1D("Rise time", "rise_time" + chan, xbins_rise_time, 0, xbin_max_rise_time)
        
        peak_time_th1d[chan] = ROOT.TH1D("Peak time", "peak_time" + chan, xbins_peak_time, 0, 100)

        cfd05_th1d[chan] = ROOT.TH1D("CFD05 Ref", "cfd05" + chan, xbins_cfd05, 0, 100)

        for entry in range(0, len(peak_values[chan])):
   
            if peak_values[chan][entry] != 0:
                peak_values_th1d[chan].Fill(peak_values[chan][entry])
            
            if rise_times[chan][entry] != 0:
                rise_times_th1d[chan].Fill(rise_times[chan][entry])
    
            if peak_time[chan][entry] != 0:
                peak_time_th1d[chan].Fill(peak_time[chan][entry])

            if cfd05[chan][entry] != 0:
                cfd05_th1d[chan].Fill(cfd05[chan][entry])
    
    
    
    
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
        fit_function_convolution.SetParameters(integral, most_prob_value, mean_value/10.0, amplitude, mean_value, std_dev)
        fit_function_convolution.SetParNames("LConstant", "L\mu", "LScale","GConstant", "GMean", "G\sigma")
        peak_values_th1d[chan].Fit("gaus_landau", "Q")


        yAxisTitle = "Entries"

        # Print maximum amplitude plots
        headTitle = "Maximum amplitudes, "+md.getNameOfSensor(chan)+", B"+str(md.getBatchNumber())
        xAxisTitle = "Max amplitude [mV]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_value_plots/pulse_amplitude_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(peak_values_th1d[chan], titles)
        
        
        # Print rise time plots
        headTitle = "Rise time, "+md.getNameOfSensor(chan)+", B"+str(md.getBatchNumber())
        xAxisTitle = "Rise time [ps]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/rise_time_plots/rise_time_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(rise_times_th1d[chan], titles)

        
        # Print peak time plots
        headTitle = "Peak time, "+md.getNameOfSensor(chan)+", B"+str(md.getBatchNumber())
        xAxisTitle = "Time [ns]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_time_plots/peak_time_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(peak_time_th1d[chan], titles)

        # Print cdf05 ref plots
        headTitle = "Time 50% crossing edge time, "+md.getNameOfSensor(chan)+", B"+str(md.getBatchNumber())
        xAxisTitle = "Time [ns]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/cfd05_plots/cfd05_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(cfd05_th1d[chan], titles)
        
        
        pulse_max_amplitude_MPV_fit = peak_values_th1d[chan].GetFunction("gaus_landau").GetParameter(1)
        pulse_max_amplitude_mean_histogram = peak_values_th1d[chan].GetMean()
        
        
        rise_time_mean_fit = rise_times_th1d[chan].GetFunction("gaus").GetParameter(1)
        rise_time_mean_histogram = rise_times_th1d[chan].GetMean()

        dt = (  [('max_amplitude', '<f8', 2), ('rise_time', '<f8', 2) ])
        pulse_characteristics_results = np.empty(1, dtype=dt)
        
        pulse_characteristics_results["max_amplitude"][0] = np.array([pulse_max_amplitude_MPV_fit, pulse_max_amplitude_mean_histogram])
        pulse_characteristics_results["rise_time"][0] = np.array([rise_time_mean_fit, rise_time_mean_histogram])

        # Export results
        # Array structure
        # max_amplitude with MPV from fit and mean value from histogram
        # rise_time with mean from gaus fit and mean value from histogram
        sensor_info = [md.getNameOfSensor(chan), chan]
        dm.exportPulseResults(pulse_characteristics_results, sensor_info)


# Produce histograms
def exportHistogram(graphList, titles):
    
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])

    
    graphList.Draw()
  
    canvas.Update()
    canvas.Print(titles[3])
    dm.exportROOTHistogram(graphList, titles[3])

    
