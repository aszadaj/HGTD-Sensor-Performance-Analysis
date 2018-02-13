import ROOT
import metadata as md
import numpy as np
import data_management as dm


ROOT.gStyle.SetOptFit()


# Concatenate all runs for each batch. When the files are concatenated, produce plots for that batch until
# all batches are considered.
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
    

    for chan in peak_times.dtype.names:
    
        index = int(chan[-1:])
        
        peak_times_graph[chan] = ROOT.TH1D("Peak time channel "+str(index), "peak_time" + chan, 1000, 0, 100)
        peak_values_graph[chan] = ROOT.TH1D("Peak value channel "+str(index), "peak_value" + chan, 1000, 0, 400)
        rise_times_graph[chan] = ROOT.TH1D("Rise time channel "+str(index), "rise_time" + chan, 1000, 0, 2)
        
        
        for entry in range(0, len(peak_values[chan])):
   
            if peak_times[chan][entry] != 0:
                peak_times_graph[chan].Fill(peak_times[chan][entry])
            
            if peak_values[chan][entry] != 0:
                peak_values_graph[chan].Fill(peak_values[chan][entry])
            
            if rise_times[chan][entry] != 0:
                rise_times_graph[chan].Fill(rise_times[chan][entry])
    


        headTitle = "Distribution of pulse peak times, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan))
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Number (N)"
        fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_time_plots/peak_time_distribution_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(peak_times_graph[chan], titles)
        
        headTitle = "Distribution of pulse peak values, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan))
        xAxisTitle = "Amplitude (mV)"
        yAxisTitle = "Number of entries (N)"
        fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/peak_value_plots/peak_value_distribution_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(peak_values_graph[chan], titles)
        
        headTitle = "Distribution of pulse rise times, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])) + ", sensor: " + str(md.getNameOfSensor(chan))
        xAxisTitle = "Time (ns)"
        yAxisTitle = "Number of entries (N)"
        fileName = md.getSourceFolderPath() + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/pulse/rise_time_plots/rise_time_distribution_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistogram(rise_times_graph[chan], titles)


# Produce histograms
def exportHistogram(graphList, titles):

    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    graphList.Draw()
    canvas.Update()
    canvas.Print(titles[3])
