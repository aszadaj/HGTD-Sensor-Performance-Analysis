import ROOT
import metadata as md
import numpy as np

import data_management as dm
import timing_calculations as t_calc

def timingPlots():

    print "\nStart producing TIMING plots, batches:", md.batchNumbers
    
    for batchNumber in md.batchNumbers:
        
        print "\nBatch", batchNumber,"\n"
        
        dm.checkIfRepositoryOnStau()
        
        time_difference_linear = np.empty(0)
        time_difference_sys_eq = np.empty(0)
        
        time_difference_linear_rise_time_ref = np.empty(0)
        time_difference_sys_eq_rise_time_ref = np.empty(0)
        
        peak_values = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers
        
        availableRunNumbersPeakTimes = md.readFileNames("pulse_peak_time")
        
        numberOfEventPerRun = [0]
        
        for runNumber in runNumbers:
        
            print runNumber
            if runNumber in availableRunNumbersPeakTimes:
                md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
                
                print "Importing run", md.getRunNumber(), "\n"

                if time_difference_linear.size == 0:
          
                    time_difference_linear  = dm.importTimingFile("linear")
                    time_difference_sys_eq  = dm.importTimingFile("sys_eq")
                    
                    time_difference_linear_rise_time_ref  = dm.importTimingFile("linear_rise_time_ref")
                    time_difference_sys_eq_rise_time_ref  = dm.importTimingFile("sys_eq_rise_time")
                    
                    
                    peak_values = dm.importPulseFile("peak_value")
                
                else:

                    time_difference_linear = np.concatenate((time_difference_linear, dm.importTimingFile("linear")), axis = 0)
                    time_difference_sys_eq = np.concatenate((time_difference_sys_eq, dm.importTimingFile("sys_eq")), axis = 0)
                    
                    time_difference_linear_rise_time_ref = np.concatenate((time_difference_linear_rise_time_ref, dm.importTimingFile("linear_rise_time_ref")), axis = 0)
                    time_difference_sys_eq_rise_time_ref = np.concatenate((time_difference_sys_eq_rise_time_ref, dm.importTimingFile("sys_eq_rise_time")), axis = 0)
                    
                    peak_values = np.concatenate((peak_values, dm.importPulseFile("peak_value")), axis = 0)
                    
                # Since the values are concatenated, number of events are tracked
                
                numberOfEventPerRun.append(len(time_difference_linear))
        
        if len(peak_values) != 0:
        
            print "Done with importing files for", batchNumber
            print "Producing plots.\n"

            produceTimingDistributionPlots(time_difference_linear, peak_values, numberOfEventPerRun)
            produceTimingDistributionPlotsSysEq(time_difference_sys_eq, peak_values, numberOfEventPerRun)
            
            produceTimingDistributionPlots(time_difference_linear_rise_time_ref, peak_values, numberOfEventPerRun, True)
            produceTimingDistributionPlotsSysEq(time_difference_sys_eq_rise_time_ref, peak_values, numberOfEventPerRun, True)


    print "Done with producing TIMING plots.\n"


def produceTimingDistributionPlots(time_difference, peak_value, numberOfEventPerRun, rise_time_ref = False):

    time_diff = dict()
    fit_function = dict()

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    
    channels = time_difference.dtype.names

    global canvas
    global chan

    canvas = ROOT.TCanvas("Timing", "timing")
    
    xbins = 3300
    xbin_low = -15000
    xbin_high = 15000
    
    #channels = ["chan1"]

    for chan in channels:
        if chan != SiPM_chan:
            index = int(chan[-1:])

            # TH1 object
            time_diff[chan] = ROOT.TH1D("Time difference "+md.getNameOfSensor(chan), "time_difference" + chan, xbins, xbin_low, xbin_high)
         
            # Fill TH1 object and cut the noise for the DUT and SiPM < 200 mV, specified in run log
            for entry in range(0, len(time_difference[chan])):
                if time_difference[chan][entry] != 0 and peak_value[chan][entry] < md.getPulseAmplitudeCut(chan) and peak_value[SiPM_chan][entry] < md.getPulseAmplitudeCut(SiPM_chan):
                    time_diff[chan].Fill(time_difference[chan][entry]*1000)
        
            # Remove bins with less than 4 entries
            for bin in range(1, xbins+1):

                num = time_diff[chan].GetBinContent(bin)

                if num < 5:
                    time_diff[chan].SetBinContent(bin, 0)

            time_diff[chan].ResetStats()


            # Choose the range for the fit and the plot
            N = 4
            xMin = time_diff[chan].GetMean() - N * time_diff[chan].GetStdDev()
            xMax = time_diff[chan].GetMean() + N * time_diff[chan].GetStdDev()
            
            # For the case when the large peak is on the right
            bin_high_peak = time_diff[chan].GetMaximumBin()
            mean_value_high_peak = int(time_diff[chan].GetXaxis().GetBinCenter(bin_high_peak))
            amplitude_high_peak = time_diff[chan].GetMaximum()
            
            # Change manually depending if the peak is on the left or right side
            largePeakOnRight = True
            timeScopeShift = -100
            
            if int(md.getBatchNumber()/100) == 1 or int(md.getBatchNumber()/100) == 2 or int(md.getBatchNumber()/100) == 4:
                largePeakOnRight = False
                timeScopeShift = 100
            
            elif int(md.getBatchNumber()/100) == 5:
                largePeakOnRight = False
                timeScopeShift = 100
                

            # The shift needs to be changed depending on time difference between the DUT and SiPM

            mean_value_low_peak = mean_value_high_peak + timeScopeShift
            bin_low_peak = time_diff[chan].FindBin(mean_value_low_peak)
            amplitude_low_peak = time_diff[chan].GetBinContent(bin_low_peak)
            sigma_double_peak = time_diff[chan].GetStdDev()
            
            
            
            # Fit using two default gaussians
#            fit_option = 1
#            defined_fit = ROOT.TF1("gaussian_mod_fit", "gaus(0) + gaus(3)", xMin, xMax)
#            defined_fit.SetParNames(amplitude_low_peak, mean_value_low_peak, sigma_double_peak*0.5, amplitude_high_peak, mean_value_high_peak, sigma_double_peak*0.5)

            # Fit using predefined function
#            fit_option = 2
#            defined_fit = ROOT.TF1("gaussian_mod_fit", "[0]*exp(-0.5*((x-[1])/[4])^2) + [2]*exp(-0.5*((x-[3])/[4])^2)", xMin, xMax)
#            defined_fit.SetParameters(amplitude_low_peak, mean_value_low_peak, amplitude_high_peak, mean_value_high_peak, sigma_double_peak)
#            defined_fit.SetParNames("Norm 1", "Mean value 1", "Norm 2", "Mean value 2", "Width both")

            fit_option = 0
            defined_fit = ""


            # In oscilloscope 1
            if int(SiPM_chan[-1]) < 4 and int(chan[-1]) < 4:

                # Fit using normal gaussian
                fit_option = 3
                defined_fit = ROOT.TF1("gaussian_mod_fit", "gaus", xMin, xMax)
            
            # In oscilloscope 2
            elif int(SiPM_chan[-1]) > 3 and int(chan[-1]) > 3:
            
                # Fit using normal gaussian
                fit_option = 3
                defined_fit = ROOT.TF1("gaussian_mod_fit", "gaus", xMin, xMax)
            
            # Else in different oscilloscopes
            else:

                # Fit using a modified of number 2
                fit_option = 4
                defined_fit = ROOT.TF1("gaussian_mod_fit", "[0]*exp(-0.5*((x-[1])/[2])^2) + [3]*exp(-0.5*((x-[1]+100)/[2])^2)", xMin, xMax)

                if largePeakOnRight:

                    defined_fit.SetParameters(amplitude_low_peak, mean_value_high_peak, sigma_double_peak, amplitude_high_peak)
                    defined_fit.SetParNames("Norm low peak", "Mean value high peak", "Width", "Norm high peak")

                else:

                    defined_fit.SetParameters(amplitude_high_peak, mean_value_high_peak, sigma_double_peak/2, amplitude_low_peak)
                    defined_fit.SetParNames("Norm high peak", "Mean value high peak", "Width", "Norm low peak")


            time_diff[chan].Fit("gaussian_mod_fit", "Q", "", xMin, xMax)
            fit_function[chan] = time_diff[chan].GetFunction("gaussian_mod_fit")

            # Change the range of the plot
            N = 4
            xMin = time_diff[chan].GetMean() - N * time_diff[chan].GetStdDev()
            xMax = time_diff[chan].GetMean() + N * time_diff[chan].GetStdDev()
            time_diff[chan].SetAxisRange(xMin, xMax)
            fit_function[chan].SetRange(xMin, xMax)
            
            # Calculate the time resolution given that the SiPM is in the same oscilloscope as the DUT.
            
            sigma_fit = 0
            
            if fit_option == 1:
                sigma_fit = (fit_function[chan].GetParameter(2) + fit_function[chan].GetParameter(5))/2
            elif fit_option == 2:
                sigma_fit = fit_function[chan].GetParameter(4)
            else:
                sigma_fit = fit_function[chan].GetParameter(2)
            
            # This is the averaged value of calculated time resolution using linear sys equations
            sigma_SiPM = 16.14
            sigma_DUT = np.sqrt( np.power(sigma_fit,2) - np.power(sigma_SiPM, 2)  )


            # Print 1D plot time difference distribution
            headTitle = "Time difference SiPM and "+md.getNameOfSensor(chan)+" B"+str(md.getBatchNumber())
            xAxisTitle = "\Delta t_{SiPM-LGAD} (ps)"
            yAxisTitle = "Number (N)"
            fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
            
            if rise_time_ref:
                headTitle = "Time difference SiPM and "+md.getNameOfSensor(chan)+" B"+str(md.getBatchNumber())
                xAxisTitle = "\Delta t_{SiPM-LGAD} (ps)"
                yAxisTitle = "Number (N)"
                fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+"_rise_time_ref.pdf"
            
            titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
            exportTHPlot(time_diff[chan], titles, "", fit_function[chan], sigma_DUT)


# Use this method to calculate the linear system of equations solution
def produceTimingDistributionPlotsSysEq(time_difference, peak_value, numberOfEventPerRun, rise_time_ref = False):
    
    # TH1 objects
    time_diff = dict()
    fit_function = dict()

    SiPM_chan = md.getChannelNameForSensor("SiPM-AFP")
    
    channels = time_difference.dtype.names

    global canvas
    global chan

    canvas = ROOT.TCanvas("Timing", "timing")
    
    xbins = 6000
    
    osc1 = ["chan0", "chan1", "chan2", "chan3"]
    s = (4,4)
    sigmas_mix = np.zeros(s)
    
    for chan in osc1:
        
        # Do not consider the same channel when comparing two
        chan2_list = list(osc1)
        chan2_list.remove(chan)
        
        # Create TH1 object
        time_diff[chan] = dict()
        for chan2 in chan2_list:
        
            time_diff[chan][chan2] = ROOT.TH1D("System of equations \sigma_{"+chan[-1]+chan2[-1]+"}", "time_difference" + chan, xbins, -15000, 15000)
        
        # Fill TH1 object between channels in oscilloscope
        for entry in range(0, len(time_difference[chan])):
            for index in range(0, len(chan2_list)):
                chan2 = chan2_list[index]
                if time_difference[chan][entry][index] != 0 and peak_value[chan][entry] < md.getPulseAmplitudeCut(chan) and peak_value[chan2][entry] < md.getPulseAmplitudeCut(chan2):
                    time_diff[chan][chan2].Fill(time_difference[chan][entry][index])
        
        for chan2 in chan2_list:
            for bin in range(1, xbins+1):
        
                num = time_diff[chan][chan2].GetBinContent(bin)

                if num < 2:
                    time_diff[chan][chan2].SetBinContent(bin, 0)
            
            time_diff[chan][chan2].ResetStats()

        # Get sigma and adapt distribution curve
        for chan2 in chan2_list:
            
            i = int(chan[-1]) % 4
            j = int(chan2[-1]) % 4
            
            # Choose the range for the fit
            N = 4
            xMin = time_diff[chan][chan2].GetMean() - N * time_diff[chan][chan2].GetStdDev()
            xMax = time_diff[chan][chan2].GetMean() + N * time_diff[chan][chan2].GetStdDev()
          
            # Obtain the parameters
            time_diff[chan][chan2].Fit("gaus", "Q0", "", xMin, xMax)
            fit_function = time_diff[chan][chan2].GetFunction("gaus")
            fitted_parameters = [fit_function.GetParameter(0), fit_function.GetParameter(1), fit_function.GetParameter(2)]
            
            
            # Get sigma between two channels
            
            sigmas_mix[i][j] = fit_function.GetParameter(2)
            sigmas_mix[j][i] = fit_function.GetParameter(2)

    # Obtain the sigmas for each channel


    #sigmas_chan = t_calc.solveLinearEq(sigmas_mix)


    for chan in osc1:
        chan2_list = list(osc1)
        chan2_list.remove(chan)
    
        for chan2 in chan2_list:
        
            if md.getNameOfSensor(chan) != md.getNameOfSensor(chan2):

                index = int(chan[-1]) % 4
                
                # Rescale the range of the plot, to make the plot look better
                N = 4
                xMin = time_diff[chan][chan2].GetMean() - N * time_diff[chan][chan2].GetStdDev()
                xMax = time_diff[chan][chan2].GetMean() + N * time_diff[chan][chan2].GetStdDev()
                
                # Obtain the parameters
                time_diff[chan][chan2].Fit("gaus", "Q0", "", xMin, xMax)
                fit_function = time_diff[chan][chan2].GetFunction("gaus")
                fitted_parameters = [fit_function.GetParameter(0), fit_function.GetParameter(1), fit_function.GetParameter(2)]
                
                # Add the fit function
                fit_function_adapted = ROOT.TF1("fit_peak_1", "gaus", xMin, xMax)
                fit_function_adapted.SetParameters(fitted_parameters[0], fitted_parameters[1], fitted_parameters[2])
                time_diff[chan][chan2].SetAxisRange(xMin, xMax)


                # Print 1D plot time difference distribution
                headTitle = "Time difference "+md.getNameOfSensor(chan)+" and "+md.getNameOfSensor(chan2)+" B"+str(md.getBatchNumber())
                xAxisTitle = "\Delta t_{DUT1 - DUT2} (ps)"
                yAxisTitle = "Number (N)"
                fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+"_and_"+str(md.getNameOfSensor(chan2))+".pdf"
                
                if rise_time_ref:
                
                    headTitle = "Time difference "+md.getNameOfSensor(chan)+" and "+md.getNameOfSensor(chan2)+" B"+str(md.getBatchNumber())
                    xAxisTitle = "\Delta t_{DUT1 - DUT2} (ps)"
                    yAxisTitle = "Number (N)"
                    fileName = dm.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/timing/timing_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+"_and_"+str(md.getNameOfSensor(chan2))+"_rise_time_ref.pdf"
            
                titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
                exportTHPlot(time_diff[chan][chan2], titles, "", fit_function_adapted, sigmas_chan.item((0, index)))




def exportTHPlot(graphList, titles, drawOption, fit, sigma=0):
 
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    ROOT.gStyle.SetOptFit()
    ROOT.gStyle.SetOptStat("ne")

    graphList.Draw()
    fit.Draw("SAME")
  
    canvas.Update()
    
    ## Remove text from stats box
    statsBox = canvas.GetPrimitive("stats")
    statsBox.SetName("Mystats")
    
    graphList.SetStats(0)

    linesStatsBox = statsBox.GetListOfLines()

#    textMean = statsBox.GetLineWith("Mean")
#    linesStatsBox.Remove(textMean)
#    textConstant = statsBox.GetLineWith("Constant")
#    linesStatsBox.Remove(textConstant)
#    textSigma = statsBox.GetLineWith("Sigma")
#    linesStatsBox.Remove(textSigma)

    statsBox.AddText("\sigma_{"+md.getNameOfSensor(chan)+"} = "+str(sigma)[0:6])
    canvas.Modified()
    canvas.Update()
    

    canvas.Print(titles[3])
    canvas.Clear()

