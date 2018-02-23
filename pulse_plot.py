import ROOT
import metadata as md
import numpy as np
import data_management as dm


ROOT.gStyle.SetOptFit()


# Concatenate all runs for each batch. When the files are concatenated, produce plots for that batch until
# all batches are considered.

# Test
def pulsePlots():

    print "\nStart producing PULSE plots, batches:", md.batchNumbers
    
    for batchNumber in md.batchNumbers:
        
        print "Batch", batchNumber,"\n"
        
        dm.checkIfRepositoryOnStau()
        
        peak_times = np.empty(0)
        peak_values = np.empty(0)
        rise_times = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers
        
        availableRunNumbersPeakTimes    = md.readFileNames("pulse_peak_time")
        availableRunNumbersPeakValues   = md.readFileNames("pulse_peak_value")
        availableRunNumbersRiseTimes    = md.readFileNames("pulse_rise_time")
    
        for runNumber in runNumbers:
            
            if runNumber in availableRunNumbersPeakTimes:
                md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
          
                print "Importing run", md.getRunNumber(), "\n"

                if peak_times.size == 0:
          
                    peak_times  = dm.importPulseFile("peak_time")
                    peak_values = dm.importPulseFile("peak_value")
                    rise_times  = dm.importPulseFile("rise_time")

                else:

                    peak_times = np.concatenate((peak_times, dm.importPulseFile("peak_time")), axis = 0)
                    peak_values = np.concatenate((peak_values, dm.importPulseFile("peak_value")), axis = 0)
                    rise_times = np.concatenate((rise_times, dm.importPulseFile("rise_time")), axis = 0)
                    
        if len(peak_times) != 0:
        
            print "Done with importing files for", batchNumber, "producing plots.\n"

            producePulsePlots(peak_times, peak_values, rise_times, batchNumber)

    print "Done with producing PULSE plots.\n"


# Fill TH1 objects
def producePulsePlots(peak_times, peak_values, rise_times, batchNumber):

    global canvas
    
    peak_values = dm.convertPulseData(peak_values)
    
    canvas = ROOT.TCanvas("Pulse", "pulse")

    peak_times_graph = dict()
    peak_values_graph = dict()
    rise_times_graph = dict()
    
    xbins = 800
    
    channels = peak_times.dtype.names
    
    #channels = ["chan0"]

    for chan in channels:

        peak_times_graph[chan] = ROOT.TH1D("Time reference " + md.getNameOfSensor(chan), "peak_time" + chan, 1000, 20, 80)
        peak_values_graph[chan] = ROOT.TH1D("Amplitude " + md.getNameOfSensor(chan), "peak_value" + chan, 700, 0, 400)
        rise_times_graph[chan] = ROOT.TH1D("Rise time " + md.getNameOfSensor(chan), "rise_time" + chan, xbins, 0, 1.5)
        

        for entry in range(0, len(peak_times[chan])):
   
            if peak_times[chan][entry] != 0:
                peak_times_graph[chan].Fill(peak_times[chan][entry])
            
            if peak_values[chan][entry] != 0:
                peak_values_graph[chan].Fill(peak_values[chan][entry])
            
            if rise_times[chan][entry] != 0:
                rise_times_graph[chan].Fill(rise_times[chan][entry])
    
#        # Remove bins with less than some entries for all three objects
#
#        count_peak_times = 0
#        count_peak_values = 0
#        count_rise_times = 0
#
#        minEntries = 2 * md.getNumberOfRunsPerBatch()
#
#        for bin in range(1, xbins):
#
#            num_peak_times = peak_times_graph[chan].GetBinContent(bin)
#            num_peak_values = peak_values_graph[chan].GetBinContent(bin)
#            num_rise_times = rise_times_graph[chan].GetBinContent(bin)
#
#            if num_peak_times < minEntries:
#                peak_times_graph[chan].SetBinContent(bin, 0)
#                count_peak_times += 1
#
#            if num_peak_values < minEntries:
#                peak_values_graph[chan].SetBinContent(bin, 0)
#                count_peak_values += 1
#
#            if num_rise_times < minEntries:
#                rise_times_graph[chan].SetBinContent(bin, 0)
#                count_rise_times += 1
#
#
#        # SetBinContent(bin, 0) increases an entry by 1.
#        peak_times_graph[chan].SetEntries((int(peak_times_graph[chan].GetEntries()) - count_peak_times))
#        peak_values_graph[chan].SetEntries((int(peak_values_graph[chan].GetEntries()) - count_peak_values))
#        rise_times_graph[chan].SetEntries((int(rise_times_graph[chan].GetEntries()) - count_rise_times))

    
        # Adapt rise time graph to be adapted for gauss fit
        N = 5
        
        xMin = rise_times_graph[chan].GetMean() - N * rise_times_graph[chan].GetStdDev()
        xMax = rise_times_graph[chan].GetMean() + N * rise_times_graph[chan].GetStdDev()
        

        # Create a gaus distribution for rise time
        rise_times_graph[chan].Fit("gaus","","", xMin, xMax)
        
        N = 7
        xMin = rise_times_graph[chan].GetMean() - N * rise_times_graph[chan].GetStdDev()
        xMax = rise_times_graph[chan].GetMean() + N * rise_times_graph[chan].GetStdDev()
    

        # Print peak time, peak value and rise time graphs and export them
        headTitle = "Time at peak location, "+md.getNameOfSensor(chan)+", Sep 2017 B"+str(md.getBatchNumber())
        #headTitle = "Time at 50% of the rising edge, "+md.getNameOfSensor(chan)+", Sep 2017 B"+str(md.getBatchNumber())
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Number (N)"
        fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_time_plots/time_reference_peak_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(peak_times_graph[chan], titles)
        
        headTitle = "Pulse amplitudes, "+md.getNameOfSensor(chan)+", Sep 2017 B"+str(md.getBatchNumber())
        xAxisTitle = "Amplitude (mV)"
        yAxisTitle = "Number of entries (N)"
        fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_value_plots/pulse_amplitude_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(peak_values_graph[chan], titles)
        
        headTitle = "Rise times, "+md.getNameOfSensor(chan)+", Sep 2017 B"+str(md.getBatchNumber())
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Number of entries (N)"
        fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/rise_time_plots/rise_time_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        ranges = [xMin, xMax]
        exportHistogram(rise_times_graph[chan], titles, ranges)


# Produce histograms
def exportHistogram(graphList, titles, ranges=[]):
    
    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    if ranges:
        graphList.SetAxisRange(ranges[0], ranges[1])
    
    graphList.Draw()
    canvas.Update()
    canvas.Print(titles[3])
