import ROOT
import metadata as md


def producePulseDistributionPlots(amplitudes, rise_times, pulse_points, del_amplitudes):

    global deleted_amplitudes
    deleted_amplitudes = del_amplitudes
    
    canvas_amplitude = ROOT.TCanvas("Amplitude Distribution", "amplitude")
    canvas_rise_time = ROOT.TCanvas("Risetime Distribution", "risetime")
    canvas_pulse_points = ROOT.TCanvas("Pulse data points", "pulse_points")

    amplitudes_graph = dict()
    rise_times_graph = dict()
    pulse_points_graph = dict()
    
    for chan in amplitudes.dtype.names:
        
        amplitudes_graph[chan] = ROOT.TH1D("Amplitude channel "+str(int(chan[-1:])+1), "amplitude" + chan,1000,0,400)
        
        rise_times_graph[chan] = ROOT.TH1D("Rise time channel "+str(int(chan[-1:])+1), "rise_time" + chan,600,0.3,1.5)
        
        pulse_points_graph[chan] = ROOT.TH1D("Pulse points, channel "+str(int(chan[-1:])+1), "pulse_points" + chan,600,0,130)
        
        index = int(chan[-1:])
        
        # Exclude filling histograms with critical amplitude values
        for entry in range(0,len(amplitudes[chan])):
            if amplitudes[chan][entry] != 0 and rise_times[chan][entry] != 0:
                amplitudes_graph[chan].Fill(amplitudes[chan][entry])
                rise_times_graph[chan].Fill(rise_times[chan][entry])
            
            if pulse_points[chan][entry] != -1:
                pulse_points_graph[chan].Fill(pulse_points[chan][entry])
    
    
        ### Export ROOT files!! ###
        
        typeOfGraph = "amplitude"
        defineAndProduceHistogram(amplitudes_graph[chan],canvas_amplitude,typeOfGraph,chan)
        typeOfGraph = "rise_time"
        defineAndProduceHistogram(rise_times_graph[chan],canvas_rise_time,typeOfGraph,chan)
        typeOfGraph = "pulse_point"
        defineAndProduceHistogram(pulse_points_graph[chan],canvas_pulse_points,typeOfGraph,chan)


# Produce TH1 plots and export them as a PDF file
def defineAndProduceHistogram(graphList,canvas,typeOfGraph,chan):
  
    headTitle = "Distribution of pulse rise times, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan))
    xAxisTitle = "Time (ns)"
    yAxisTitle = "Number (N)"
    fileName = "../../HGTD_material/plots_hgtd_efficiency_sep_2017/pulse/rise_time_plots/rise_time_distribution_"+str(md.getBatchNumber())+"_"+chan+".pdf"
    
    
    if typeOfGraph == "amplitude":
    
        headTitle = "Distribution of pulse amplitudes, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan))
        xAxisTitle = "Amplitude (mV)"
        fileName = "../../HGTD_material/plots_hgtd_efficiency_sep_2017/pulse/amplitude_plots/amplitude_distribution_"+str(md.getBatchNumber())+"_"+chan+".pdf"
    
    elif typeOfGraph == "pulse_point":
    
        headTitle = "Distribution of pulse points for found pulse, Sep 2017 batch "+str(md.getBatchNumber())+", channel " + str(int(chan[-1:])+1) + ", sensor: " + str(md.getNameOfSensor(chan)) + " fraction of removed amplitudes (critical values): " + str(float(deleted_amplitudes[chan])*100) + " %"
        xAxisTitle = "Data points (mV)"
        fileName = "../../HGTD_material/plots_hgtd_efficiency_sep_2017/pulse/pulse_points/pulse_points_distribution_"+str(md.getBatchNumber())+"_"+chan+".pdf"
    

    graphList.SetLineColor(1)
    graphList.SetMarkerColor(1)
    graphList.GetYaxis().SetTitle(yAxisTitle)
    graphList.GetXaxis().SetTitle(xAxisTitle)
    
    graphList.SetTitle(headTitle)
    
    canvas.cd()
    graphList.Draw()
    canvas.Update()
    canvas.Print(fileName)
