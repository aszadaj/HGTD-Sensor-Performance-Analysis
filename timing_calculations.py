import ROOT
import numpy as np

import run_log_metadata as md

# Define non-singular matrix with its inverse
matrix = np.array([[1, 0, 0, 1], [0, 1, 1, 0], [0, 0, 1, 1], [0, 1, 0, 1]])
matrix_inv = np.linalg.inv(matrix)

def getTimeDifferencePerRun(time_location):
    
    time_difference = np.zeros(len(time_location), dtype = time_location.dtype)

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")

    for chan in time_location.dtype.names:

        if md.getNameOfSensor(chan) == "SiPM-AFP":
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
def solveSystemOfEqs(sigma_convoluted_matrix, error_convoluted_matrix): #solveLinearEq

    # Get \sigma_{i}
    sigma_convoluted_squared = np.power(matrix.dot(sigma_convoluted_matrix).diagonal(), 2)
    sigma_squared = matrix_inv.dot(sigma_convoluted_squared)
    sigma = np.sqrt(sigma_squared)
 
    # Note, the error is of the form
    # \sigma_{ij}^2 \cdot (\Delta\sigma_{ij})^2 =
    # \sigma_{i}^2 \cdot (\Delta\sigma_{i})^2 + \sigma_{j}^2 \cdot (\Delta\sigma_{j})^2
    
    # Get \Delta\sigma_{i}
    sigma_error_convoluted_squared = np.power(matrix.dot(error_convoluted_matrix).diagonal(), 2)
    sigma_times_error_convoluted_squared = np.multiply(sigma_convoluted_squared, sigma_error_convoluted_squared)
    sigma_times_error_squared = matrix_inv.dot(sigma_times_error_convoluted_squared)
    error = np.divide(np.sqrt(sigma_times_error_squared), sigma)

    return sigma, error


def getSigmasFromFit(th1d_list, window_range, chan):

    # Find the maximal value
    MPV_bin = th1d_list.GetMaximumBin()
    MPV_time_diff = int(th1d_list.GetXaxis().GetBinCenter(MPV_bin))
    MPV_entries = th1d_list.GetMaximum()
    
    # Change the window
    xMin = MPV_time_diff - window_range
    xMax = MPV_time_diff + window_range
    th1d_list.SetAxisRange(xMin, xMax)
    
    # Fit using normal gaussian
    N = 3
    mean_window = th1d_list.GetMean()
    sigma_window = th1d_list.GetStdDev()
    xMin = mean_window - N * sigma_window
    xMax = mean_window + N * sigma_window
    
    # Within the same oscilloscope
    if md.checkIfSameOscAsSiPM(chan):
        
        fit_function = ROOT.TF1("gaus_fit", "gaus", xMin, xMax)

    # Else in different oscilloscopes
    else:
        fit_function = ROOT.TF1("gaus_fit", "[0]*exp(-0.5*((x-[2])/[3])^2) + [1]*exp(-0.5*((x-([2]+100))/[3])^2)", xMin, xMax)
        fit_function.SetParameters(MPV_entries, MPV_entries, mean_window, sigma_window)
        fit_function.SetParNames("Constant 1", "Constant 2", "Mean 1", "\sigma_{tot}")

    try:
        # Create fit and calculate the width
        th1d_list.Fit("gaus_fit", "Q", "", xMin, xMax)
        sigma_SiPM = md.getSigmaSiPM()
        if md.checkIfSameOscAsSiPM(chan):
            sigma_number = 2
            mean_number = 1
        else:
            sigma_number = 3
            mean_number = 2

        sigma_fit       = th1d_list.GetFunction("gaus_fit").GetParameter(sigma_number)
        sigma_fit_error = th1d_list.GetFunction("gaus_fit").GetParError(sigma_number)
        time_diff_mean  = th1d_list.GetFunction("gaus_fit").GetParameter(mean_number)
    
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
