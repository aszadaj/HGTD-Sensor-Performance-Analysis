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
    
    dm.defineDataFolderPath()
    
    for batchNumber in md.batchNumbers:
        
        print "Batch", batchNumber,"\n"
        
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
     
            print "Importing run", md.getRunNumber(), "\n"

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
        
            print "Done with importing files for", batchNumber, "producing plots.\n"
            
            producePulsePlots(peak_values, rise_times, points, max_sample, cfd05, peak_time)

    print "Done with producing PULSE plots.\n"


# Fill TH1 objects
def producePulsePlots(peak_values, rise_times, points, max_sample, cfd05, peak_time):

    global canvas
    
    # Limit of the oscilloscope
    osc_limit = 350
    
    peak_values = dm.convertPulseData(peak_values)
    max_sample = dm.convertPulseData(max_sample)
    rise_times = dm.convertRiseTimeData(rise_times)


    canvas = ROOT.TCanvas("Pulse", "pulse")

    channels = peak_values.dtype.names
    
    # Select only a certain sensor to be plotted
    #channels = [x for x in channels if md.getNameOfSensor(x) == "50D-GBGR2"]
    #channels = ["chan3"]

    for chan in channels:
 
        peak_values_th1d    = ROOT.TH1D("Pulse amplitude", "peak_value" + chan, 100, 0, 500)
        rise_times_th1d     = ROOT.TH1D("Rise time", "rise_time" + chan, 600, 0, 4000)
        point_count_th1d     = ROOT.TH1D("Point count", "point_count" + chan, 100, 0, 100)
        max_sample_th1d     = ROOT.TH1D("Max sample", "max_sample" + chan, 100, 0, 360)
        cfd05_th1d     = ROOT.TH1D("CFD05", "CFD05_plot" + chan, 100, 0, 100)
        peak_time_th1d     = ROOT.TH1D("Peak time", "peak_time" + chan, 100, 0, 100)
        max_sample_vs_points_threshold_th2d = ROOT.TH2D("Max sample vs no of points", "amp_vs_points", 80, 0, 80, 100, 0, 200)

        for entry in range(0, len(peak_values[chan])):
   
            if peak_values[chan][entry] != 0 and peak_values[chan][entry] < osc_limit:
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


        max_sample_vs_points_threshold_th2d.ResetStats()
        max_sample_vs_points_threshold_th2d.SetAxisRange(0, 500, "Z")


        N = 4
        bin_max_rise_time = rise_times_th1d.GetMaximumBin()
        max_value_rise_time = rise_times_th1d.GetBinCenter(bin_max_rise_time)
        xMin = max_value_rise_time - N * rise_times_th1d.GetStdDev()
        xMax = max_value_rise_time + N * rise_times_th1d.GetStdDev()
        rise_times_th1d.SetAxisRange(xMin, xMax)

        N = 1
        bin_max_rise_time = rise_times_th1d.GetMaximumBin()
        max_value_rise_time = rise_times_th1d.GetBinCenter(bin_max_rise_time)
        xMin = max_value_rise_time - N * rise_times_th1d.GetStdDev()
        xMax = max_value_rise_time + N * rise_times_th1d.GetStdDev()
        rise_times_th1d.Fit("gaus", "Q", "", xMin, xMax)
        fit_params_rise_time = rise_times_th1d.GetFunction("gaus").GetParameters()

        
        
        # Create convoluted fit for max amplitude
        bin_max = peak_values_th1d.GetMaximumBin()
        most_prob_value = int(peak_values_th1d.GetBinCenter(bin_max))
        mean_value = peak_values_th1d.GetMean()
        std_dev = peak_values_th1d.GetStdDev()
        amplitude = peak_values_th1d.GetMaximum()
        integral = peak_values_th1d.Integral()
        
        N = 0.8
        xMin = most_prob_value - N * std_dev
        xMax = most_prob_value + N * std_dev
        
        fit_function_convolution = ROOT.TF1("gaus_landau", "landau(0) + gaus(3)", xMin, 350)
        fit_function_convolution.SetParameters(integral, most_prob_value, mean_value/9.0, amplitude, mean_value, std_dev)
        fit_function_convolution.SetParNames("Constant (L)", "MPV", "Scale","Constant (G)", "Mean value", "Sigma")
        peak_values_th1d.Fit("gaus_landau", "QR")
        

        # Define plot information

        yAxisTitle = "Entries"

        # Print maximum amplitude plots
        headTitle = "Pulse amplitude - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
        xAxisTitle = "Pulse amplitude [mV]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_value/pulse_amplitude_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(peak_values_th1d, titles)


        # Print rise time plots
        headTitle = "Rise time - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"
        xAxisTitle = "Rise time [ps]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/rise_time/rise_time_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
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
        
        # Print cfd05  plots
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


        # Export results to root file
        peak_value_result = np.empty(2, dtype=[('peak_value', '<f8')])
        rise_time_result    = np.empty(2, dtype=[('rise_time', '<f8')])

        peak_value_MPV   = peak_values_th1d.GetFunction("gaus_landau").GetParameter(1)
        peak_value_error = peak_values_th1d.GetFunction("gaus_landau").GetParError(1)

        rise_time_mean = rise_times_th1d.GetFunction("gaus").GetParameter(1)
        rise_time_error = rise_times_th1d.GetFunction("gaus").GetParError(1)

        peak_value_result["peak_value"][0] = peak_value_MPV
        peak_value_result["peak_value"][1] = peak_value_error

        rise_time_result["rise_time"][0] = rise_time_mean
        rise_time_result["rise_time"][1] = rise_time_error

        sensor_info = [md.getNameOfSensor(chan), chan]
        dm.exportPulseResults(peak_value_result, rise_time_result, sensor_info)

    del canvas

# Produce histograms
def exportHistogram(graphList, titles):

    ROOT.gStyle.SetOptStat("ne")
    ROOT.gStyle.SetOptFit(0012)
    
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    graphList.Draw()

  
    canvas.Update()
    canvas.Print(titles[3])
    dm.exportROOTHistogram(graphList, titles[3])


def exportHistogram2D(graphList, titles):

    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    # Move the stats box


    graphList.Draw("COLZ")
    canvas.Update()

    stats_box = graphList.GetListOfFunctions().FindObject("stats")
    stats_box.SetX1NDC(0.1)
    stats_box.SetX2NDC(0.3)
    stats_box.SetY1NDC(0.93)
    stats_box.SetY2NDC(0.83)
    
    # Recreate stats box
    stats_box.SetOptStat(1000000011)



    canvas.Print(titles[3])


    
