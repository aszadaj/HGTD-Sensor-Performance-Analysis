import ROOT
import numpy as np
import root_numpy as rnm

import run_log_metadata as md
import data_management as dm


# Concatenate all runs for each batch. When the files are concatenated, produce plots for that batch until
# all batches are considered.
def noisePlots():

    print "\nStart producing NOISE plots, batches:", md.batchNumbers
        
    dm.defineDataFolderPath()
    for batchNumber in md.batchNumbers:
        
        print "Batch", batchNumber,"\n"

        noise_average   = np.empty(0)
        noise_std       = np.empty(0)

        runNumbers = md.getAllRunNumbers(batchNumber)
        
        if md.limitRunNumbers != 0:
            runNumbers = runNumbers[0:md.limitRunNumbers] # Restrict to some run numbers


        for runNumber in runNumbers:
            
            md.defineGlobalVariableRun(md.getRowForRunNumber(runNumber))
            
            print "Importing run", md.getRunNumber(), "\n"
            
            if noise_average.size == 0:
            
                noise_average  = dm.importNoiseFilePlot("pedestal")
                noise_std      = dm.importNoiseFilePlot("noise")
            
            else:

                noise_average = np.concatenate((noise_average, dm.importNoiseFilePlot("pedestal")), axis = 0)
                noise_std = np.concatenate((noise_std, dm.importNoiseFilePlot("noise")), axis = 0)
    
        if len(noise_average) != 0:
        
            print "Done with importing files for", batchNumber, "producing plots.\n"
        
            produceNoisePlots(noise_average, noise_std)

    print "Done with producing NOISE plots.\n"


def produceNoisePlots(noise_average, noise_std):
    
    global canvas, chan
    
    dm.convertNoiseData(noise_average, noise_std)
    
    canvas = ROOT.TCanvas("Noise", "noise")
    
    channels = noise_average.dtype.names
 
    # This is used to export data for pulse analysis. Takes the value from the
    # fitted function
    pedestal_data = dm.changeDTYPEOfData(np.empty(1, dtype=noise_average.dtype))
    noise_data    = dm.changeDTYPEOfData(np.empty(1, dtype=noise_std.dtype))
    
 
    # First fill pedestal and noise histograms and create fits
    for chan in channels:
        
        # Automized constants for setting the range of the TH1 graph
        width = 6
        
        pedestal_mean = np.average(noise_average[chan][np.nonzero(noise_average[chan])])
        pedestal_width  = np.std(noise_average[chan][np.nonzero(noise_average[chan])])
        
        pedestal_min = pedestal_mean - width * pedestal_width
        pedestal_max = pedestal_mean + width * pedestal_width
        
        noise_mean = np.average(noise_std[chan][np.nonzero(noise_std[chan])])
        noise_width  = np.std(noise_std[chan][np.nonzero(noise_std[chan])])
        
        noise_min = noise_mean - width * noise_width
        noise_max = noise_mean + width * noise_width
        
        
        pedestal_graph = ROOT.TH1D("Pedestal", "pedestal"+chan, 100, pedestal_min, pedestal_max)
        
        noise_graph    = ROOT.TH1D("Noise", "noise"+chan, 100, noise_min, noise_max)

        for entry in range(0, len(noise_average)):

            if noise_std[entry][chan] != 0:
                pedestal_graph.Fill(noise_average[entry][chan])
                noise_graph.Fill(noise_std[entry][chan])
    
        # Automized constants for setting the range of the Gauss Fit
        width = 4.5
    
        pedestal_min = pedestal_mean - width * pedestal_width
        pedestal_max = pedestal_mean + width * pedestal_width
        
        noise_min = noise_mean - width * noise_width
        noise_max = noise_mean + width * noise_width

        ROOT.gStyle.SetOptFit()

        pedestal_graph.Fit("gaus","Q","", pedestal_min, pedestal_max)
        noise_graph.Fit("gaus","Q","", noise_min, noise_max)
        
        yAxisTitle = "Entries"


        headTitle = "Noise - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"
        xAxisTitle = "Standard deviation [mV]"
        fileName = str(dm.getSourceFolderPath()) + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/noise/noise_plots/noise_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistograms(noise_graph, titles)
        
        
        headTitle = "Pedestal - "+md.getNameOfSensor(chan)+", T = "+str(md.getTemperature()) + " \circ"+"C, " + "U = "+str(md.getBiasVoltage(md.getNameOfSensor(chan), md.getBatchNumber())) + " V"
        xAxisTitle = "Average value [mV]"
        fileName = str(dm.getSourceFolderPath()) + "plots_hgtd_efficiency_sep_2017/"+md.getNameOfSensor(chan)+"/noise/pedestal_plots/pedestal_"+str(md.getBatchNumber())+"_"+chan+ "_"+str(md.getNameOfSensor(chan))+".pdf"
        titles = [headTitle, xAxisTitle, yAxisTitle, fileName]
        exportHistograms(pedestal_graph, titles)
        
        # Export results
        pedestal_result = np.empty(2, dtype=[('pedestal', '<f8')])
        noise_result    = np.empty(2, dtype=[('noise', '<f8')])
        
        pedestal_mean   = pedestal_graph.GetFunction("gaus").GetParameter(1)
        pedestal_error  = pedestal_graph.GetFunction("gaus").GetParError(1)
        
        noise_mean = noise_graph.GetFunction("gaus").GetParameter(1)
        noise_error = noise_graph.GetFunction("gaus").GetParError(1)

        pedestal_result["pedestal"][0] = pedestal_mean
        pedestal_result["pedestal"][1] = pedestal_error

        noise_result["noise"][0] = noise_mean
        noise_result["noise"][1] = noise_error
        
        # Export results per sensor
        sensor_info = [md.getNameOfSensor(chan), chan]
        dm.exportNoiseResults(pedestal_result, noise_result, sensor_info)
        

        # Export data to be used by the code (pulse calculation)
        pedestal_data[chan][0] = pedestal_mean*-0.001
        noise_data[chan][0] = noise_mean*0.001
        
        del pedestal_graph, noise_graph

    # Here export the data for pulse analysis
    dm.exportNoiseData(noise_data, pedestal_data)




# Produce histograms
def exportHistograms(graphList, titles):

    canvas.Clear()

    ROOT.gStyle.SetOptStat("ne")
    ROOT.gStyle.SetOptFit(0012)

    graphList.SetLineColor(1)
    graphList.SetTitle(titles[0])
    graphList.GetXaxis().SetTitle(titles[1])
    graphList.GetYaxis().SetTitle(titles[2])
    
    graphList.Draw()
    canvas.Update()
    dm.exportROOTHistogram(graphList, titles[3])
    canvas.Print(titles[3])

