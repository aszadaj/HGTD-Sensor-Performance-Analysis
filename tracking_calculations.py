import ROOT
import numpy as np

import run_log_metadata as md
import data_management as dm
import tracking_plot as t_plot


def fillTHObjects(numpy_arrays, TH2_objects_fill, tracking, th1_limits):
    
    [peak_value_mean_TH2F, gain_mean_TH2F, rise_time_mean_TH2F, time_difference_peak_TH2F, time_difference_cfd_TH2F, timing_peak_TH2F, timing_cfd_TH2F] = [i for i in TH2_objects_fill]
    
    [xbin, ybin, xbin_timing, ybin_timing, distance_x, distance_y] = [i for i in th1_limits]
    
    fill = False
    
    # Import values mean values of the time difference.
    mpv_time_diff_peak =  dm.exportImportROOTData("results", "linear")["linear"][2]
    mpv_time_diff_cfd  =  dm.exportImportROOTData("results", "linear_cfd")["linear_cfd"][2]
    
    # Fill all objects except timing resolution
    for event in range(0, len(tracking)):
        if (-distance_x < tracking['X'][event] < distance_x) and (-distance_y < tracking['Y'][event] < distance_y):
            for index in range(0, len(numpy_arrays)):
                if numpy_arrays[index][event] != 0:
                    if index == 3:
                        if (mpv_time_diff_peak - t_plot.width_time_diff) < numpy_arrays[index][event] < (mpv_time_diff_peak + t_plot.width_time_diff):
                            fill = True
                    elif index == 4:
                        if (mpv_time_diff_cfd - t_plot.width_time_diff) < numpy_arrays[index][event] < (mpv_time_diff_cfd + t_plot.width_time_diff):
                            fill = True
                    else:
                        fill = True
                    
                    if fill:
                        TH2_objects_fill[index].Fill(tracking['X'][event], tracking['Y'][event], numpy_arrays[index][event])
                        fill = False


    # Remove bins with few entries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):
            
            bin = peak_value_mean_TH2F.GetBin(i,j)
            removeBin(bin, peak_value_mean_TH2F)
            removeBin(bin, rise_time_mean_TH2F)
            removeBin(bin, gain_mean_TH2F)

        peak_value_mean_TH2F.ResetStats()
        rise_time_mean_TH2F.ResetStats()
        gain_mean_TH2F.ResetStats()

    
    # Fill timing resolution bins
    for i in range(1, xbin_timing+1):
        for j in range(1, ybin_timing+1):
            
            bin = time_difference_peak_TH2F.GetBin(i,j)
            fillTimeResBin(bin, time_difference_peak_TH2F, timing_peak_TH2F)
            fillTimeResBin(bin, time_difference_cfd_TH2F, timing_cfd_TH2F)


def fillEfficiencyObjects(LGAD_TH2F, MIMOSA_TH2F, tracking, peak_values, distance_x, distance_y, xbin, ybin):

    # Fill MIMOSA and LGAD (TH2 objects)
    for event in range(0, len(tracking)):
        if (-distance_x < tracking['X'][event] < distance_x) and (-distance_y < tracking['Y'][event] < distance_y):

            # Total events
            MIMOSA_TH2F.Fill(tracking['X'][event], tracking['Y'][event], 1)

            # Passed events
            if peak_values[event] != 0:
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


# Change tracking information
def changeCenterPositionSensor(tracking):

    position = dm.exportImportROOTData("tracking", "position")

    center = np.array([position[md.chan_name][0][0], position[md.chan_name][0][1]])

    if md.checkIfArrayPad():
    
        dist_center = getDistanceFromCenterArrayPad(position)
 
        tracking["X"] = tracking["X"] + dist_center[md.chan_name][0][0]
        tracking["Y"] = tracking["Y"] + dist_center[md.chan_name][0][1]
    
        # Center the pad or array
        tracking["X"] = tracking["X"] - center[0]
        tracking["Y"] = tracking["Y"] - center[1]

        # Rotation for W4-S204_6e14
        if md.getSensor() == "W4-S204_6e14":

            theta = 4.3 * np.pi/180

            # Use the rotation matrix around z
            tracking["X"] = np.multiply(tracking["X"], np.cos(theta)) - np.multiply(tracking["Y"], np.sin(theta))
            tracking["Y"] = np.multiply(tracking["X"], np.sin(theta)) + np.multiply(tracking["Y"], np.cos(theta))

        # Rotation for W4-S215
        elif md.getSensor() == "W4-S215":

            theta = 0.6 * np.pi/180
            
              # Use the rotation matrix around z
            tracking["X"] = np.multiply(tracking["X"], np.cos(theta)) - np.multiply(tracking["Y"], np.sin(theta))
            tracking["Y"] = np.multiply(tracking["X"], np.sin(theta)) + np.multiply(tracking["Y"], np.cos(theta))

    
    else:
    
        # Center the pad or array
        tracking["X"] = tracking["X"] - center[0]
        tracking["Y"] = tracking["Y"] - center[1]


    return tracking


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


def calculateCenterOfSensorPerBatch(peak_values, tracking):

    print "Producing center positions for batch", md.getBatchNumber(), "\n"

    # Choose ranges for the tracking info
    xmin = -7000
    xmax = 7000
    ymin = 5000
    ymax = 16000
    
    bin_size = 18.5 * 2
    xbin = int((xmax-xmin)/bin_size)
    ybin = int((ymax-ymin)/bin_size)

    minEntries = 7
    
    values = [minEntries, xmin, xmax, ymin, ymax, xbin, ybin]

    position_temp = np.zeros(1, dtype = dm.getDTYPETrackingPosition())

    for chan in peak_values.dtype.names:

        position_temp[chan][0] = getCenterOfSensor(peak_values[chan], tracking, values)

    dm.exportImportROOTData("tracking", "position", position_temp)

    print "Done producing center position for batch", md.getBatchNumber()


def getCenterOfSensor(peak_values, tracking, values):

    [minEntries, xmin, xmax, ymin, ymax, xbin, ybin] = [i for i in values]

    mean_values = ROOT.TProfile2F("Mean value","Mean value", xbin, xmin, xmax, ybin, ymin, ymax)

    # Fill the events
    for event in range(0, len(tracking)):
        if tracking['X'][event] > -9990 and tracking['Y'][event] > -9990 and peak_values[event] != 0:
            mean_values.Fill(tracking['X'][event], tracking['Y'][event], peak_values[event])


    # Remove bins with less than minEntries
    for i in range(1, xbin+1):
        for j in range(1, ybin+1):

            bin = mean_values.GetBin(i,j)
            num = mean_values.GetBinEntries(bin)

            if num < minEntries:
                mean_values.SetBinContent(bin, 0)
                mean_values.SetBinEntries(bin, 0)

    mean_values.ResetStats()
    
    position_temp = np.array([mean_values.GetMean(), mean_values.GetMean(2)])

    del mean_values
    
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

    arrayPadChannels = getArrayPadChannels()
    chan = arrayPadChannels[index]
    
    objectName = TH2_object.GetName()
    fileName, headTitle = getTitleAndFileName(objectName, chan)
    
    TH2_file = dm.exportImportROOTHistogram(fileName)
    TH2_object_import = TH2_file.Get(objectName)
    TH2_object.Add(TH2_object_import)


def getTitleAndFileName(objectName, chan):
    
    fileName = "empty"
    headTitle = "empty"

    if objectName.find("Pulse") != -1:
        graphTitle = "Pulse amplitude mean value"
        dimension_z = "V [mV]"
        folderLocation = "pulse_amplitude_mean/tracking_mean_value"
    
    
    elif objectName.find("Gain") != -1:
        graphTitle = "Gain mean value"
        dimension_z = "Gain"
        folderLocation = "gain_mean/tracking_gain_mean_value"

    
    elif objectName.find("Rise") != -1:
        graphTitle = "Rise time mean value"
        dimension_z = "t [ps]"
        folderLocation = "rise_time_mean/tracking_rise_time_mean_value"

    
    elif objectName.find("peak") != -1:
        graphTitle = "Timing resolution (peak)"
        dimension_z = "\sigma_{t} [ps]"
        folderLocation = "time_resolution/peak/tracking_time_resolution_peak"


    elif objectName.find("CFD") != -1:
    
        graphTitle = "Timing resolution (CFD)"
        dimension_z = "\sigma_{t} [ps]"
        folderLocation = "time_resolution/cfd/tracking_time_resolution_cfd"

    
    elif objectName.find("Efficiency") != -1:
        graphTitle = "Efficiency"
        dimension_z = "Efficiency (%)"
        folderLocation = "efficiency/tracking_efficiency"

    
    elif objectName.find("Inefficiency") != -1:
        graphTitle = "Inefficiency"
        dimension_z = "Inefficiency (%)"
        folderLocation = "inefficiency/tracking_inefficiency"


    headTitle = graphTitle + " - " + md.getSensor() + ", T = " + str(md.getTemperature()) + " \circ C, U = " + str(md.getBiasVoltage()) + " V; X [\mum] ; Y [\mum] ; " + dimension_z
    fileName = dm.getSourceFolderPath() + dm.getPlotsSourceFolder() + "/" + md.getSensor()+ "/tracking/" + folderLocation + "_" + str(md.getBatchNumber()) + "_" + chan + "_" + str(md.getSensor()) + ".pdf"
    

    if array_pad_export:
        fileName = fileName.replace(".pdf", "_array.pdf")
        

    return fileName, headTitle


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
    if md.getSensor() == "W4-S204_6e14":
        
        if md.chan_name == "chan5":
            center_position = [-530, -575]
        
        elif md.chan_name == "chan6":
            center_position = [530, 500]
            
        elif md.chan_name == "chan7":
            center_position = [-530, 500]
        

    x1 = center_position[0] - projection_cut
    x2 = center_position[0] + projection_cut
    y1 = center_position[1] - projection_cut
    y2 = center_position[1] + projection_cut
    

    return np.array([[x1, x2], [y1, y2]]), center_position


def removeBin(bin, time_diff):

    if time_diff.GetBinEntries(bin) < t_plot.bin_entries:
        time_diff.SetBinContent(bin, 0)
        time_diff.SetBinEntries(bin, 0)


def fillTimeResBin(bin, time_diff, time_res):

    if time_diff.GetBinEntries(bin) > t_plot.bin_entries_timing:

        sigma_DUT = np.sqrt(np.power(time_diff.GetBinError(bin), 2) - np.power(md.getSigmaSiPM(), 2))
        time_res.SetBinContent(bin, sigma_DUT)


def setArrayPadExportBool(bool):

    global array_pad_export
    array_pad_export = bool
