import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md
import data_management as dm
import timing_calculations as t_calc
import tracking_calc as track_calc

ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(20)

def produceTrackingGraphs(peak_values, tracking, time_difference_peak, time_difference_cfd05):
   
    global canvas
    global bin_size
    global sep_x
    global sep_y
    global minEntries
    
    # Convert pulse data to positive mV values, and x and y positions into mm.
    peak_values = dm.convertPulseData(peak_values)
    position = dm.importTrackingFile("position")
    canvas = ROOT.TCanvas("Tracking", "tracking")

    # Bin size resolution of the MIMOSA
    bin_size = 18.5 * 0.001
    
    # Limits of the information where a hit from the MIMOSA is seen.
    # Also used to plot the sensor
    sep_x = 0.85
    sep_y = 0.65
    
    # Minimum entries in each bin
    minEntries = 3

    # In case there are arrays in batch, produce seperately array plots
    if md.checkIfArrayPad():
        produceArrayPlots(peak_values, np.copy(tracking), position, time_difference_peak, time_difference_cfd05)

    # Produce single pad plots
    for chan in peak_values.dtype.names:

        if md.checkIfArrayPad(chan) or md.getNameOfSensor(chan) == "SiPM-AFP":
            continue

        print "\nSingle pad", md.getNameOfSensor(chan), "\n"

        pos_x = position[chan][0][0]
        pos_y = position[chan][0][1]

        tracking_chan = track_calc.changeCenterPositionSensor(np.copy(tracking), pos_x, pos_y)

        produceTProfilePlots(peak_values[chan], tracking_chan, time_difference_peak[chan], time_difference_cfd05[chan], chan)
        produceEfficiencyPlot(peak_values[chan], tracking_chan, chan)


###########################################
#                                         #
#  MEAN VALUE AND TIME RESOLUTION GRAPHS  #
#                                         #
###########################################


# Produce mean value and time resolution plots
def produceTProfilePlots(peak_values, tracking, time_difference_peak, time_difference_cfd05, chan, array_pad=False):

    sep_x, sep_y, bin_size, minEntries = getSepGlobVar()
    
    if array_pad:
        sep_x *= 2
        sep_y *= 2

    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)
    
    
    timing_bin_increase = 2
    xbin_timing = int(xbin/timing_bin_increase)
    ybin_timing = int(ybin/timing_bin_increase)

    mean_values = dict()
    timing_resolution_peak = dict()
    timing_resolution_cfd05 = dict()

    timing_resolution_peak_copy = dict()
    timing_resolution_cfd05_copy = dict()
    

    mean_values[chan] = ROOT.TProfile2D("Mean value","Mean value", xbin, -sep_x, sep_x, ybin, -sep_y, sep_y)

    timing_resolution_peak[chan] = ROOT.TProfile2D("Timing resolution peak copy", "timing resolution peak temp", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y, "s")
    timing_resolution_cfd05[chan] = ROOT.TProfile2D("Timing resolution cdf05 copy", "timing resolution cdf05", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y, "s")

    timing_resolution_peak_copy[chan] = ROOT.TH2D("Timing resolution peak", "timing resolution peak", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)
    timing_resolution_cfd05_copy[chan] = ROOT.TH2D("Timing resolution cdf05", "timing resolution cdf05", xbin_timing, -sep_x, sep_x, ybin_timing, -sep_y, sep_y)

    # Fill mean values and time differences in each bin, for peak reference and rise time reference
    # If the sensor have more than one channel in each run, multiple tracking info is considered.
    if array_pad:
    
        for event in range(0, len(tracking)):
        
            for pad in range(0, len(peak_values[event])):
        
                if (-sep_x < tracking['X'][event] < sep_x) and (-sep_y < tracking['Y'][event] < sep_y):

                    mean_values[chan].Fill(tracking['X'][event], tracking['Y'][event], peak_values[event][pad])
                
                    if time_difference_peak[event][pad] != 0:

                        timing_resolution_peak[chan].Fill(tracking['X'][event], tracking['Y'][event], time_difference_peak[event][pad])

                    if time_difference_cfd05[event][pad] != 0:

                        timing_resolution_cfd05[chan].Fill(tracking['X'][event], tracking['Y'][event], time_difference_cfd05[event][pad])

    else:
    
        for event in range(0, len(tracking)):

            if (-sep_x < tracking['X'][event] < sep_x) and (-sep_y < tracking['Y'][event] < sep_y):

                if peak_values[event] > -md.getPulseAmplitudeCut(chan)*1000:
                
                    mean_values[chan].Fill(tracking['X'][event], tracking['Y'][event], peak_values[event])
                
                    if time_difference_peak[event] != 0:

                        timing_resolution_peak[chan].Fill(tracking['X'][event], tracking['Y'][event], time_difference_peak[event])

                    if time_difference_cfd05[event] != 0:

                        timing_resolution_cfd05[chan].Fill(tracking['X'][event], tracking['Y'][event], time_difference_cfd05[event])


    # Introduce the dependence on the SiPM time resolution if it is cooled or not
    sigma_sipm = md.getSigmaSiPM()
    
    # Filter bins and fill time resolution values
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
        
            bin = mean_values[chan].GetBin(i,j)
            num_mean = mean_values[chan].GetBinEntries(bin)
            num_time_peak = timing_resolution_peak[chan].GetBinEntries(bin)
            num_time_rtref = timing_resolution_cfd05[chan].GetBinEntries(bin)
            
            if 0 < num_mean < minEntries:
                mean_values[chan].SetBinContent(bin, 0)
                mean_values[chan].SetBinEntries(bin, 0)


    for i in range(1, xbin_timing+1):
        for j in range(1, ybin_timing+1):
        
            bin = timing_resolution_peak[chan].GetBin(i,j)
            num_time_peak = timing_resolution_peak[chan].GetBinEntries(bin)
            num_time_rtref = timing_resolution_cfd05[chan].GetBinEntries(bin)


            if num_time_peak > minEntries:
                sigma_dut_conv = timing_resolution_peak[chan].GetBinError(bin)

                if sigma_dut_conv > sigma_sipm:
                    sigma_dut = np.sqrt(sigma_dut_conv**2 - sigma_sipm**2)
                    timing_resolution_peak_copy[chan].SetBinContent(bin, sigma_dut)

            if num_time_rtref > minEntries:
                sigma_dut_conv_rt = timing_resolution_cfd05[chan].GetBinError(bin)
                
                if sigma_dut_conv_rt > sigma_sipm:
                    sigma_dut = np.sqrt(sigma_dut_conv_rt**2 - sigma_sipm**2)
                    timing_resolution_cfd05_copy[chan].SetBinContent(bin, sigma_dut)


    mean_values[chan].ResetStats()
    ROOT.gStyle.SetOptStat(1)

    totalEntries = mean_values[chan].GetEntries()

    # Print mean value 2D plot
    headTitle = "Mean pulse amplitude value - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+"; X [mm] ; Y [mm] ; V [mV]"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/mean_value/tracking_mean_value_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")
    titles = [headTitle, fileName, totalEntries]
    mean_values[chan].SetAxisRange(-md.getPulseAmplitudeCut(chan)*1000, mean_values[chan].GetMaximum(), "Z")
    mean_values[chan].SetNdivisions(10, "Z")
    printTHPlot(mean_values[chan], titles)


    # Print time resolution peak reference
    headTitle = "Time resolution (peak ref.) - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+"; X [mm] ; Y [mm] ; \sigma_{t} [ps]"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/time_resolution/tracking_time_resolution_peak_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")
    titles = [headTitle, fileName, totalEntries]
    timing_resolution_peak_copy[chan].SetAxisRange(0, 100, "Z")
    printTHPlot(timing_resolution_peak_copy[chan], titles)


    # Print time resolution rise time ref
    headTitle = "Time resolution (CFD ref) - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+"; X [mm] ; Y [mm] ; \sigma_{t} [ps]"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/time_resolution/tracking_time_resolution_cfd05_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")
    titles = [headTitle, fileName, totalEntries]
    timing_resolution_cfd05_copy[chan].SetAxisRange(0, 100, "Z")
    printTHPlot(timing_resolution_cfd05_copy[chan], titles)


###########################################
#                                         #
#           EFFICIENCY GRAPHS             #
#                                         #
###########################################


# Produce efficiency graphs (for array and single pads) and projection histograms (single pad arrays only)
def produceEfficiencyPlot(peak_values, tracking, chan, array_pad=False):


    sep_x, sep_y, bin_size, minEntries = getSepGlobVar()

    if array_pad:
        sep_x *= 2
        sep_y *= 2

    xbin = int(2*sep_x/bin_size)
    ybin = int(2*sep_y/bin_size)
    
    
    LGAD = dict()
    MIMOSA = dict()
    efficiency = dict()
    inefficiency = dict()
    efficiency_projectionX = dict()
    efficiency_projectionY = dict()
    
    
    # Fill events for which the sensors records a hit
    LGAD[chan]         = ROOT.TH2D("LGAD_particles", "LGAD particles",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    # Fill events for which the tracking notes a hit
    MIMOSA[chan]       = ROOT.TH2D("tracking_particles", "Tracking particles",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    # For a given TEfficiency object, recreate to make it an inefficiency
    inefficiency[chan] = ROOT.TH2D("Inefficiency", "Inefficiency",xbin,-sep_x,sep_x,ybin,-sep_y,sep_y)
    
    # Projection X of efficiency
    efficiency_projectionX[chan] = ROOT.TProfile("Projection X", "projection x", xbin,-sep_x,sep_x)
    
    # Projection Y of efficiency
    efficiency_projectionY[chan] = ROOT.TProfile("Projection Y", "projection y", ybin,-sep_y,sep_y)
    
    
    # Fill MIMOSA and LGAD (TH2 objects)
    
    if array_pad:
        
        for event in range(0, len(tracking)):
            if (-sep_x < tracking['X'][event] < sep_x) and (-sep_y < tracking['Y'][event] < sep_y):
            
                for pad in range(0, len(peak_values[event])):
                    
                    # Total events
                    MIMOSA[chan].Fill(tracking['X'][event], tracking['Y'][event], 1)
                    
                    # Passed events
                    if peak_values[event][pad] > -md.getPulseAmplitudeCut(chan)*1000:
                        LGAD[chan].Fill(tracking['X'][event], tracking['Y'][event], 1)

    else:
    
         for event in range(0, len(tracking)):
            if (-sep_x < tracking['X'][event] < sep_x) and (-sep_y < tracking['Y'][event] < sep_y):
        
                # Total events
                MIMOSA[chan].Fill(tracking['X'][event], tracking['Y'][event], 1)
                
                # Passed events
                if peak_values[event] > -md.getPulseAmplitudeCut(chan)*1000:
                    LGAD[chan].Fill(tracking['X'][event], tracking['Y'][event], 1)


    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = MIMOSA[chan].GetBin(i,j)
            num_LGAD = LGAD[chan].GetBinContent(bin)
            
            if 0 < num_LGAD < minEntries:
                LGAD[chan].SetBinContent(bin, 0)
                MIMOSA[chan].SetBinContent(bin, 0)


    LGAD[chan].ResetStats()
    MIMOSA[chan].ResetStats()

    # Projection plot limits
    bin_low_x = LGAD[chan].GetXaxis().FindBin(-0.3)
    bin_high_x = LGAD[chan].GetXaxis().FindBin(0.3)

    bin_low_y = LGAD[chan].GetYaxis().FindBin(-0.3)
    bin_high_y = LGAD[chan].GetYaxis().FindBin(0.3)

    efficiency[chan] = ROOT.TEfficiency(LGAD[chan], MIMOSA[chan])

    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            
            
            bin = efficiency[chan].GetGlobalBin(i,j)
            eff = efficiency[chan].GetEfficiency(bin)
  
            # Compensate for array pads, one trigger per pad
            if array_pad:
                eff *= 4
                    
            if eff >= 1:
                inefficiency[chan].SetBinContent(bin, 0.001)
 
        
            elif eff != 0:
                inefficiency[chan].SetBinContent(bin, 1 - eff)
            
            if not array_pad:
                # Get projection x data given limits
                if bin_low_x <= i <= bin_high_x:
                    y_pos = LGAD[chan].GetYaxis().GetBinCenter(j)
                    efficiency_projectionY[chan].Fill(y_pos, eff*100)
                
                # Get projection x data given limits
                if bin_low_y <= j <= bin_high_y:
                    x_pos = LGAD[chan].GetXaxis().GetBinCenter(i)
                    efficiency_projectionX[chan].Fill(x_pos, eff*100)


    # Create projection plots for single pad arrays only
    if not array_pad:
     
        fit_sigmoid_x = ROOT.TF1("sigmoid_x", "([0]/(1+ TMath::Exp(-[1]*(x-[2]))) - [0]/(1+ TMath::Exp(-[1]*(x-[3]))))", -sep_x, sep_x)
        fit_sigmoid_x.SetParameters(100, 70, -0.5, 0.5)
        fit_sigmoid_x.SetParNames("Constant", "k", "Pos left", "Pos right")
        efficiency_projectionX[chan].Fit("sigmoid_x", "Q","", -sep_x, sep_x)
        
        fit_sigmoid_y = ROOT.TF1("sigmoid_y", "([0]/(1+ TMath::Exp(-[1]*(x-[2]))) - [0]/(1+ TMath::Exp(-[1]*(x-[3]))))", -sep_y, sep_y)
        fit_sigmoid_y.SetParameters(100, 70, -0.5, 0.5)
        fit_sigmoid_x.SetParNames("Constant", "k", "Pos left", "Pos right")
        efficiency_projectionY[chan].Fit("sigmoid_y", "Q","", -sep_y, sep_y)
     
     
        # Print projection X plot
        headTitle = "Projection of X-axis of efficiency 2D plot - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+ "; X [mm] ; Efficiency (%)"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/projection/tracking_projectionX_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, fileName]
        printProjectionPlot(efficiency_projectionX[chan], titles)
        
        # Print projection Y plot
        headTitle = "Projection of Y-axis of efficiency 2D plot - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+ "; Y [mm] ; Efficiency (%)"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/projection/tracking_projectionY_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, fileName]
        printProjectionPlot(efficiency_projectionY[chan], titles)
    
    
    totalEntries = efficiency[chan].GetPassedHistogram().GetEntries()

    # Print efficiency plot
    headTitle = "Efficiency - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+ "; X [mm] ; Y [mm] ; Efficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/efficiency/tracking_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")

    titles = [headTitle, fileName, totalEntries]
    printTHPlot(efficiency[chan], titles, True, False, array_pad)


    # Print inefficiency plot
    headTitle = "Inefficiency - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+ "; X [mm] ; Y [mm] ; Inefficiency (%)"
    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/inefficiency/tracking_inefficiency_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    if array_pad:
        fileName = fileName.replace(".pdf", "_array.pdf")

    titles = [headTitle, fileName, totalEntries]
    inefficiency[chan].Scale(100)
    inefficiency[chan].SetAxisRange(0, 100, "Z")
    printTHPlot(inefficiency[chan], titles, False, True, array_pad)



###########################################
#                                         #
#           ARRAY PAD GRAPHS              #
#                                         #
###########################################


def produceArrayPlots(peak_values, tracking, position, time_difference_peak, time_difference_cfd05):


    channels = ["chan5"]
    batchCategory = md.getBatchNumber()/100
    # W4-S204_6e14 -40 C
    if batchCategory == 5 or batchCategory == 7:
        channels = ["chan5", "chan6", "chan7"]
        
        # Calculate mean position from position of each array sensor
        array_pos_x = (position["chan6"][0][0] + position["chan7"][0][0])/2
        array_pos_y = (position["chan7"][0][1] + position["chan5"][0][1])/2
    
    else:
        # W4-S215 22 C
        if int(md.getBatchNumber()/100) == 1:
            channels = ["chan4", "chan5", "chan6", "chan7"]

        # W4-S215 22 C
        elif int(md.getBatchNumber()/100) == 2:
            channels = ["chan3", "chan5", "chan6", "chan7"]
        
        # W4-S215 -30 C
        elif int(md.getBatchNumber()/100) == 4:
            channels = ["chan1", "chan5", "chan6", "chan7"]

        # Calculate mean position from position of each array sensor
        array_pos_x = (position[channels[0]][0][0] + position[channels[1]][0][0] + position[channels[2]][0][0] + position[channels[3]][0][0])/4
        array_pos_y = (position[channels[0]][0][1] + position[channels[1]][0][1] + position[channels[2]][0][1] + position[channels[3]][0][1])/4


    track_calc.changeCenterPositionSensor(tracking, array_pos_x, array_pos_y, True)
    peak_values_array = peak_values[channels]
    time_difference_peak_array = time_difference_peak[channels]
    time_difference_cfd05_array = time_difference_cfd05[channels]

    print "\nArray Pad", md.getNameOfSensor(channels[0]), "\n"

    produceTProfilePlots(peak_values_array, tracking, time_difference_peak_array, time_difference_cfd05_array, channels[0], True)
    produceEfficiencyPlot(peak_values_array, tracking, channels[0], True)


    del channels


# Print TH2 Object plot
def printTHPlot(graphList, info, efficiency=False, inefficiency=False, array_pad=False):
    
    canvas.SetRightMargin(0.14)
    graphList.SetTitle(info[0])
    
    graphList.Draw("COLZ")
    canvas.Update()
    
    if efficiency:
    
        # Get painted histogram by calling TEfficiency-object
        
        if array_pad:
            graphList.GetPaintedHistogram().Scale(4)
        
        graphList.GetPaintedHistogram().Scale(100)
        graphList.GetPaintedHistogram().SetAxisRange(80, 100, "Z")
        graphList.GetPaintedHistogram().SetNdivisions(10, "Z")
        graphList.GetPaintedHistogram().SetTitle(info[0])
        
        # Update
        graphList.GetPaintedHistogram().Draw("COLZ")
        
        # Correct the number of entries, since PaintedHistogram have one per bin
        graphList.GetPaintedHistogram().SetStats(1)
        graphList.GetPaintedHistogram().SetEntries(info[2])
        
        ROOT.gStyle.SetOptStat(1000000011)
        
        # Move the stats box
        stats_box = graphList.GetPaintedHistogram().GetListOfFunctions().FindObject("stats")
        stats_box.SetX1NDC(0.1)
        stats_box.SetX2NDC(0.3)
        stats_box.SetY1NDC(0.93)
        stats_box.SetY2NDC(0.83)
        
        # Recreate stats box
        stats_box.SetOptStat(1000000011)
        
        # Draw projection limit lines for x
        proj_line_selection_up = ROOT.TLine(-0.6, 0.3, 0.6, 0.3)
        proj_line_selection_down = ROOT.TLine(-0.6, -0.3, 0.6, -0.3)
        #proj_line_selection_up.Draw("same")
        #proj_line_selection_down.Draw("same")
        
    else:
        graphList.SetStats(1)
        graphList.SetEntries(info[2])
        ROOT.gStyle.SetOptStat(1000000011)
        
        # Move the stats box
        stats_box = graphList.GetListOfFunctions().FindObject("stats")
        stats_box.SetX1NDC(0.1)
        stats_box.SetX2NDC(0.3)
        stats_box.SetY1NDC(0.93)
        stats_box.SetY2NDC(0.83)
        
        # Recreate stats box
        stats_box.SetOptStat(1000000011)


    # Export PDF
    canvas.Print(info[1])
    
    if efficiency:
        dm.exportROOTHistogram(graphList.GetPaintedHistogram(), info[1])
    
    else:
        dm.exportROOTHistogram(graphList, info[1])

    canvas.Clear()



# Print projection plot
def printProjectionPlot(graphList, info):

    ROOT.gStyle.SetOptStat("ne")
    ROOT.gStyle.SetOptFit(0012)
    ROOT.gStyle.SetStatW(0.15)

    graphList.SetTitle(info[0])
    graphList.SetStats(1)
    graphList.Draw()
    canvas.Update()

    # Export PDF
    canvas.Print(info[1])
    
    # Export histogram as ROOT file
    dm.exportROOTHistogram(graphList, info[1])
    canvas.Clear()
    


# Return global varables, separation and bin size
def getSepGlobVar():

    return sep_x, sep_y, bin_size, minEntries

