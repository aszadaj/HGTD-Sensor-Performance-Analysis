import numpy as np
import metadata as md
import ROOT

def timingAnalysisPerRun(time_location):
    
    time_difference = np.zeros(len(time_location), dtype = time_location.dtype)
    
    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")

    for chan in time_location.dtype.names:

        if chan != SiPM_chan:
            
            for event in range (0, len(time_location)):
                if time_location[SiPM_chan][event] != 0 and time_location[chan][event] != 0:
                    # This is for the case if the SiPM is in the same oscilloscope as the DUT
                    time_difference[chan][event] = time_location[event][chan] - time_location[event][SiPM_chan]


    return time_difference


# This is used to produce ROOT files which have multiple solutions
# Note that the system of equations only applies to the first oscilloscope
# Reason: the first oscilloscope contains different sensors.
def timingAnalysisPerRunSysEq(time_location):
    
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


def getFitFunction(th1d_list, chan, same_osc):


    # Choose the range for the fit and the plot
    N = 2
    xMin = th1d_list.GetMean() - N * th1d_list.GetStdDev()
    xMax = th1d_list.GetMean() + N * th1d_list.GetStdDev()
    
    # For the case when the large peak is on the right
    bin_high_peak = th1d_list.GetMaximumBin()
    mean_value_high_peak = int(th1d_list.GetXaxis().GetBinCenter(bin_high_peak))
    amplitude_high_peak = th1d_list.GetMaximum()
    
    # Change manually depending if the peak is on the left or right side
    largePeakOnRight = True
    timeScopeShift = -100
    batchConfig = md.getBatchNumber()/100
    
    # How the shift behaves, based on observation from plots
    if batchConfig == 1 or batchConfig == 2 or batchConfig == 4:
        largePeakOnRight = False
        timeScopeShift = 100
    
    elif int(md.getBatchNumber()/100) == 5:
        largePeakOnRight = False
        timeScopeShift = 100
    
    mean_value_low_peak = mean_value_high_peak + timeScopeShift
    bin_low_peak = th1d_list.FindBin(mean_value_low_peak)
    amplitude_low_peak = th1d_list.GetBinContent(bin_low_peak)
    sigma_double_peak = th1d_list.GetStdDev()

    
    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")

    # Within the same oscilloscope
    if same_osc:

        # Fit using normal gaussian
        defined_fit = ROOT.TF1("gaussian_mod_fit", "gaus", xMin, xMax)


    # Else in different oscilloscopes
    else:

        defined_fit = ROOT.TF1("gaussian_mod_fit", "[0]*exp(-0.5*((x-[1])/[2])^2) + [3]*exp(-0.5*((x-([1]+100))/[2])^2)", xMin, xMax)

        if largePeakOnRight:

            defined_fit.SetParameters(amplitude_low_peak, mean_value_high_peak, sigma_double_peak, amplitude_high_peak)
            defined_fit.SetParNames("Constant low peak", "Mean high peak ", "\sigma_{tot}", "Constant high peak")

        else:            
            defined_fit.SetParameters(amplitude_high_peak, mean_value_high_peak, sigma_double_peak, amplitude_low_peak)
            defined_fit.SetParNames("Constant high peak", "Mean high peak", "\sigma_{tot}", "Constant low peak")


    th1d_list.Fit("gaussian_mod_fit", "Q", "", xMin, xMax)
    fit_function = th1d_list.GetFunction("gaussian_mod_fit")
    
    
    fit_function.SetRange(xMin, xMax)
    
    N = 4
    xMin = th1d_list.GetMean() - N * th1d_list.GetStdDev()
    xMax = th1d_list.GetMean() + N * th1d_list.GetStdDev()
    th1d_list.SetAxisRange(xMin, xMax)
        
    sigma_SiPM = 15
    
    if md.getTemperature() < 0:
        sigma_SiPM = 9
    
    sigma_fit = fit_function.GetParameter(2)
    sigma_fit_error = fit_function.GetParError(2)
    
    # Here assume that the error is zero fro


    if sigma_fit > sigma_SiPM:
        sigma_DUT = np.sqrt(np.power(sigma_fit, 2) - np.power(sigma_SiPM, 2))

    else:
        sigma_DUT = 0


    del defined_fit

    return fit_function, sigma_DUT, sigma_fit_error
