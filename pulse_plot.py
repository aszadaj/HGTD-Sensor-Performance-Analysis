import ROOT
import numpy as np

import pulse_main as p_main
import run_log_metadata as md
import data_management as dm


ROOT.gStyle.SetOptFit(1)
ROOT.gStyle.SetOptStat(1)
ROOT.gInterpreter.ProcessLine('#include "langaus.c"')
ROOT.gROOT.SetBatch(True)

canvas = ROOT.TCanvas("Pulse", "pulse")

# Amplitude limit for the fit function
signal_limit = 340


def pulsePlots():

    print "\nStart producing PULSE plots, batches:", md.batchNumbers, "\n"
    
    for batchNumber in md.batchNumbers:
    
        p_main.defineNameOfProperties()
        
        runNumbers = md.getAllRunNumbers(batchNumber)
        
        numpy_arrays = [np.empty(0, dtype = dm.getDTYPE(batchNumber)) for _ in range(len(p_main.var_names))]
 
        for runNumber in runNumbers:
            
            md.defineRunInfo(md.getRowForRunNumber(runNumber))
            
            if runNumber not in md.getRunsWithSensor():
                continue
        
            for index in range(0, len(p_main.var_names)):
                numpy_arrays[index] = np.concatenate((numpy_arrays[index], dm.exportImportROOTData("pulse", p_main.var_names[index])), axis = 0)


        if len(numpy_arrays[0]) != 0:
            producePulsePlots(numpy_arrays)

    print "Done with producing PULSE plots.\n"


def producePulsePlots(numpy_variables):

    [noise, pedestal, pulse_amplitude, rise_time, charge, cfd, peak_time, points, max_sample] = [i for i in numpy_variables]
    
    dm.changeIndexNumpyArray(noise, 1000.0)
    dm.changeIndexNumpyArray(pedestal, -1000.0)
    dm.changeIndexNumpyArray(pulse_amplitude, -1000.0)
    dm.changeIndexNumpyArray(rise_time, 1000.0)
    dm.changeIndexNumpyArray(charge, 10**15)
    dm.changeIndexNumpyArray(max_sample, -1000.0)
    
    print "\nBATCH", md.getBatchNumber(), "\n"
   
   
    for chan in pulse_amplitude.dtype.names:
    
        md.setChannelName(chan)
        
        if md.sensor != "" and md.getSensor() != md.sensor:
            continue

        # if a fit fails, slightly change the bin number
        pulse_amplitude_bins = 120
        point_count_limit = 50
        charge_pulse_bins = 140
        rise_time_bins = 300
        charge_max = 150
        
        
        # This is a limit for the point count, to increase it
        if md.getSensor() == "SiPM-AFP" or md.getSensor() == "W4-RD01":
            point_count_limit = 100
            charge_max = 500

        
        print md.getSensor(), "\n"

        noise_avg_std    = [np.average(noise[chan]), np.std(noise[chan])]
        pedestal_avg_std = [np.average(pedestal[chan]), np.std(pedestal[chan])]
        
        noise_ranges, pedestal_ranges = getRanges(noise_avg_std, pedestal_avg_std, 6)
        
 
        # Create TH objects with properties to be analyzed
        
        th_name = "_"+str(md.getBatchNumber())+"_"+md.chan_name
        
        noise_TH1F                          = ROOT.TH1F("noise"+th_name, "noise", 300, noise_ranges[0], noise_ranges[1])
        pedestal_TH1F                       = ROOT.TH1F("pedestal"+th_name, "pedestal", 300, pedestal_ranges[0], pedestal_ranges[1])
        
        pulse_amplitude_TH1F                = ROOT.TH1F("pulse_amplitude"+th_name, "pulse_amplitude", pulse_amplitude_bins, 0, 500)
        rise_time_TH1F                      = ROOT.TH1F("rise_time"+th_name, "rise_time", rise_time_bins, 0, 4000)
        charge_TH1F                         = ROOT.TH1F("charge"+th_name, "charge", charge_pulse_bins, 0, charge_max)
        
        # Additional TH objects for inspection of signals
        peak_time_TH1F                      = ROOT.TH1F("peak_time"+th_name, "peak_time", 100, 0, 100)
        cfd_TH1F                            = ROOT.TH1F("cfd"+th_name, "cfd", 100, 0, 100)
        point_count_TH1F                    = ROOT.TH1F("point_count"+th_name, "point_count", point_count_limit, 0, point_count_limit)
        max_sample_TH1F                     = ROOT.TH1F("max_sample"+th_name, "max_sample", 100, 0, 400)
        max_sample_vs_points_threshold_TH2F = ROOT.TH2F("max_sample_vs_point_count"+th_name, "max_sample_vs_point_count", point_count_limit, 0, point_count_limit, 100, 0, 400)
        

        TH1_objects = [noise_TH1F, pedestal_TH1F, pulse_amplitude_TH1F, rise_time_TH1F, charge_TH1F, peak_time_TH1F, cfd_TH1F, point_count_TH1F, max_sample_TH1F]
        
        # Fill TH1 objects
        for index in range(0, len(TH1_objects)):
            for entry in range(0, len(numpy_variables[index][chan])):
                if numpy_variables[index][chan][entry] != 0:
                    TH1_objects[index].Fill(numpy_variables[index][chan][entry])

        # Fill TH2 object
        for entry in range(0, len(pulse_amplitude[chan])):
            if max_sample[chan][entry] != 0 and points[chan][entry] != 0:
                max_sample_vs_points_threshold_TH2F.Fill(points[entry][chan], max_sample[entry][chan])


        # Redefine ranges for noise and pedestal fits
        ranges_noise_pedestal = getRanges(noise_avg_std, pedestal_avg_std, 3)

        # Create fits
        noise_fit, pedestal_fit = makeNoisePedestalFits(noise_TH1F, pedestal_TH1F, ranges_noise_pedestal)
        pulse_amplitude_langaufit = makeLandauGausFit(pulse_amplitude_TH1F, signal_limit)
        rise_time_fit = makeRiseTimeFit(rise_time_TH1F)
        charge_langaufit = makeLandauGausFit(charge_TH1F)

        # Export plots
        for TH_obj in TH1_objects:
            exportHistogram(TH_obj)

        exportHistogram(max_sample_vs_points_threshold_TH2F)


def makeNoisePedestalFits(noise_TH1F, pedestal_TH1F, ranges):
    
    noise_TH1F.Fit("gaus","Q","", ranges[0][0], ranges[0][1])
    pedestal_TH1F.Fit("gaus","Q","", ranges[1][0], ranges[1][1])

    return noise_TH1F.GetFunction("gaus"), pedestal_TH1F.GetFunction("gaus")


def makeRiseTimeFit(th1_object):

    # Change window for rise time values
    bin_max_rise_time = th1_object.GetMaximumBin()
    max_value_rise_time = th1_object.GetBinCenter(bin_max_rise_time)
    window_range = 1000
    xMin = max_value_rise_time - window_range
    xMax = max_value_rise_time + window_range
    th1_object.SetAxisRange(xMin, xMax)

    # Select range for the fit for rise time plot
    xMin = max_value_rise_time - th1_object.GetStdDev()
    xMax = max_value_rise_time + th1_object.GetStdDev()
    th1_object.Fit("gaus", "Q", "", xMin, xMax)

    return th1_object.GetFunction("gaus")


def makeLandauGausFit(th1_object, signal_limit=0):
    
    if th1_object.GetTitle() == "charge":
        xMax = th1_object.GetXaxis().GetXmax()
    
    else:
        xMax = signal_limit
        th1_object.SetAxisRange(0, xMax)
    
    # Create parameters for landau (*) gaus fit for CHARGE distribution
    std_dev = th1_object.GetStdDev()
    integral = th1_object.Integral()
    MPV_bin = th1_object.GetMaximumBin()
    MPV = th1_object.GetBinCenter(MPV_bin)
    
    # Set range for fit
    xMin = max((MPV - std_dev), 0)

    # Define range of fit, limits for parameters
    # Parameters for gaus(*)landau - fit
    # 1. Width/constant of the landau fit
    # 2. Most proble value
    # 3. Area, normalization constant
    # 4. Width of the gaus fit
    
    fit_range = np.array([xMin, xMax])
    start_values = np.array([std_dev, MPV, integral, std_dev])
    param_limits_low = np.multiply(np.array([std_dev, MPV, integral, std_dev]), 0.1)
    param_limits_high = np.multiply(param_limits_low, 100)

    langauFit = ROOT.langaufit(th1_object, fit_range, start_values, param_limits_low, param_limits_high)

    if th1_object.GetTitle() == "pulse_amplitude":
        th1_object.SetAxisRange(0, 500)

    return langauFit


def getRanges(noise_avg_std, pedestal_avg_std, N):

    noise_ranges = [noise_avg_std[0] - N * noise_avg_std[1], noise_avg_std[0] + N * noise_avg_std[1]]
    pedestal_ranges = [pedestal_avg_std[0] - N * pedestal_avg_std[1], pedestal_avg_std[0] + N * pedestal_avg_std[1]]

    return noise_ranges, pedestal_ranges



# Produce histograms
def exportHistogram(th1_object):

    canvas.Clear()
    category = th1_object.GetTitle()
    titles = getPlotAttributes(category)
    drawOpt = "COLZ"
    
    if category != "max_sample_vs_point_count":
        ROOT.gStyle.SetOptStat("ne")
        ROOT.gStyle.SetOptFit(0012)
        th1_object.SetLineColor(1)
        drawOpt = ""
    
    
    # Move the margins to make place for legend on left axis
    canvas.SetLeftMargin(0.11)

    th1_object.SetTitle(titles[0]+";"+titles[1]+";"+titles[2])

    th1_object.Draw(drawOpt)
    canvas.Update()
    
    if category == "max_sample_vs_point_count":
        # Move the margins to make place for legend on right axis
        canvas.SetRightMargin(0.14)
    
        th1_object.SetAxisRange(0, 500, "Z")
    
        # Redefine the stats box
        stats_box = th1_object.GetListOfFunctions().FindObject("stats")
        stats_box.SetX1NDC(0.65)
        stats_box.SetX2NDC(0.85)
        stats_box.SetY1NDC(0.93)
        stats_box.SetY2NDC(0.83)
        stats_box.SetOptStat(1000000011)

        headTitle = titles[0]+";"+titles[1]+";"+titles[2]+";Entries"
        th1_object.SetTitle(headTitle)

        canvas.Update()


    canvas.Print(titles[3])
    dm.exportImportROOTHistogram("pulse", category, "", "", th1_object)


def getPlotAttributes(category):

    yAxisTitle = "Entries"
    
    if category.find("noise") != -1:

        head_title_type = "Noise"
        xAxisTitle = "Standard deviation [mV]"
 
    elif category.find("pedestal") != -1:

        head_title_type = "Pedestal"
        xAxisTitle = "Average value [mV]"
    
    elif category.find("pulse_amplitude") != -1:

        head_title_type = "Pulse amplitude"
        xAxisTitle = "Pulse amplitude [mV]"
 
    elif category.find("rise_time") != -1:

        head_title_type = "Rise time"
        xAxisTitle = "Rise time [ps]"


    elif category.find("cfd") != -1:

        head_title_type = "CFD time location"
        xAxisTitle = "Time location [ns]"


    elif category.find("peak_time") != -1:

        head_title_type = "Peak time location"
        xAxisTitle = "Time location [ns]"


    elif category.find("charge") != -1:

        head_title_type = "Charge distribution"
        xAxisTitle = "Charge [fC]"


    elif category.find("max_sample_vs_point_count") != -1:

        head_title_type = "Maximum sample value vs number of samples above the threshold"
        xAxisTitle = "Number of samples [N]"
        yAxisTitle = "Maximum sample value [mV]"

    elif category.find("max_sample") != -1:

        head_title_type = "Maximum sample value above the threshold"
        xAxisTitle = "Maximum sample value [mV]"


    elif category.find("point_count") != -1:

        head_title_type = "Samples above the threshold"
        xAxisTitle = "Number of samples [N]"

    
    headTitle = head_title_type + " - " + md.getSensor()+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage()) + " V"

    fileName = dm.getFileNameForHistogram("pulse", category)

    return [headTitle, xAxisTitle, yAxisTitle, fileName]


