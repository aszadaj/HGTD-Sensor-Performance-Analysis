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

# Amplitude limit for the oscilloscope in mV
signal_limit = 340


def pulsePlots():

    print "\nStart producing PULSE plots, batches:", md.batchNumbers, "\n"
    
    dm.defineDataFolderPath()
    
    for batchNumber in md.batchNumbers:
    
        p_main.defineNameOfProperties()
        
        runNumbers = md.getAllRunNumbers(batchNumber)
        
        numpy_arrays = [np.empty(0, dtype = dm.getDTYPE(batchNumber)) for _ in range(len(p_main.var_names))]
 
        for runNumber in runNumbers:
            
            md.defineRunInfo(md.getRowForRunNumber(runNumber))
            p_main.defineNameOfProperties()
            
            if runNumber not in md.getRunsWithSensor():
                continue
        
            for index in range(0, len(p_main.var_names)):
                numpy_arrays[index] = np.concatenate((numpy_arrays[index], dm.exportImportROOTData("pulse", p_main.var_names[index])), axis = 0)


        if len(numpy_arrays[0]) != 0:
            producePulsePlots(numpy_arrays)

    print "Done with producing PULSE plots.\n"


# Fill TH1 objects
def producePulsePlots(numpy_variables):

    [noise, pedestal, peak_value, rise_time, charge, cfd, peak_time, points, max_sample] = [i for i in numpy_variables]
    
    dm.changeIndexNumpyArray(noise, 1000)
    dm.changeIndexNumpyArray(pedestal, -1000)
    dm.changeIndexNumpyArray(peak_value, -1000)
    dm.changeIndexNumpyArray(rise_time, 1000)
    dm.changeIndexNumpyArray(charge, 10**15)
    dm.changeIndexNumpyArray(max_sample, -1000)
    
    print "\nBATCH", md.getBatchNumber(), "\n"
   
   
    for chan in peak_value.dtype.names:
    
        md.setChannelName(chan)
        
        if md.sensor != "" and md.getSensor() != md.sensor:
            continue

        point_count_limit = 50
        charge_pulse_bins = 150
        rise_time_bins = 300
        
        # This is a limit for the point count, to increase it
        if md.getSensor() == "SiPM-AFP" or md.getSensor() == "W4-RD01":
            point_count_limit = 100
        
        print md.getSensor(), "\n"
        
        noise_avg_std, pedestal_avg_std = getAvgStd(noise, pedestal)
        noise_ranges, pedestal_ranges = getRanges(noise_avg_std, pedestal_avg_std, 6)
        
        # Create TH objects with properties to be analyzed
        noise_TH1F                          = ROOT.TH1F("Noise"+" "+str(md.getBatchNumber())+" "+md.chan_name, "noise", 300, noise_ranges[0], noise_ranges[1])
        pedestal_TH1F                       = ROOT.TH1F("Pedestal"+" "+str(md.getBatchNumber())+" "+md.chan_name, "pedestal", 300, pedestal_ranges[0], pedestal_ranges[1])
        
        peak_value_TH1F                     = ROOT.TH1F("Pulse amplitude"+" "+str(md.getBatchNumber())+" "+md.chan_name, "peak_value", charge_pulse_bins, 0, 500)
        rise_time_TH1F                      = ROOT.TH1F("Rise time"+" "+str(md.getBatchNumber())+" "+md.chan_name, "rise_time", rise_time_bins, 0, 4000)
        charge_TH1F                         = ROOT.TH1F("Charge"+" "+str(md.getBatchNumber())+" "+md.chan_name, "charge", charge_pulse_bins, 0, 500)
        
        # Additional TH objects for inspection of signals
        peak_time_TH1F                      = ROOT.TH1F("Peak time"+" "+str(md.getBatchNumber())+" "+md.chan_name, "peak_time", 100, 0, 100)
        cfd_TH1F                            = ROOT.TH1F("CFD"+" "+str(md.getBatchNumber())+" "+md.chan_name, "cfd", 100, 0, 100)
        point_count_TH1F                    = ROOT.TH1F("Point count"+" "+str(md.getBatchNumber())+" "+md.chan_name, "point_count", point_count_limit, 0, point_count_limit)
        max_sample_TH1F                     = ROOT.TH1F("Max sample"+" "+str(md.getBatchNumber())+" "+md.chan_name, "max_sample", 100, 0, 400)
        max_sample_vs_points_threshold_TH2F = ROOT.TH2F("Max sample vs points"+" "+str(md.getBatchNumber())+" "+md.chan_name, "max_sample_vs_point_count", point_count_limit, 0, point_count_limit, 100, 0, 400)
        

        TH1_objects = [noise_TH1F, pedestal_TH1F, peak_value_TH1F, rise_time_TH1F, charge_TH1F, peak_time_TH1F, cfd_TH1F, point_count_TH1F, max_sample_TH1F]
        
        # Fill TH1 objects
        for index in range(0, len(TH1_objects)):
            for entry in range(0, len(numpy_variables[index][chan])):
                if numpy_variables[index][chan][entry] != 0:
                    TH1_objects[index].Fill(numpy_variables[index][chan][entry])

        # Fill TH2 object
        for entry in range(0, len(peak_value[chan])):
            if max_sample[chan][entry] != 0 and points[chan][entry] != 0:
                max_sample_vs_points_threshold_TH2F.Fill(points[entry][chan], max_sample[entry][chan])


        # Create fits for pulse amplitude, rise time and charge
        # Redefine ranges for noise and pedestal fits
        ranges_noise_pedestal = getRanges(noise_avg_std, pedestal_avg_std, 3)
        
        noise_fit, pedestal_fit = makeNoisePedestalFits(noise_TH1F, pedestal_TH1F, ranges_noise_pedestal)
        pulse_amplitude_langaufit = makeLandauGausFit(peak_value_TH1F, signal_limit)
        rise_time_fit = makeRiseTimeFit(rise_time_TH1F)
        charge_langaufit = makeLandauGausFit(charge_TH1F)


        # Export plots
        for TH_obj in TH1_objects:
            exportHistogram(TH_obj)

        exportHistogram(max_sample_vs_points_threshold_TH2F)

        # Export results
        exportResults([noise_fit, pedestal_fit, pulse_amplitude_langaufit, rise_time_fit, charge_langaufit])

        del noise_TH1F, pedestal_TH1F, peak_value_TH1F, rise_time_TH1F, charge_TH1F, peak_time_TH1F, cfd_TH1F, point_count_TH1F, max_sample_TH1F



def makeNoisePedestalFits(noise_TH1F, pedestal_TH1F, ranges):
    
    noise_TH1F.Fit("gaus","Q","", ranges[0][0], ranges[0][1])
    pedestal_TH1F.Fit("gaus","Q","", ranges[1][0], ranges[1][1])

    return noise_TH1F.GetFunction("gaus"), pedestal_TH1F.GetFunction("gaus")



def makeRiseTimeFit(graphList):

    # Change window for rise time values
    bin_max_rise_time = graphList.GetMaximumBin()
    max_value_rise_time = graphList.GetBinCenter(bin_max_rise_time)
    window_range = 1000
    xMin = max_value_rise_time - window_range
    xMax = max_value_rise_time + window_range
    graphList.SetAxisRange(xMin, xMax)

    # Select range for the fit for rise time plot
    xMin = max_value_rise_time - graphList.GetStdDev()
    xMax = max_value_rise_time + graphList.GetStdDev()
    graphList.Fit("gaus", "Q", "", xMin, xMax)

    return graphList.GetFunction("gaus")


def makeLandauGausFit(graphList, signal_limit=0):
    
    if graphList.GetTitle() == "charge":
        xMax = graphList.GetXaxis().GetXmax()
    
    else:
        xMax = signal_limit
        graphList.SetAxisRange(0, signal_limit)
    
    # Create parameters for landau (*) gaus fit for CHARGE distribution
    std_dev = graphList.GetStdDev()
    integral = graphList.Integral()
    MPV_bin = graphList.GetMaximumBin()
    MPV = graphList.GetBinCenter(MPV_bin)
    
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

    langauFit = ROOT.langaufit(graphList, fit_range, start_values, param_limits_low, param_limits_high)

    if graphList.GetTitle() == "peak_value":
        graphList.SetAxisRange(0, 500)

    return langauFit



def getAvgStd(noise_std, noise_average):
    
    noise_avg   = np.average(noise_std[md.chan_name][np.nonzero(noise_std[md.chan_name])])
    noise_std  = np.std(noise_std[md.chan_name][np.nonzero(noise_std[md.chan_name])])
    
    pedestal_avg = np.average(noise_average[md.chan_name][np.nonzero(noise_average[md.chan_name])])
    pedestal_std  = np.std(noise_average[md.chan_name][np.nonzero(noise_average[md.chan_name])])

    return [noise_avg, noise_std], [pedestal_avg, pedestal_std]


def getRanges(noise_avg_std, pedestal_avg_std, N):

    noise_ranges = [noise_avg_std[0] - N * noise_avg_std[1], noise_avg_std[0] + N * noise_avg_std[1]]
    pedestal_ranges = [pedestal_avg_std[0] - N * pedestal_avg_std[1], pedestal_avg_std[0] + N * pedestal_avg_std[1]]

    return noise_ranges, pedestal_ranges


def exportResults(tf1_fit):

    [noise_fit, pedestal_fit, pulse_amplitude_langaufit, rise_time_fit, charge_langaufit] = [i for i in tf1_fit]

    noise_mean_error = [noise_fit.GetParameter(1), noise_fit.GetParError(1)]
    pedestal_mean_error = [pedestal_fit.GetParameter(1), pedestal_fit.GetParError(1)]

    peak_mpv_error = [pulse_amplitude_langaufit.GetParameter(1), pulse_amplitude_langaufit.GetParError(1)]
    rise_time_mpv_error = [rise_time_fit.GetParameter(1), rise_time_fit.GetParError(1)]
    charge_mpv_error = [charge_langaufit.GetParameter(1), charge_langaufit.GetParError(1)]

    noise_result   = np.empty(2, dtype=[('noise', '<f8')])
    pedestal_result   = np.empty(2, dtype=[('pedestal', '<f8')])
    
    peak_value_result   = np.empty(2, dtype=[('peak_value', '<f8')])
    rise_time_result    = np.empty(2, dtype=[('rise_time', '<f8')])
    charge_result       = np.empty(2, dtype=[('charge', '<f8')])
    
    noise_result['noise'] = noise_mean_error
    pedestal_result['pedestal'] = pedestal_mean_error
    
    peak_value_result['peak_value'] = peak_mpv_error
    rise_time_result['rise_time']   = rise_time_mpv_error
    charge_result['charge']         = charge_mpv_error
    
    p_main.defineNameOfProperties(True)
    
    var_numpy = [noise_result, pedestal_result, peak_value_result, rise_time_result, charge_result]
    
    for index in range(0, len(p_main.var_names)):
        dm.exportImportROOTData("results", p_main.var_names[index], var_numpy[index])


# Produce histograms
def exportHistogram(graphList):

    canvas.Clear()
    name = graphList.GetTitle()
    titles = getPlotAttributes(name)
    drawOpt = "COLZ"
    
    if name != "max_sample_vs_point_count":
        ROOT.gStyle.SetOptStat("ne")
        ROOT.gStyle.SetOptFit(0012)
        graphList.SetLineColor(1)
        drawOpt = ""
    
    if name == "peak_value":
        graphList.SetAxisRange(0, 500)
    
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])

    graphList.Draw(drawOpt)
    canvas.Update()
    
    if name == "max_sample_vs_point_count":
    
        graphList.SetAxisRange(0, 500, "Z")
    
        # Redefine the stats box
        stats_box = graphList.GetListOfFunctions().FindObject("stats")
        stats_box.SetX1NDC(0.65)
        stats_box.SetX2NDC(0.9)
        stats_box.SetY1NDC(0.93)
        stats_box.SetY2NDC(0.83)
        stats_box.SetOptStat(1000000011)


    canvas.Print(titles[3])
    dm.exportImportROOTHistogram(titles[3], graphList)


def getPlotAttributes(name):

    yAxisTitle = "Entries"
    
    if name.find("noise") != -1:

        head_title_type = "Noise"
        xAxisTitle = "Standard deviation [mV]"
 
    elif name.find("pedestal") != -1:

        head_title_type = "Pedestal"
        xAxisTitle = "Average value [mV]"
    
    elif name.find("peak_value") != -1:

        head_title_type = "Pulse amplitude"
        xAxisTitle = "Pulse amplitude [mV]"
 
    elif name.find("rise_time") != -1:

        head_title_type = "Rise time"
        xAxisTitle = "Rise time [ps]"


    elif name.find("cfd") != -1:

        head_title_type = "CFD time location"
        xAxisTitle = "Time location [ns]"


    elif name.find("peak_time") != -1:

        head_title_type = "Peak time location"
        xAxisTitle = "Time location [ns]"


    elif name.find("charge") != -1:

        head_title_type = "Charge distribution"
        xAxisTitle = "Charge [fC]"


    elif name.find("max_sample_vs_point_count") != -1:

        head_title_type = "Max sample point vs number of points over threshold"
        xAxisTitle = "Number points > threshold"
        yAxisTitle = "Max sample point [mV]"

    elif name.find("max_sample") != -1:

        head_title_type = "Max sample in event over threshold"
        xAxisTitle = "Max sample in event [mV]"


    elif name.find("point_count") != -1:

        head_title_type = "Point count over threshold"
        xAxisTitle = "Point count over threshold [N]"

    

    headTitle = head_title_type + " - " + md.getSensor()+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage()) + " V"
    fileName = dm.getSourceFolderPath() + dm.getPlotsSourceFolder()+"/"+md.getSensor()+"/pulse/"+name+"/"+name+"_"+str(md.getBatchNumber())+"_"+md.chan_name+ "_"+str(md.getSensor())+".pdf"
    
    return [headTitle, xAxisTitle, yAxisTitle, fileName]
