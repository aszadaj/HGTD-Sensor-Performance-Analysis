import numpy as np
import metadata as md
import ROOT

def getTimeDifferencePerRun(time_location):
    
    time_difference = np.zeros(len(time_location), dtype = time_location.dtype)
    
    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")

    for chan in time_location.dtype.names:
        
        if SiPM_chan == chan:
            continue
            
        for event in range (0, len(time_location)):
            if time_location[SiPM_chan][event] != 0 and time_location[chan][event] != 0:
                time_difference[chan][event] = (time_location[chan][event] - time_location[SiPM_chan][event])*1000


    return time_difference


# This is used to produce ROOT files which have multiple solutions
# Note that the system of equations only applies to the first oscilloscope
# Reason: the first oscilloscope contains different sensors.
def getTimeDifferencePerRunSysEq(time_location):
    
    dt = (  [('chan0',  '<f8', 3), ('chan1',  '<f8', 3) ,('chan2',  '<f8', 3) ,('chan3',  '<f8', 3)] )
    
    time_difference = np.zeros(len(time_location), dtype = dt)

    osc1 = ["chan0", "chan1", "chan2", "chan3"]

    for chan in osc1:
    
        chan2_list = list(osc1)
        chan2_list.remove(chan)
        
        for event in range(0, len(time_location[chan])):
            
            time_difference[chan][event] = np.zeros(3)
            
            for index in range(0, len(chan2_list)):
                chan2 = chan2_list[index]
                if time_location[chan][event] != 0 and time_location[chan2][event] != 0:
                   
                    value = (time_location[chan][event] - time_location[chan2][event])*1000
                    time_difference[chan][event][index] = value


    return time_difference

# Solve system of linear equation
# Note, there are multiple to choose from, 4 unknowns, 6 different equations, not all are independent
def solveLinearEq(sigmas_mix):

    # Non-singular matrix selected
    matrix = np.matrix([[1, 0, 0, 1], [0, 1, 1, 0], [0, 0, 1, 1], [0, 1, 0, 1]])
    inverse = np.linalg.inv(matrix)
    vector = np.array([sigmas_mix[0][3], sigmas_mix[1][2], sigmas_mix[2][3], sigmas_mix[1][3]])
    vector = np.power(vector, 2)
    solution = inverse.dot(vector)
    sigma_chan = np.sqrt(solution)
    
    # Warning, need to take into consideration the error as a function of two variables
    
    return sigma_chan


def getSigmasFromFit(th1d_list, chan):

    # Find the maximal value
    MPV_bin = th1d_list.GetMaximumBin()
    MPV_time_diff = int(th1d_list.GetXaxis().GetBinCenter(MPV_bin))
    MPV_entries = th1d_list.GetMaximum()
    
    # Change the window
    window_range = 1000
    xMin = MPV_time_diff - window_range
    xMax = MPV_time_diff + window_range
    th1d_list.SetAxisRange(xMin, xMax)
    
    # Fit using normal gaussian
    N = 1
    sigma_window = th1d_list.GetStdDev()
    mean_window = th1d_list.GetMean()
    xMin = mean_window - N * sigma_window
    xMax = mean_window + N * sigma_window

    # Within the same oscilloscope
    if md.checkIfSameOscAsSiPM(chan):
        
        fit_function = ROOT.TF1("gaus_fit", "gaus", xMin, xMax)

    # Else in different oscilloscopes
    else:

        fit_function = ROOT.TF1("gaus_fit", "[0]*exp(-0.5*((x-[3])/[2])^2) + [1]*exp(-0.5*((x-([3]+100))/[2])^2)", xMin, xMax)
        fit_function.SetParameters(MPV_entries, MPV_entries, sigma_window, mean_window)
        fit_function.SetParNames("Constant 1", "Constant 2", "\sigma_{tot}", "Mean 1")

    try:
        # Create fit and calculate the width
        th1d_list.Fit("gaus_fit", "Q", "", xMin, xMax)
        sigma_SiPM = md.getSigmaSiPM()
        sigma_fit = th1d_list.GetFunction("gaus_fit").GetParameter(2)
        sigma_fit_error = th1d_list.GetFunction("gaus_fit").GetParError(2)
    
        if sigma_fit > sigma_SiPM:
            sigma_DUT = np.sqrt(np.power(sigma_fit, 2) - np.power(sigma_SiPM, 2))

        else:
            sigma_DUT = 0

    # In case that the fit fails, due to no data, ignore the result.
    except:

        sigma_DUT = 0
        sigma_fit_error = 0


    return sigma_DUT, sigma_fit_error
