import ROOT
import metadata as md
import numpy as np
import data_management as dm

ROOT.gStyle.SetOptFit(1)
ROOT.gStyle.SetOptStat(1)
ROOT.gInterpreter.ProcessLine('#include "langaus.c"')
ROOT.gROOT.ProcessLine("gErrorIgnoreLevel = 1001;")

canvas = ROOT.TCanvas("Pulse", "pulse")

# Amplitude limit for the oscilloscope
osc_limit = 345

def pulsePlots():

    print "\nStart producing PULSE plots, batches:", md.batchNumbers
    
    dm.defineDataFolderPath()
    
    for batchNumber in md.batchNumbers:
        
        peak_values = np.empty(0)
        rise_times = np.empty(0)
        points = np.empty(0)
        max_sample = np.empty(0)
        cfd05 = np.empty(0)
        peak_time = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers
    
        for runNumber in runNumbers:
            md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))

     
            if peak_values.size == 0:
      
                peak_values = dm.importPulseFile("peak_value")
                rise_times  = dm.importPulseFile("rise_time")
                points  = dm.importPulseFile("points")
                max_sample = dm.importPulseFile("max_sample")
                cfd05 = dm.importPulseFile("cfd05")
                peak_time = dm.importPulseFile("peak_time")

            else:

                peak_values = np.concatenate((peak_values, dm.importPulseFile("peak_value")), axis = 0)
                rise_times = np.concatenate((rise_times, dm.importPulseFile("rise_time")), axis = 0)
                points = np.concatenate((points, dm.importPulseFile("points")), axis = 0)
                max_sample = np.concatenate((max_sample, dm.importPulseFile("max_sample")), axis = 0)
                cfd05 = np.concatenate((cfd05, dm.importPulseFile("cfd05")), axis = 0)
                peak_time = np.concatenate((peak_time, dm.importPulseFile("peak_time")), axis = 0)
                

        if len(peak_values) != 0:
        
            producePulsePlots(peak_values, rise_times, points, max_sample, cfd05, peak_time)

    print "Done with producing PULSE plots.\n"


# Fill TH1 objects
def producePulsePlots(peak_values, rise_times, points, max_sample, cfd05, peak_time):

    peak_values = dm.convertPulseData(peak_values)
    max_sample = dm.convertPulseData(max_sample)
    rise_times = dm.convertRiseTimeData(rise_times)
    
    channels = peak_values.dtype.names
    
    for chan in channels:
        
        if md.getNameOfSensor(chan) == "SiPM-AFP":
            continue


        print "\nPULSE PLOTS: Batch", md.getBatchNumber(),"sensor", md.getNameOfSensor(chan), chan, "\n"
        
        # Create and fill objects with values
        peak_values_th1d   = ROOT.TH1F("Pulse amplitude", "peak_value", 92, 0, 500)
        rise_times_th1d    = ROOT.TH1F("Rise time", "rise_time", 300, 0, 4000)
        point_count_th1d   = ROOT.TH1F("Point count", "point_count", 100, 0, 100)
        max_sample_th1d    = ROOT.TH1F("Max sample", "max_sample", 100, 0, 360)
        cfd05_th1d         = ROOT.TH1F("CFD05", "CFD05_plot", 100, 0, 100)
        peak_time_th1d     = ROOT.TH1F("Peak time", "peak_time", 100, 0, 100)
        max_sample_vs_points_threshold_th2d = ROOT.TH2D("Max sample vs no of points", "amp_vs_points", 80, 0, 80, 100, 0, 200)
        
        for entry in range(0, len(peak_values[chan])):

            if peak_values[chan][entry] != 0:
                peak_values_th1d.Fill(peak_values[chan][entry])

            if rise_times[chan][entry] != 0:
                rise_times_th1d.Fill(rise_times[chan][entry])

            if points[chan][entry] != 0:
                point_count_th1d.Fill(points[chan][entry])

            if max_sample[chan][entry] != 0:
                max_sample_th1d.Fill(max_sample[chan][entry])

            if cfd05[chan][entry] != 0:
                cfd05_th1d.Fill(cfd05[chan][entry])

            if peak_time[chan][entry] != 0:
                peak_time_th1d.Fill(peak_time[chan][entry])

            if max_sample[chan][entry] != 0 and points[chan][entry] != 0:
                max_sample_vs_points_threshold_th2d.Fill(points[entry][chan], max_sample[entry][chan])

        max_sample_vs_points_threshold_th2d.SetAxisRange(0, 500, "Z")

        # Change window for rise time values
        bin_max_rise_time = rise_times_th1d.GetMaximumBin()
        max_value_rise_time = rise_times_th1d.GetBinCenter(bin_max_rise_time)
        window_range = 1000
        xMin = max_value_rise_time - window_range
        xMax = max_value_rise_time + window_range
        rise_times_th1d.SetAxisRange(xMin, xMax)

        # Select range for the fit for rise time plot
        xMin = max_value_rise_time - rise_times_th1d.GetStdDev()
        xMax = max_value_rise_time + rise_times_th1d.GetStdDev()
        rise_times_th1d.Fit("gaus", "Q", "", xMin, xMax)


        # Create parameters for landau (*) gaus fit
        peak_values_th1d.SetAxisRange(0, osc_limit)
        std_dev = peak_values_th1d.GetStdDev()
        integral = peak_values_th1d.Integral()
        MPV_bin = peak_values_th1d.GetMaximumBin()
        MPV_value = peak_values_th1d.GetBinCenter(MPV_bin)
        
        
        # Set range for fit
        xMin = max((MPV_value - std_dev), 5.0)
        xMax = osc_limit
        
        # Define range of fit, limits for parameters
        # Parameters for gaus(*)landau - fit
        # 1. Width/constant of the landau fit
        # 2. Most proble value
        # 3. Area, normalization constant
        # 4. Width of the gaus fit
        
        fit_range = np.array([xMin, xMax])
        start_values = np.array([std_dev, MPV_value, integral, std_dev])
        param_limits_low = np.array([std_dev*0.1, MPV_value*0.1, integral*0.1, std_dev*0.1])
        param_limits_high = np.array([std_dev*10, MPV_value*10, integral*10, std_dev*10])
        
        landau_gaus_fit_function = ROOT.langaufit(peak_values_th1d, fit_range, start_values, param_limits_low, param_limits_high)
        
        peak_values_th1d.SetAxisRange(0, 500)

        # Define and print plot titles for all types of TH objects
        yAxisTitle = "Entries"

        # Print maximum amplitude plots
        headTitle = "Pulse amplitude - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
        xAxisTitle = "Pulse amplitude [mV]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_value/pulse_amplitude_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        # Debug
        #fileName = "/Users/aszadaj/Desktop/debug/pulse_amplitude_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        values_peak_distribution = [landau_gaus_fit_function.GetMaximumX(), landau_gaus_fit_function.GetParError(1)]
        exportHistogram(peak_values_th1d, titles, values_peak_distribution, landau_gaus_fit_function)


        # Print rise time plots
        headTitle = "Rise time - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
        xAxisTitle = "Rise time [ps]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/rise_time/rise_time_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        # Debug
        #fileName = "/Users/aszadaj/Desktop/debug/rise_time_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(rise_times_th1d, titles)


        # Print point count plots
        headTitle = "Point count over threshold - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
        xAxisTitle = "Point count over threshold [N]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/point_count/point_count_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(point_count_th1d, titles)


        # Print max sample plots
        headTitle = "Max sample in event over threshold - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
        xAxisTitle = "Max sample in event [mV]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/max_sample/max_sample_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(max_sample_th1d, titles)

        # Print cfd05 plots
        headTitle = "CFD05 time locaiton - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
        xAxisTitle = "Time location [ns]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/cfd05/cfd05_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(cfd05_th1d, titles)


        # Print peak time plots
        headTitle = "Peak time locaiton - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
        xAxisTitle = "Time location [ns]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_time/peak_time_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(peak_time_th1d, titles)

        # Print th2d plot
        headTitle = "Max sample point vs no of points over threshold - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
        xAxisTitle = "Number points > threshold"
        yAxisTitle = "Max sample value [mV]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/max_sample_vs_point_count/amp_vs_points_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram2D(max_sample_vs_points_threshold_th2d, titles)
        
        getAndExportResults(landau_gaus_fit_function, rise_times_th1d, chan)



def getAndExportResults(fit_function, rise_times_th1d, chan):


        # Export results to root file
        peak_value_result   = np.empty(2, dtype=[('peak_value', '<f8')])
        rise_time_result    = np.empty(2, dtype=[('rise_time', '<f8')])

        # Here assume that the error is the same as with calculating the MPV in the fit
        peak_value_max   = fit_function.GetMaximumX()
        peak_value_error = fit_function.GetParError(1)

        rise_time_mean = rise_times_th1d.GetFunction("gaus").GetParameter(1)
        rise_time_error = rise_times_th1d.GetFunction("gaus").GetParError(1)

        peak_value_result["peak_value"][0] = peak_value_max
        peak_value_result["peak_value"][1] = peak_value_error

        rise_time_result["rise_time"][0] = rise_time_mean
        rise_time_result["rise_time"][1] = rise_time_error

        sensor_info = [md.getNameOfSensor(chan), chan]
        dm.exportPulseResults(peak_value_result, rise_time_result, sensor_info)


# Produce histograms
def exportHistogram(graphList, titles, values_peak_distribution = 0,  landau_gaus_fit = False):

    canvas.Clear()
    
    ROOT.gStyle.SetOptStat("ne")
    ROOT.gStyle.SetOptFit(0012)
    
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    graphList.Draw()
    canvas.Update()
    
    if landau_gaus_fit:

        landau_gaus_fit.Draw("lsame")
    
        # Add Peak value to the stats box
        statsBox = canvas.GetPrimitive("stats")
        statsBox.SetName("Mystats")
        graphList.SetStats(0)
        statsBox.AddText("Peak = "+str(values_peak_distribution[0])[0:5] + " \pm "+str(values_peak_distribution[1])[0:5])

    canvas.Print(titles[3])
    dm.exportROOTHistogram(graphList, titles[3])



def exportHistogram2D(graphList, titles):

    canvas.Clear()

    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    graphList.Draw("COLZ")
    canvas.Update()

    # Redefine the stats box
    stats_box = graphList.GetListOfFunctions().FindObject("stats")
    stats_box.SetX1NDC(0.1)
    stats_box.SetX2NDC(0.3)
    stats_box.SetY1NDC(0.93)
    stats_box.SetY2NDC(0.83)
    stats_box.SetOptStat(1000000011)

    canvas.Print(titles[3])

