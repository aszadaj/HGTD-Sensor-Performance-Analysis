import ROOT
import numpy as np
import itertools as it

import data_management as dm
import run_log_metadata as md

ROOT.gROOT.SetBatch(True)

# The function imports pulse files and creates timing resolution files with
# time differences used for timingPlots and trackingAnalysis.
def createTimingFiles(batchNumber):

    runNumbers = md.getAllRunNumbers(batchNumber)

    startTimeBatch = dm.getTime()

    print "\nBatch:", batchNumber, len(runNumbers), "run files.\n"
    
    for runNumber in runNumbers:
        
        md.defineRunInfo(md.getRowForRunNumber(runNumber))
        
        if not dm.checkIfFileAvailable():
            continue
    
        print "Run", runNumber, "\n"
        
        # Import files per run
        peak_time = dm.exportImportROOTData("pulse", "peak_time")
        cfd = dm.exportImportROOTData("pulse", "cfd")
        
        # Perform linear calculations
        time_diff_peak = getTimeDifferencePerRun(peak_time)
        time_diff_cfd = getTimeDifferencePerRun(cfd)
        
        # Export per run number linear
        dm.exportImportROOTData("timing", "normal_peak", time_diff_peak)
        dm.exportImportROOTData("timing", "normal_cfd", time_diff_cfd)
        
        if batchNumber/100 != 6:
            # Perform calculations sys eq
            time_diff_peak_sys_eq = getTimeDifferencePerRunSysEq(peak_time)
            time_diff_cfd_sys_eq = getTimeDifferencePerRunSysEq(cfd)

            # Export per run number sys eq
            dm.exportImportROOTData("timing", "system_peak", time_diff_peak_sys_eq)
            dm.exportImportROOTData("timing", "system_cfd", time_diff_cfd_sys_eq)

        print "Done with run", runNumber, "\n"
    
    print "Done with batch", batchNumber, "Time analysing: "+str(dm.getTime()-startTimeBatch)+"\n"


# This takes the time difference between a DUT and the SiPM.
def getTimeDifferencePerRun(time_location):
    
    time_difference = np.zeros(len(time_location), dtype = time_location.dtype)

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")

    for chan in time_location.dtype.names:
        
        md.setChannelName(chan)

        if md.getSensor() == "SiPM-AFP":
            continue

        for event in range (0, len(time_location)):
            if time_location[SiPM_chan][event] != 0 and time_location[chan][event] != 0:
                time_difference[chan][event] = (time_location[chan][event] - time_location[SiPM_chan][event])*1000


    return time_difference


# This is used to produce ROOT files which have multiple solutions
# Note that the system of equations only applies to the first oscilloscope
# Reason: the first oscilloscope contains different sensors.
def getTimeDifferencePerRunSysEq(time_location):
    
    dt = dm.getDTYPESysEq()
    
    time_difference = np.zeros(len(time_location), dtype = dt)
    
    channels_1st_oscilloscope = ["chan0", "chan1", "chan2", "chan3"]
    
    for chan in channels_1st_oscilloscope:
        
        chan2_list = list(channels_1st_oscilloscope)
        chan2_list.remove(chan)
        for event in range(0, len(time_location[chan])):
            
            value = np.zeros(3)
            
            for index in range(0, len(chan2_list)):
                chan2 = chan2_list[index]
                
                if time_location[chan][event] != 0 and time_location[chan2][event] != 0:
                    value[index] = (time_location[chan][event] - time_location[chan2][event])*1000
    
            time_difference[chan][event] = value


    return time_difference


# The input is two matrices, one with widths (\sigma_{ij}) of time difference graphs between sensor i and j and
# corresponding errors from the fits (\Delta\sigma_{ij}).
# The output is the width of sensor i (\sigma_i) and corresponding error (\Delta\sigma{i}). All values in [ps].
# The function solves the equation according to (4.3) in report.
def solveSystemOfEqs(sigma_convoluted_matrix, error_convoluted_matrix):
    
    matrices, inverses = possibleMatrices()
    
    check_sum = 0
    
    for index in range(0, len(matrices)):
        
        matrix = matrices[index]
        matrix_inv = inverses[index]
        
        # Get \sigma_{i}
        sigma_convoluted_squared = np.power(matrix.dot(sigma_convoluted_matrix).diagonal(), 2)
        sigma_squared = matrix_inv.dot(sigma_convoluted_squared)
        
        if np.any(sigma_squared < 0):
            continue
        
        sigma_solution = np.sqrt(sigma_squared)
        
        # Get \Delta\sigma_{i}, note that the errors cannot be subtracted
        error_convoluted = matrix.dot(error_convoluted_matrix).diagonal()
        error_solution = abs(matrix_inv).dot(error_convoluted)
        
        # Select the solution with the largest sum of timing resolutions
        if check_sum < np.sum(sigma_solution):
            sigma = sigma_solution
            error = error_solution
            check_sum = np.sum(sigma_solution)


    return sigma, error



def getSigmasFromFit(TH1F_histogram, window_range, percentage):

    # Change the window
    xMin = TH1F_histogram.GetXaxis().GetBinCenter(TH1F_histogram.GetMaximumBin()) - window_range
    xMax = TH1F_histogram.GetXaxis().GetBinCenter(TH1F_histogram.GetMaximumBin()) + window_range
    TH1F_histogram.SetAxisRange(xMin, xMax)
    
    # Set ranges to be at the positions of defined height
    value_limit = TH1F_histogram.GetMaximum() * (1.0 - percentage)
    xMin = TH1F_histogram.GetXaxis().GetBinCenter(TH1F_histogram.FindFirstBinAbove(value_limit))
    xMax = TH1F_histogram.GetXaxis().GetBinCenter(TH1F_histogram.FindLastBinAbove(value_limit))
    
    # Create fit function if the same oscilloscope
    if md.checkIfSameOscAsSiPM():
        
        fit_function = ROOT.TF1("gaus", "gaus", xMin, xMax)

    # Create fit function if different oscilloscope
    else:
        
        # For some double-peak distributions the highest peak have to be set for the fit
        # to function correctly. Change the bool accordingly!
        high_peak_at_left = True
        
        if high_peak_at_left:
            
            # In the case when the highest peak is at left
            amplitude_1 = TH1F_histogram.GetMaximum()
            bin_second_peak = TH1F_histogram.GetBinCenter(TH1F_histogram.GetMaximumBin())+100
            position_second_peak = TH1F_histogram.FindBin(bin_second_peak)
            amplitude_2 = TH1F_histogram.GetBinContent(position_second_peak)
        
        else:
            # In the case when the highest peak is at right
            bin_first_peak = TH1F_histogram.GetBinCenter(TH1F_histogram.GetMaximumBin())-100
            position_first_peak = TH1F_histogram.FindBin(bin_second_peak)
            amplitude_1 = TH1F_histogram.GetBinContent(position_second_peak)
            amplitude_2 = TH1F_histogram.GetMaximum()

        fit_function = ROOT.TF1("gaus", "[0]*exp(-0.5*((x-[1])/[2])^2) + [3]*exp(-0.5*((x-([1]+100))/[2])^2)", xMin, xMax)
        fit_function.SetParameters(amplitude_1, TH1F_histogram.GetMean(), TH1F_histogram.GetStdDev(), amplitude_2)
        fit_function.SetParNames("Constant1", "Mean1", "Sigma", "Constant2")

    try:

        # Create fit and calculate the width
        TH1F_histogram.Fit("gaus", "Q", "", xMin, xMax)
        th1_function = TH1F_histogram.GetFunction("gaus")

        sigma_fit       = th1_function.GetParameter(2)
        sigma_fit_error = th1_function.GetParError(2)

        sigma_SiPM = md.getSigmaSiPM()

        if sigma_fit > sigma_SiPM:
            sigma_DUT = np.sqrt(np.power(sigma_fit, 2) - np.power(sigma_SiPM, 2))

        else:
            sigma_DUT = 0

    # In case that the fit fails, due to no data, ignore the result.
    except:

        sigma_DUT = 0
        sigma_fit_error = 0


    return sigma_DUT, sigma_fit_error


# Calculate all 4x4 matrices which have diagonal elements
def possibleMatrices():
    
    # The arrays indicate the possible ways to extract the width between sensor i and j.
    possible_combinations = np.array([ [1, 1, 0, 0], [1, 0, 1, 0], [1, 0, 0, 1], [0, 1, 1, 0], [0, 1, 0, 1], [0, 0, 1, 1] ])
    
    matrices = []
    inverses = []
    
    for combination in list(it.permutations(possible_combinations,4)):

        try:
            matrix = np.array(combination)
            inverse = np.linalg.inv(matrix)
            
            # Require that the matrix have diagonal elements
            if np.sum(matrix.diagonal()) != 4:
                continue

            matrices.append(matrix)
            inverses.append(inverse)

        except:
            continue
                

    return matrices, inverses
