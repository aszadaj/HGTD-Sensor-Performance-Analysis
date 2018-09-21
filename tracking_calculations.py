import ROOT
import numpy as np

import run_log_metadata as md
import data_management as dm
import tracking_plot as t_plot


# Change tracking information
def changeCenterPositionSensor(tracking):

    position = dm.exportImportROOTData("tracking", "position", False)

    center = np.array([position[t_plot.chan][0][0], position[t_plot.chan][0][1]])

    if md.checkIfArrayPad(t_plot.chan):
    
        dist_center = getDistanceFromCenterArrayPad(position)
 
        tracking["X"] = tracking["X"] + dist_center[t_plot.chan][0][0]
        tracking["Y"] = tracking["Y"] + dist_center[t_plot.chan][0][1]
    
        # Center the pad or array
        tracking["X"] = tracking["X"] - center[0]
        tracking["Y"] = tracking["Y"] - center[1]

        # Rotation for W4-S204_6e14
        if md.getNameOfSensor(t_plot.chan) == "W4-S204_6e14":

            theta = 4.3 * np.pi/180

            # Use the rotation matrix around z
            tracking["X"] = np.multiply(tracking["X"], np.cos(theta)) - np.multiply(tracking["Y"], np.sin(theta))
            tracking["Y"] = np.multiply(tracking["X"], np.sin(theta)) + np.multiply(tracking["Y"], np.cos(theta))

        # Rotation for W4-S215
        elif md.getNameOfSensor(t_plot.chan) == "W4-S215":

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

    if md.getNameOfSensor(t_plot.chan) == "W4-S204_6e14":
        numberOfPads += 1

    pos_pad = np.zeros((numberOfPads, 2))

    for pad_no in range(0, numberOfPads):
        for dim in range(0, 2):
            
            # This is a hand-waving fix for the missing pad, to temporarily calculate the average value to find the center of the three (four) pads
            if md.getNameOfSensor(t_plot.chan) == "W4-S204_6e14" and pad_no == 3:
                pos_pad[pad_no][0] = position[arrayPadChannels][0][1][0]
                pos_pad[pad_no][1] = position[arrayPadChannels][0][0][1]
            
            else:
                pos_pad[pad_no][dim] = position[arrayPadChannels][0][pad_no][dim]


    centerArrayPadPosition = np.average(pos_pad, axis=0)

    newArrayPositions = createCenterPositionArray()

    if md.getNameOfSensor(t_plot.chan) == "W4-S204_6e14":
        numberOfPads -= 1

    for index in range(0, numberOfPads):
        chan2 = arrayPadChannels[index]
        newArrayPositions[chan2][0] = pos_pad[index] - centerArrayPadPosition

    return newArrayPositions


# Create array for exporting center positions, inside tracking
def createCenterPositionArray():

    dt = (  [('chan0', '<f8', 2), ('chan1', '<f8', 2) ,('chan2', '<f8', 2) ,('chan3', '<f8', 2) ,('chan4', '<f8', 2) ,('chan5', '<f8', 2) ,('chan6', '<f8', 2) ,('chan7', '<f8', 2)] )
    
    return np.zeros(1, dtype = dt)


def calculateCenterOfSensorPerBatch(peak_values, tracking):

    # Choose ranges for the tracking info
    xmin = -7000
    xmax = 7000
    ymin = 5000
    ymax = 16000
    
    bin_size = 18.5 * 2
    xbin = int((xmax-xmin)/bin_size)
    ybin = int((ymax-ymin)/bin_size)

    minEntries = 5
    
    values = [minEntries, xmin, xmax, ymin, ymax, xbin, ybin]

    position_temp = createCenterPositionArray()

    for chan in peak_values.dtype.names:
        
        if md.getNameOfSensor(chan) != "SiPM-AFP":
        
            position_temp[chan][0] = getCenterOfSensor(peak_values[chan], tracking, values)

    dm.exportImportROOTData("tracking", "position", True, position_temp)

    print "Done exporting batch", md.getBatchNumber()


def getCenterOfSensor(peak_values, tracking, values):

    [minEntries, xmin, xmax, ymin, ymax, xbin, ybin] = [i for i in values]

    mean_values = ROOT.TProfile2D("Mean value","Mean value", xbin, xmin, xmax, ybin, ymin, ymax)

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


def sensorIsAnArrayPad():

    # If all sensors are considered, progress with the function
    if md.sensor == "":
        return True
    
    # Otherwise check if the sensor processed is an array pad
    else:
        chan = getArrayPadChannels()[0]

        if md.sensor == md.getNameOfSensor(chan):
            return True
        else:
            return False


def importAndAddHistogram(TH2D_object, index, export=False):

    arrayPadChannels = getArrayPadChannels()
    chan = arrayPadChannels[index]
    objectName = TH2D_object.GetName()

    fileName, headTitle = getTitleAndFileName(objectName, chan)
    
    TH2D_file = dm.exportImportROOTHistogram(fileName, False)
    TH2D_object_import = TH2D_file.Get(objectName)
    TH2D_object.Add(TH2D_object_import)



def getTitleAndFileName(objectName, chan):
    
    fileName = "empty"
    headTitle = "empty"

    if objectName.find("Pulse") != -1:
        headTitle = "Mean pulse amplitude value - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"+"; X [\mum] ; Y [\mum] ; V [mV]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/pulse_amplitude_mean/tracking_mean_value_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    elif objectName.find("Gain") != -1:
        headTitle = "Gain mean value - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"+"; X [\mum] ; Y [\mum] ; Gain"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/gain_mean/tracking_gain_mean_value_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    elif objectName.find("Rise") != -1:
        headTitle = "Mean pulse rise time value - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"+"; X [\mum] ; Y [\mum] ; t [ps]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/rise_time_mean/tracking_rise_time_mean_value_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    elif objectName.find("peak") != -1:
        headTitle = "Time resolution (peak ref.) - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"+"; X [\mum] ; Y [\mum] ; \sigma_{t} [ps]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/time_resolution/peak/tracking_time_resolution_peak_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    elif objectName.find("cfd") != -1:
        headTitle = "Time resolution (CFD ref) - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"+"; X [\mum] ; Y [\mum] ; \sigma_{t} [ps]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/time_resolution/cfd/tracking_time_resolution_cfd_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    elif objectName.find("Efficiency") != -1:
        headTitle = "Efficiency - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"+ "; X [\mum] ; Y [\mum] ; Efficiency (%)"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/efficiency/tracking_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    elif objectName.find("Inefficiency") != -1:
        headTitle = "Inefficiency - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"+ "; X [\mum] ; Y [\mum] ; Inefficiency (%)"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/inefficiency/tracking_inefficiency_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    if array_pad_export:
        fileName = fileName.replace(".pdf", "_array.pdf")

    return fileName, headTitle


def drawLines(efficiency):

    # Draw lines for which the projection limis is chosen
    if t_plot.singlePadGraphs and efficiency:
  
        ranges, center_positions = findSelectionRange()

        x1 = ranges[0][0]
        x2 = ranges[0][1]
        y1 = ranges[1][0]
        y2 = ranges[1][1]
        
        line_length_from_center = 300

        # Lines which selects the area in y for projection in x
        line_y1 = ROOT.TLine(x1-line_length_from_center, y1, x2+line_length_from_center, y1)
        line_y2 = ROOT.TLine(x1-line_length_from_center, y2, x2+line_length_from_center, y2)

        # Lines which selects the area in x for projection in y
        line_x1 = ROOT.TLine(x1, y1-line_length_from_center, x1, y2+line_length_from_center)
        line_x2 = ROOT.TLine(x2, y1-line_length_from_center, x2, y2+line_length_from_center)
        
        line_y1.SetLineWidth(2)
        line_y2.SetLineWidth(2)
        line_x1.SetLineWidth(2)
        line_x2.SetLineWidth(2)
        
        return [line_y1, line_y2, line_x1, line_x2]


def findSelectionRange():
    
    position = dm.exportImportROOTData("tracking", "position", False)
    
    # In case of array pads, refer to the center of the pad
    if md.checkIfArrayPad(t_plot.chan):
    
        center_position  = (getDistanceFromCenterArrayPad(position)[t_plot.chan])[0]
    
    # otherwise, refer from origo with predefined structured array
    else:
        center_position = (createCenterPositionArray()[t_plot.chan])[0]


    # Distance from the center of the pad and 300 um from the center
    projection_cut = 300

    x1 = center_position[0] - projection_cut
    x2 = center_position[0] + projection_cut
    y1 = center_position[1] - projection_cut
    y2 = center_position[1] + projection_cut

    return np.array([[x1, x2], [y1, y2]]), center_position


def removeBin(bin, time_diff, minEntries):

    num = time_diff.GetBinEntries(bin)
    
    if num < minEntries:
        time_diff.SetBinContent(bin, 0)
        time_diff.SetBinEntries(bin, 0)


def fillTimeResBin(bin, time_diff, time_res):
    entries_per_bin = t_plot.glob_variables[2]
    num = time_diff.GetBinEntries(bin)

    if num > entries_per_bin:

        sigma_convoluted = time_diff.GetBinError(bin)
        sigma_DUT = np.sqrt(np.power(sigma_convoluted, 2) - np.power(md.getSigmaSiPM(), 2))
        time_res.SetBinContent(bin, sigma_DUT)


def setArrayPadExportBool(bool):

    global array_pad_export
    array_pad_export = bool
