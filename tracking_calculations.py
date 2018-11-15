import ROOT
import numpy as np

import run_log_metadata as md
import data_management as dm
import tracking_plot as t_plot
import pulse_plot as p_plot
import timing_plot as tim_plot


def fillTHObjects(numpy_arrays, TH2_pulse, TH2_timing, tracking, th1_limits):
    
    [xbin, ybin, xbin_timing, ybin_timing, distance_x, distance_y] = [i for i in th1_limits]
    
    # Create time difference objects, with standard deviation as error in each bin
    th_name = "_"+str(md.getBatchNumber())+"_"+md.chan_name
    time_difference_peak_TH2D   = ROOT.TProfile2D("timing_peak"+th_name+"temp", "timing_peak", xbin_timing, -distance_x, distance_x, ybin_timing, -distance_y, distance_y, "s")
    time_difference_cfd_TH2D    = ROOT.TProfile2D("timing_cfd"+th_name+"temp", "timing_cfd", xbin_timing, -distance_x, distance_x, ybin_timing, -distance_y, distance_y, "s")
    
    # Remove large values
    stripNumpyArrays(numpy_arrays, TH2_pulse, TH2_timing)
    TH2_objects_fill = [i for i in TH2_pulse]
    TH2_objects_fill.append(time_difference_peak_TH2D)
    TH2_objects_fill.append(time_difference_cfd_TH2D)

    
    # Fill all objects
    for event in range(0, len(tracking)):
        if (-distance_x < tracking['X'][event] < distance_x) and (-distance_y < tracking['Y'][event] < distance_y):
            for index in range(0, len(numpy_arrays)):
                if numpy_arrays[index][event] != 0:
                    TH2_objects_fill[index].Fill(tracking['X'][event], tracking['Y'][event], numpy_arrays[index][event])


    # Remove bins with few entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            for index in range(0, len(TH2_pulse)):
                bin = TH2_pulse[index].GetBin(i,j)
                removeBin(bin, TH2_pulse[index])

    for index in range(0, len(TH2_pulse)):
        TH2_pulse[index].ResetStats()

    
    entries_timing_resolution = [time_difference_peak_TH2D.GetEntries(), time_difference_cfd_TH2D.GetEntries()]
    
    # Fill timing resolution bins
    for i in range(1, xbin_timing+1):
        for j in range(1, ybin_timing+1):
            for index in range(0, len(TH2_timing)):
                bin = TH2_timing[index].GetBin(i,j)
                fillTimeResBin(bin, TH2_objects_fill[index+3], TH2_timing[index])


    del time_difference_peak_TH2D, time_difference_cfd_TH2D

    return entries_timing_resolution


def fillEfficiencyObjects(LGAD_TH2F, MIMOSA_TH2F, tracking, pulse_amplitude, distance_x, distance_y, xbin, ybin):

    # Fill MIMOSA and LGAD (TH2 objects)
    for event in range(0, len(tracking)):
        if (-distance_x < tracking['X'][event] < distance_x) and (-distance_y < tracking['Y'][event] < distance_y):

            # Total events
            MIMOSA_TH2F.Fill(tracking['X'][event], tracking['Y'][event], 1)

            # Passed events
            if pulse_amplitude[event] != 0:
                LGAD_TH2F.Fill(tracking['X'][event], tracking['Y'][event], 1)


    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = LGAD_TH2F.GetBin(i,j)
            num_LGAD = LGAD_TH2F.GetBinContent(bin)
            
            if num_LGAD < t_plot.bin_entries:
                LGAD_TH2F.SetBinContent(bin, 0)
                MIMOSA_TH2F.SetBinContent(bin, 0)

    LGAD_TH2F.ResetStats()
    MIMOSA_TH2F.ResetStats()


def fillInefficiencyAndProjectionObjects(efficiency_TH2F, inefficiency_TH2F, projectionX_th1d, projectionY_th1d, xbin, ybin):
    
    distance_projection, center_positions = findSelectionRange()

    # Define lower and upper limits bins
    bin_x_low = efficiency_TH2F.GetXaxis().FindBin(distance_projection[0][0])
    bin_x_high = efficiency_TH2F.GetXaxis().FindBin(distance_projection[0][1])
    bin_y_low = efficiency_TH2F.GetYaxis().FindBin(distance_projection[1][0])
    bin_y_high = efficiency_TH2F.GetYaxis().FindBin(distance_projection[1][1])
    
    bin_limits = np.array([bin_x_low, bin_x_high, bin_y_low, bin_y_high])
    
    efficiency_bulk_data = np.array([])
    
    # Loop through each bin, to obtain inefficiency, and fill projection objects
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            
            bin = efficiency_TH2F.GetBin(i,j)
            eff = efficiency_TH2F.GetBinContent(bin)
            
            if eff > 0:
                inefficiency_TH2F.SetBinContent(bin, 100-eff)
                
                if (bin_limits[0] <= i <= bin_limits[1]) and (bin_limits[2] <= j <= bin_limits[3]):
                    
                    efficiency_bulk_data = np.concatenate((efficiency_bulk_data, np.array([eff])))
            
            if eff == 100:
                inefficiency_TH2F.SetBinContent(bin, 0.001)
            
            
            # Fill projection Y efficiency values within x-limits
            if bin_limits[0] <= i <= bin_limits[1]:
                y = efficiency_TH2F.GetYaxis().GetBinCenter(j)
                projectionY_th1d.Fill(y, eff)
            
            # Fill projection X efficiency values within y-limits
            if bin_limits[2] <= j <= bin_limits[3]:
                x = efficiency_TH2F.GetXaxis().GetBinCenter(i)
                projectionX_th1d.Fill(x, eff)

    # Additional comment: bin_limits marks the lines for which the selection of the
    # projection for each dimension. Vertical limits are for the Y-projection, where
    # horizontal is for X-projection. Then for each "line of bins" are projected by
    # filling within the limits. TProfile objects then calculate the mean in each filled
    # line. The point here is to see how the edges increases

    efficiency_bulk = [np.mean(efficiency_bulk_data), np.std(efficiency_bulk_data)]
    dm.exportImportROOTData("tracking", "efficiency", np.array(efficiency_bulk))


# Import results from already exported histograms to strip extreme values. Set a 5 sigma level on the standard deviation from the histogram.
def stripNumpyArrays(numpy_arrays, TH2_pulse, TH2_timing):
    
    TH_titles = [i.GetTitle() for i in TH2_pulse]
    TH_titles.append(TH2_timing[-2].GetTitle())
    TH_titles.append(TH2_timing[-1].GetTitle())
    
    # the 5 sigma limit ensures with large limit than relevant values are filled and that extreme values are omitted.
    # It should be noted that the GetStdDev() refers to histogram deviation, not the fit. The histogram have larger std values.
    N = 5
    
    # Strip pulse amplitude values higher than 500 mV. There is a tendency that some fit fails and give extreme values.
    numpy_arrays[0][numpy_arrays[0] > 500] = 0
    numpy_arrays[1][numpy_arrays[0] > 500] = 0
    
    # For other types, strip with a 5 sigma width from the histograms
    # Strip gain, rise time and
    for index in range(2, len(numpy_arrays)):
        
        category = TH_titles[index]
        subcategory = ""
        
        if category.find("rise_time") != -1:
            group = "pulse"
        
        else:
            
            group, subcategory = category.split("_")
            category = "normal"
        
        THistogram = dm.exportImportROOTHistogram(group, category, subcategory)

        mean = THistogram.GetMean()
        sigma = THistogram.GetStdDev()
        
        numpy_arrays[index][mean - N * sigma > numpy_arrays[index]] = 0
        numpy_arrays[index][mean + N * sigma < numpy_arrays[index]] = 0



# Change tracking information
def changeCenterPositionSensor(tracking):

    position = dm.exportImportROOTData("tracking", "position")

    center = np.array([position[md.chan_name][0][0], position[md.chan_name][0][1]])
    
    # Center the pad or array
    tracking["X"] = tracking["X"] - center[0]
    tracking["Y"] = tracking["Y"] - center[1]

    if md.checkIfArrayPad():
    
        # Plot each pad to its position
        dist_center = getDistanceFromCenterArrayPad(position)
        tracking["X"] = tracking["X"] + dist_center[md.chan_name][0][0]
        tracking["Y"] = tracking["Y"] + dist_center[md.chan_name][0][1]
    
    rotateSensor(tracking)

    return tracking

# these values are manually adapted for each batch.
# To make this more modular, a suggestion is to get the sigma-values from the projections
# and iterate this function until the left and right projections for both x and y reaches a limit.
def rotateSensor(tracking):
    
    theta = 0.0
    
    sensor = md.getSensor()
    batchGroup = md.getBatchNumber()/100
    
    # Rotation for W4-S204_6e14
    
    if sensor == "W9-LGA35" and batchGroup == 2:
        
        theta = 0.1
    
    elif sensor == "W4-LG12" and batchGroup == 2:
        
        theta = 0

    elif sensor == "W4-RD01":
        
        theta = 0.0
        
        if batchGroup == 3:
            theta = 0.2

    elif sensor == "W4-S1022":
        
        theta = 0.2
        
        if batchGroup == 5:
            
            theta = 0.1
        
        elif batchGroup == 7:
            
            theta = 0.1


    elif sensor == "W4-S1061":
        
        theta = 0.2
        if batchGroup == 5:
            theta = 0.15
        
        elif batchGroup == 7:
            theta = 0.15


    elif sensor == "W4-S203":
        
        theta = -0.1
        if batchGroup == 5:
            theta = -0.2
                
        elif batchGroup == 7:
            theta = -0.5
                

    elif sensor == "W4-S204_6e14":
        
        theta = 4.45
    

    elif sensor == "W4-S215":
        
        theta = 0.55
        if batchGroup == 5:
            theta = 0.8
        elif batchGroup == 7:
            theta = 0.8

    
    if theta != 0.0:
        # Use the rotation matrix around z
        theta *= np.pi/180.0
        tracking["X"] = np.multiply(tracking["X"], np.cos(theta)) - np.multiply(tracking["Y"], np.sin(theta))
        tracking["Y"] = np.multiply(tracking["X"], np.sin(theta)) + np.multiply(tracking["Y"], np.cos(theta))



def getDistanceFromCenterArrayPad(position):

    arrayPadChannels = getArrayPadChannels()
   
    numberOfPads = len(position[arrayPadChannels][0])

    if md.getSensor() == "W4-S204_6e14":
        numberOfPads += 1

    pos_pad = np.zeros((numberOfPads, 2))

    for pad_no in range(0, numberOfPads):
        for dim in range(0, 2):
            
            # This is a hand-waving fix for the missing pad, to temporarily calculate the average value to find the center of the three (four) pads
            if md.getSensor() == "W4-S204_6e14" and pad_no == 3:
                pos_pad[pad_no][0] = position[arrayPadChannels][0][1][0]
                pos_pad[pad_no][1] = position[arrayPadChannels][0][0][1]
            
            else:
                pos_pad[pad_no][dim] = position[arrayPadChannels][0][pad_no][dim]


    centerArrayPadPosition = np.average(pos_pad, axis=0)

    newArrayPositions = np.zeros(1, dtype = dm.getDTYPETrackingPosition())

    if md.getSensor() == "W4-S204_6e14":
        numberOfPads -= 1

    for index in range(0, numberOfPads):
        chan2 = arrayPadChannels[index]
        newArrayPositions[chan2][0] = pos_pad[index] - centerArrayPadPosition

    return newArrayPositions

# The centerpositions are dependent on which batch is selected. The batches are
# manually selected for Sep 2017. A tip is to choose a batch which have largest number of files.
def calculateCenterOfSensorPerBatch(pulse_amplitude, tracking):

    # Calculate position for largest batches
    if md.getBatchNumber() not in [101, 207, 306, 401, 507, 601, 707]:
        return 0
    
    global canvas_center
    
    canvas_center = ROOT.TCanvas("c1", "c1")
    
    print "\nCalculating CENTER POSITIONS for batch", md.getBatchNumber(), "\n"

    position_temp = np.zeros(1, dtype = dm.getDTYPETrackingPosition())

    for chan in pulse_amplitude.dtype.names:
        md.setChannelName(chan)
        print md.getSensor()

        position_temp[chan][0] = getCenterOfSensor(pulse_amplitude[chan], np.copy(tracking))

    dm.exportImportROOTData("tracking", "position", position_temp)

    print "\nDONE producing CENTER POSITIONS for batch", md.getBatchNumber(), "\n"


def getCenterOfSensor(pulse_amplitude, tracking):
    
    bin_size = 18.5
    
    # This has to be changed to match the MIMOSA! These are ranges in um.
    [xmin, xmax, ymin, ymax, minEntries] = [-7000, 8000, 9000, 16000, 5]
    
    # Choose ranges to center the DUTs depending on batch (the SiPM is larger, therefore the mean values of it are not exact)
    if md.getBatchNumber() == 101 or md.getBatchNumber() == 207:
        [xmin, xmax, ymin, ymax, minEntries] = [-1500, 1500, 11500, 14500, 8]

    elif md.getBatchNumber() == 306:
        [xmin, xmax, ymin, ymax, minEntries] = [-4500, -1000, 11000, 14000, 20]

    elif md.getBatchNumber() == 401:
        [xmin, xmax, ymin, ymax, minEntries] = [-4000, -1200, 10500, 13500, 5]

    elif md.getBatchNumber() == 507 or md.getBatchNumber() == 707:
        [xmin, xmax, ymin, ymax, minEntries] = [-3000, 800, 10000, 13500, 5]
        if md.getBatchNumber() == 707:
            bin_size *= 2

    elif md.getBatchNumber() == 601:
        [xmin, xmax, ymin, ymax, minEntries] = [-1500, 500, 10000, 13000, 20]



    xbin = int((xmax-xmin)/bin_size)
    ybin = int((ymax-ymin)/bin_size)

    passed_th2d = ROOT.TH2D("passed","passed",xbin,xmin,xmax,ybin,ymin,ymax)
    total_th2d = ROOT.TH2D("total","total",xbin,xmin,xmax,ybin,ymin,ymax)

    # Fill the events
    for event in range(0, len(tracking)):
        if tracking['X'][event] > -9990 and tracking['Y'][event] > -9990:
            total_th2d.Fill(tracking['X'][event], tracking['Y'][event], 1)
            if pulse_amplitude[event] != 0:
                passed_th2d.Fill(tracking['X'][event], tracking['Y'][event], 1)


    # Remove bins with less than some entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            bin = passed_th2d.GetBin(i,j)
            num_passed = float(passed_th2d.GetBinContent(bin))
            num_total = float(total_th2d.GetBinContent(bin))
            
            if num_total != 0.0:
                if 0.8 > (num_passed/num_total):
                    passed_th2d.SetBinContent(bin, 0)
                    total_th2d.SetBinContent(bin, 0)
        
            if num_total < minEntries:
                passed_th2d.SetBinContent(bin, 0)
                total_th2d.SetBinContent(bin, 0)

    passed_th2d.ResetStats()
    total_th2d.ResetStats()

    efficiency = ROOT.TEfficiency(passed_th2d, total_th2d)
    efficiency.Draw("COLZ")
    canvas_center.Update()
    efficiency_th2d = efficiency.GetPaintedHistogram()

    # Calculate the mean value for each DUT
    position_temp = np.array([efficiency_th2d.GetMean(), efficiency_th2d.GetMean(2)])

    line_distance = 700
    line_x = ROOT.TLine(position_temp[0], position_temp[1]-line_distance, position_temp[0], position_temp[1]+line_distance)
    line_y = ROOT.TLine(position_temp[0]-line_distance, position_temp[1], position_temp[0]+line_distance, position_temp[1])

    # Print the graph to estimate if the positions are correct
    canvas_center.Clear()
    efficiency_th2d.SetStats(1)
    efficiency_th2d
    efficiency_th2d.Draw("COLZ")
    line_x.Draw("same")
    line_y.Draw("same")
    canvas_center.Update()
    
    filePath = dm.getSourceFolderPath()+"/position_"+str(md.getBatchNumber())+"_"+md.getSensor()+"_"+md.chan_name+".pdf"
    
    # If one wants to see where the center is, comment this line and change filePath
    #canvas_center.Print(filePath)

    canvas_center.Clear()
    
    return position_temp


def getArrayPadChannels():

    batchCategory = md.getBatchNumber()/100

    if batchCategory == 1:
        channels = ["chan4", "chan5", "chan6", "chan7"]

    elif batchCategory == 2:
        channels = ["chan3", "chan5", "chan6", "chan7"]

    elif batchCategory == 3:
        channels = ["chan4", "chan5"]

    elif batchCategory == 4:
        channels = ["chan1", "chan5", "chan6", "chan7"]

    elif batchCategory == 5 or batchCategory == 7:
        channels = ["chan5", "chan6", "chan7"]

    elif batchCategory == 6:
        channels = ["chan0", "chan1"]

    return channels

# Check if the sensor processed is an array pad
def sensorIsAnArrayPad():

    bool = True

    if md.sensor != "":
        md.setChannelName(getArrayPadChannels()[0])
        
        if md.sensor != md.getSensor():
            bool = False

    return bool


def importAndAddHistogram(TH2_object, index):

    chan = getArrayPadChannels()[index]
    md.setChannelName(chan)
    
    category = TH2_object.GetTitle()
    
    subcategory = ""
    
    if category.find("timing") != -1:
        category, subcategory = category.split("_")

    THistogram = dm.exportImportROOTHistogram("tracking", category, subcategory)
    TH2_object.Add(THistogram)


def drawLines(line_extension=0):

    ranges, center_positions = findSelectionRange()

    x1 = ranges[0][0]
    x2 = ranges[0][1]
    y1 = ranges[1][0]
    y2 = ranges[1][1]

    # Lines which selects the area in y for projection in x
    line_y1 = ROOT.TLine(x1-line_extension, y1, x2+line_extension, y1)
    line_y2 = ROOT.TLine(x1-line_extension, y2, x2+line_extension, y2)

    # Lines which selects the area in x for projection in y
    line_x1 = ROOT.TLine(x1, y1-line_extension, x1, y2+line_extension)
    line_x2 = ROOT.TLine(x2, y1-line_extension, x2, y2+line_extension)
    
    line_y1.SetLineWidth(2)
    line_y2.SetLineWidth(2)
    line_x1.SetLineWidth(2)
    line_x2.SetLineWidth(2)
    
    return [line_y1, line_y2, line_x1, line_x2]


def findSelectionRange():
    
    position = dm.exportImportROOTData("tracking", "position")
    
    
    # In case of array pads, refer to the center of the pad
    if md.checkIfArrayPad():
    
        center_position  = (getDistanceFromCenterArrayPad(position)[md.chan_name])[0]
    
    # otherwise, refer from origo with predefined structured array
    else:
        center_position = (np.zeros(1, dtype = dm.getDTYPETrackingPosition())[md.chan_name])[0]

    # Distance from the center of the pad and 350 um from the center
    projection_cut = 350

    # This is a correction for the irradiated array pad to center the selection of the bulk for efficiency calculation
    if md.getSensor() == "W4-S204_6e14": # check for batch 707

        if md.chan_name == "chan5":
            center_position = [-540, -550]

        elif md.chan_name == "chan6":
            center_position = [530, 530]

        elif md.chan_name == "chan7":
            center_position = [-540, 530]


    x1 = center_position[0] - projection_cut
    x2 = center_position[0] + projection_cut
    y1 = center_position[1] - projection_cut
    y2 = center_position[1] + projection_cut
    

    return np.array([[x1, x2], [y1, y2]]), center_position


def removeBin(bin, time_diff, minEntries=0):

    if minEntries == 0:
        minEntries = t_plot.bin_entries
    
    if time_diff.GetBinEntries(bin) < minEntries:
        time_diff.SetBinContent(bin, 0)
        time_diff.SetBinEntries(bin, 0)


def fillTimeResBin(bin, time_diff, time_res):

    if time_diff.GetBinEntries(bin) > t_plot.bin_entries_timing:
        
        sigma_DUT = np.sqrt(np.power(time_diff.GetBinError(bin), 2) - np.power(md.getSigmaSiPM(), 2))
        time_res.SetBinContent(bin, sigma_DUT)


def setArrayPadExportBool(bool):

    global array_pad_export
    array_pad_export = bool
