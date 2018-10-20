import ROOT
import numpy as np
import itertools as it

import data_management as dm
import run_log_metadata as md

# The function imports pulse files and creates timing resolution files with
# time differences used for timingPlots and trackingAnalysis.
def createTimingFiles():
    
    ROOT.gROOT.SetBatch(True)
    
    dm.setFunctionAnalysis("timing_analysis")
    dm.defineDataFolderPath()
    
    runLog_batch = md.getRunLogBatches(md.batchNumbers)
    print "\nStart TIMING RESOLUTION analysis, batches:", md.batchNumbers
    
    for runLog in runLog_batch:
        
        print "Batch:", runLog[0][5], len(runLog), "run files.\n"
        
        for index in range(0, len(runLog)):
            
            md.defineRunInfo(runLog[index])
            
            if not dm.checkIfFileAvailable():
                continue
        
            print "Run", md.getRunNumber()
            
            # Import files per run
            peak_time = dm.exportImportROOTData("pulse", "peak_time")
            cfd = dm.exportImportROOTData("pulse", "cfd")
            
            # Perform linear calculations
            time_diff_peak = getTimeDifferencePerRun(peak_time)
            time_diff_cfd = getTimeDifferencePerRun(cfd)
            
            # Export per run number linear
            dm.exportImportROOTData("timing", "linear", time_diff_peak)
            dm.exportImportROOTData("timing", "linear_cfd", time_diff_cfd)
            
            if md.getBatchNumber()/100 != 6:
                # Perform calculations sys eq
                time_diff_peak_sys_eq = getTimeDifferencePerRunSysEq(peak_time)
                time_diff_cfd_sys_eq = getTimeDifferencePerRunSysEq(cfd)

                # Export per run number sys eq
                dm.exportImportROOTData("timing", "system", time_diff_peak_sys_eq)
                dm.exportImportROOTData("timing", "system_cfd", time_diff_cfd_sys_eq)

                print "Done with run", md.getRunNumber(), "\n"
                        
        print "Done with batch", runLog[0][5], "\n"

    print "Done with TIMING RESOLUTION analysis\n"



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
    
    dt = getDTYPESysEq()
    
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



def getSigmasFromFit(TH1F_list, window_range, chan):

    # Find the maximal value
    MPV_bin = TH1F_list.GetMaximumBin()
    MPV_time_diff = int(TH1F_list.GetXaxis().GetBinCenter(MPV_bin))
    MPV_entries = TH1F_list.GetMaximum()
    
    # Change the window
    xMin = MPV_time_diff - window_range
    xMax = MPV_time_diff + window_range
    TH1F_list.SetAxisRange(xMin, xMax)
    
    # Fit using normal gaussian
    N = 3
    mean_window = TH1F_list.GetMean()
    sigma_window = TH1F_list.GetStdDev()
    xMin = mean_window - N * sigma_window
    xMax = mean_window + N * sigma_window
    
    # Within the same oscilloscope
    if md.checkIfSameOscAsSiPM(chan):
        
        fit_function = ROOT.TF1("gaus", "gaus", xMin, xMax)

    # Else in different oscilloscopes
    else:
        fit_function = ROOT.TF1("gaus", "[0]*exp(-0.5*((x-[1] )/[2])^2) + [3]*exp(-0.5*((x-([1]+100))/[2])^2)", xMin, xMax)
        fit_function.SetParameters(MPV_entries, mean_window, sigma_window, MPV_entries)
        fit_function.SetParNames("Constant1", "Mean1", "Sigma-tot", "Constant2")

    try:

        # Create fit and calculate the width
        TH1F_list.Fit("gaus", "Q", "", xMin, xMax)
        th1_function = TH1F_list.GetFunction("gaus")

        sigma_fit       = th1_function.GetParameter(2)
        sigma_fit_error = th1_function.GetParError(2)
        time_diff_mean  = th1_function.GetParameter(1)

        sigma_SiPM = md.getSigmaSiPM()

        if sigma_fit > sigma_SiPM:
            sigma_DUT = np.sqrt(np.power(sigma_fit, 2) - np.power(sigma_SiPM, 2))

        else:
            sigma_DUT = 0
            time_diff_mean = 0

    # In case that the fit fails, due to no data, ignore the result.
    except:

        sigma_DUT = 0
        sigma_fit_error = 0
        time_diff_mean = 0


    return sigma_DUT, sigma_fit_error, time_diff_mean


def getDTYPESysEq():
    
    return (  [('chan0',  '<f8', (1,3)), ('chan1',  '<f8', (1,3)) ,('chan2',  '<f8', (1,3)) ,('chan3',  '<f8', (1,3))] )


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
