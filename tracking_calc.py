import ROOT
import numpy as np

import metadata as md
import data_management as dm


# Change tracking information
def changeCenterPositionSensor(tracking, position, chan):
    
    tracking["X"] = np.multiply(tracking["X"], 0.001)
    tracking["Y"] = np.multiply(tracking["Y"], 0.001)

    center = np.array([position[chan][0][0], position[chan][0][1]])

    if md.checkIfArrayPad(chan):
    
        dist_center = getDistanceFromCenterArrayPad(position)
 
        tracking["X"] = tracking["X"] + dist_center[chan][0][0]
        tracking["Y"] = tracking["Y"] + dist_center[chan][0][1]
    
        # Center the pad or array
        tracking["X"] = tracking["X"] - center[0]
        tracking["Y"] = tracking["Y"] - center[1]

        # Rotation for W4-S204_6e14
        if md.getNameOfSensor(chan) == "W4-S204_6e14":

            tan_theta = 0.15/1.75

            cos_theta = np.sqrt(1./(1+np.power(tan_theta, 2)))
            sin_theta = np.sqrt(1-np.power(cos_theta, 2))

            # Use the rotation matrix around z
            tracking["X"] = np.multiply(tracking["X"], cos_theta) - np.multiply(tracking["Y"], sin_theta)
            tracking["Y"] = np.multiply(tracking["X"], sin_theta) + np.multiply(tracking["Y"], cos_theta)

        # Rotation for W4-S215
        elif md.getNameOfSensor(chan) == "W4-S215":

            tan_theta = 4./300

            cos_theta = np.sqrt(1./(1+np.power(tan_theta, 2)))
            sin_theta = np.sqrt(1-np.power(cos_theta, 2))

            # Use the rotation matrix around z
            tracking["X"] = np.multiply(tracking["X"], cos_theta) - np.multiply(tracking["Y"], sin_theta)
            tracking["Y"] = np.multiply(tracking["X"], sin_theta) + np.multiply(tracking["Y"], cos_theta)

    
    else:
    
        # Center the pad or array
        tracking["X"] = tracking["X"] - center[0]
        tracking["Y"] = tracking["Y"] - center[1]


    return tracking


def getDistanceFromCenterArrayPad(position):

    arrayPadChannels = getArrayPadChannels()
   
    numberOfPads = len(position[arrayPadChannels][0])

    pos_pad = np.zeros((numberOfPads, 2))

    for pad_no in range(0, numberOfPads):
        for dim in range(0, 2):
            pos_pad[pad_no][dim] = position[arrayPadChannels][0][pad_no][dim]
    
    centerArrayPadPosition = np.average(pos_pad, axis=0)

    newArrayPositions = createCenterPositionArray()
    
    for index in range(0, numberOfPads):
        chan = arrayPadChannels[index]
        newArrayPositions[chan][0] = pos_pad[index] - centerArrayPadPosition

    return newArrayPositions


# Create array for exporting center positions, inside tracking
def createCenterPositionArray():

    dt = (  [('chan0', '<f8', 2), ('chan1', '<f8', 2) ,('chan2', '<f8', 2) ,('chan3', '<f8', 2) ,('chan4', '<f8', 2) ,('chan5', '<f8', 2) ,('chan6', '<f8', 2) ,('chan7', '<f8', 2)] )
    
    return np.zeros(1, dtype = dt)


def calculateCenterOfSensorPerBatch(peak_values, tracking):

    global minEntries, xmin, xmax, ymin, ymax, xbin, ybin, chan
   
    # Choose ranges for the tracking info
    xmin = -7000
    xmax = 7000
    ymin = 5000
    ymax = 16000
    
    bin_size = 18.5 * 2
    xbin = int((xmax-xmin)/bin_size)
    ybin = int((ymax-ymin)/bin_size)

    minEntries = 5

    position = createCenterPositionArray()

    for chan in peak_values.dtype.names:
        
        if md.getNameOfSensor(chan) != "SiPM-AFP":
        
            position[chan][0] = getCenterOfSensor(peak_values[chan], tracking)

    dm.exportTrackingData(position)

    print "Done exporting batch", md.getBatchNumber()


def getCenterOfSensor(peak_values, tracking):

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
    
    position = np.array([mean_values.GetMean(), mean_values.GetMean(2)])

    del mean_values
    
    return position


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

    elif batchCategory == 5:
        channels = ["chan5", "chan6", "chan7"]

    elif batchCategory == 6:
        channels = ["chan0", "chan1"]

    elif batchCategory == 7:
        channels = ["chan5", "chan6", "chan7"]

    return channels


def importAndAddHistogram(TH2D_object, index, export=False):

    arrayPadChannels = getArrayPadChannels()
    chan = arrayPadChannels[index]
    objectName = TH2D_object.GetName()

    fileName, headTitle = getTitleAndFileName(objectName, chan)
    
    TH2D_file = dm.importROOTHistogram(fileName)
    TH2D_object_import = TH2D_file.Get(objectName)
    TH2D_object.Add(TH2D_object_import)



def getTitleAndFileName(objectName, chan):
    
    fileName = "empty"
    headTitle = "empty"

    if objectName.find("Pulse") != -1:
        headTitle = "Mean pulse amplitude value - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+"; X [mm] ; Y [mm] ; V [mV]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/pulse_amplitude_mean/tracking_mean_value_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    elif objectName.find("Gain") != -1:
        headTitle = "Gain mean value - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+"; X [mm] ; Y [mm] ; Gain"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/gain_mean/tracking_gain_mean_value_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    elif objectName.find("Rise") != -1:
        headTitle = "Mean pulse rise time value - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+"; X [mm] ; Y [mm] ; t [ps]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/rise_time_mean/tracking_rise_time_mean_value_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    elif objectName.find("peak") != -1:
        headTitle = "Time resolution (peak ref.) - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+"; X [mm] ; Y [mm] ; \sigma_{t} [ps]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/time_resolution/peak/tracking_time_resolution_peak_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    elif objectName.find("cfd05") != -1:
        headTitle = "Time resolution (CFD ref) - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+"; X [mm] ; Y [mm] ; \sigma_{t} [ps]"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/time_resolution/cfd05/tracking_time_resolution_cfd05_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    elif objectName.find("Efficiency") != -1:
        headTitle = "Efficiency - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+ "; X [mm] ; Y [mm] ; Efficiency (%)"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/efficiency/tracking_efficiency_" + str(md.getBatchNumber()) +"_" + chan + "_"+str(md.getNameOfSensor(chan))+".pdf"
    
    elif objectName.find("Inefficiency") != -1:
        headTitle = "Inefficiency - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan))) + " V"+ "; X [mm] ; Y [mm] ; Inefficiency (%)"
        fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/tracking/inefficiency/tracking_inefficiency_"+ str(md.getBatchNumber()) +"_"+ chan + "_"+str(md.getNameOfSensor(chan))+".pdf"

    if array_pad_export:
        fileName = fileName.replace(".pdf", "_array.pdf")

    return fileName, headTitle



def removeBin(bin, th2d_object, minEntries):

    num = th2d_object.GetBinEntries(bin)
    
    if num < minEntries:
        th2d_object.SetBinContent(bin, 0)
        th2d_object.SetBinEntries(bin, 0)


def fillTimeResBin(bin, th2d_object_temp, th2d_object):
    sigma_SiPM = md.getSigmaSiPM()

    num = th2d_object_temp.GetBinEntries(bin)

    if num > 10:

        sigma_convoluted = th2d_object_temp.GetBinError(bin)
        sigma_DUT = np.sqrt(np.power(sigma_convoluted, 2) - np.power(sigma_SiPM, 2))
        th2d_object.SetBinContent(bin, sigma_DUT)




def setArrayPadExportBool(bool):

    global array_pad_export
    array_pad_export = bool
