import ROOT
import numpy as np

import run_log_metadata as md
import data_management as dm


ROOT.gStyle.SetOptFit(1)
ROOT.gStyle.SetOptStat(1)
ROOT.gInterpreter.ProcessLine('#include "langaus.c"')
ROOT.gROOT.SetBatch(True)

canvas = ROOT.TCanvas("Pulse", "pulse")

# Amplitude limit for the oscilloscope
osc_limit = 345


def pulsePlots():

    print "\nStart producing PULSE plots, batches:", md.batchNumbers
    
    dm.defineDataFolderPath()
    
    for batchNumber in md.batchNumbers:
        
        firstRun = True

        runNumbers = md.getAllRunNumbers(batchNumber)
        
        numpy_arrays = [np.empty(0, dtype = dm.getDTYPE(batchNumber)) for _ in range(7)]
        var_names = ["peak_value", "rise_time", "charge", "peak_time", "cfd", "points", "max_sample"]
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers
    
        for runNumber in runNumbers:
            
            md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
            
            if runNumber not in md.getRunsWithSensor(md.sensor):
                continue

            for index in range(0, len(var_names)):
                numpy_arrays[index] = np.concatenate((numpy_arrays[index], dm.exportImportROOTData("pulse", var_names[index], False)), axis = 0)


        if len(numpy_arrays[0]) != 0:
            producePulsePlots(numpy_arrays)

    print "Done with producing PULSE plots.\n"


# Fill TH1 objects
def producePulsePlots(numpy_variables):

    global chan

    
    [peak_value, rise_time, charge, peak_time, cfd, points, max_sample] = [i for i in numpy_variables]

    print np.size(peak_value)

    dm.changeIndexNumpyArray(peak_value, -1000)
    dm.changeIndexNumpyArray(max_sample, -1000)
    dm.changeIndexNumpyArray(rise_time, 1000)
    dm.changeIndexNumpyArray(charge, 10**15)
    
    for chan in peak_value.dtype.names:
        
        if md.sensor != "" and md.getNameOfSensor(chan) != md.sensor:
            continue
    
        print "\nPULSE PLOTS: Batch", md.getBatchNumber(),"sensor", md.getNameOfSensor(chan), chan, "\n"
        
        # Create and fill objects with values
        peak_value_th1d                    = ROOT.TH1F("Pulse amplitude", "peak_value", 80, 0, 500)
        rise_time_th1d                     = ROOT.TH1F("Rise time", "rise_time", 300, 0, 4000)
        charge_th1d                         = ROOT.TH1F("Charge", "charge", 25, 0, 500)
        peak_time_th1d                      = ROOT.TH1F("Peak time", "peak_time", 100, 0, 100)
        cfd_th1d                            = ROOT.TH1F("CFD", "cfd", 100, 0, 100)
        max_sample_th1d                     = ROOT.TH1F("Max sample", "max_sample", 100, 0, 360)
        point_count_th1d                    = ROOT.TH1F("Point count", "point_count", 100, 0, 100)
        max_sample_vs_points_threshold_th2d = ROOT.TH2D("Max sample vs points", "max_sample_vs_point_count", 80, 0, 100, 100, 0, 350)
        
        TH1_objects = [peak_value_th1d, rise_time_th1d, charge_th1d, peak_time_th1d, cfd_th1d, max_sample_th1d, point_count_th1d]
        
        for index in range(0, len(TH1_objects)):
            for entry in range(0, len(numpy_variables[index][chan])):
                if numpy_variables[index][chan][entry] != 0:
                    TH1_objects[index].Fill(numpy_variables[index][chan][entry])

        
        for entry in range(0, len(peak_value[chan])):
            if max_sample[chan][entry] != 0 and points[chan][entry] != 0:
                max_sample_vs_points_threshold_th2d.Fill(points[entry][chan], max_sample[entry][chan])

      
        rise_time_fit = makeRiseTimeFit(rise_time_th1d)
        pulse_amplitude_langaufit = makeLandauGausFit(peak_value_th1d, osc_limit)
        charge_langaufit = makeLandauGausFit(charge_th1d)
      
        for TH_obj in TH1_objects:
            exportHistogram(TH_obj)

        # Export results
        
        peak_mpv_error = [pulse_amplitude_langaufit.GetParameter(1), pulse_amplitude_langaufit.GetParError(1)]
        rise_time_mpv_error = [rise_time_fit.GetParameter(1), rise_time_fit.GetParError(1)]
        charge_mpv_error = [charge_langaufit.GetParameter(1), charge_langaufit.GetParError(1)]
        
        exportResults(peak_mpv_error, charge_mpv_error, rise_time_mpv_error)


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


def makeLandauGausFit(graphList, osc_limit=0):
    
    # Create parameters for landau (*) gaus fit for CHARGE distribution
    std_dev = graphList.GetStdDev()
    integral = graphList.Integral()
    MPV_bin = graphList.GetMaximumBin()
    MPV = graphList.GetBinCenter(MPV_bin)
    
    # Set range for fit
    xMin = max((MPV - std_dev), 4.0)
    
    if graphList.GetTitle == "charge":
        xMax = graphList.GetXaxis().GetXmax()
    
    else:
        xMax = osc_limit
        graphList.SetAxisRange(0, osc_limit)
    
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

    return ROOT.langaufit(graphList, fit_range, start_values, param_limits_low, param_limits_high)


def exportResults(peak_mpv_error, charge_mpv_error, rise_time_mpv_error):

        peak_value_result   = np.empty(2, dtype=[('peak_value', '<f8')])
        charge_result       = np.empty(2, dtype=[('charge', '<f8')])
        rise_time_result    = np.empty(2, dtype=[('rise_time', '<f8')])
        
        peak_value_result['peak_value'] = peak_mpv_error
        charge_result['charge']         = charge_mpv_error
        rise_time_result['rise_time']   = rise_time_mpv_error
        
        dm.exportPulseResults(peak_value_result, charge_result, rise_time_result, chan)


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
    
        graphList.SetAxisRange(0, 60, "X")
        graphList.SetAxisRange(0, 350, "Y")
        graphList.SetAxisRange(0, 500, "Z")
        
        # Redefine the stats box
        stats_box = graphList.GetListOfFunctions().FindObject("stats")
        stats_box.SetX1NDC(0.65)
        stats_box.SetX2NDC(0.9)
        stats_box.SetY1NDC(0.93)
        stats_box.SetY2NDC(0.83)
        stats_box.SetOptStat(1000000011)


    canvas.Print(titles[3])
    dm.exportImportROOTHistogram(titles[3], True, graphList)




def getPlotAttributes(name):

    
    if name.find("peak_value") != -1:

        head_title_type = "Pulse amplitude"
        xAxisTitle = "Pulse amplitude [mV]"
 
    elif name.find("rise_time") != -1:

        head_title_type = "Rise time"
        xAxisTitle = "Rise time [ps]"


    elif name.find("point_count") != -1:

        head_title_type = "Point count over threshold"
        xAxisTitle = "Point count over threshold [N]"


    elif name.find("max_sample") != -1:

        head_title_type = "Max sample in event over threshold"
        xAxisTitle = "Max sample in event [mV]"


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


    headTitle = head_title_type + " - " + md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/"+name+"/"+name+"_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    return [headTitle, xAxisTitle, "Entries", fileName]

