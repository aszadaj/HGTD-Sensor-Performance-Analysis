import ROOT
import numpy as np

# create the TFile object for reading the input file
f = ROOT.TFile("~/data_1504818689.tree.root")

# get the TTree from the TFile
t  = f.Get("oscilloscope")

# need some spacing in the x-axis for the samples, i.e. the sampling period of the scope
dt = 0.1 # guessing, in ns

data = [[] for _ in range(8)] # Nested tuple, two dimensional
c1 = ROOT.TCanvas("Noises", "Noises")
graphs_noise = {}
graphs_histogram = {}



# loop over entries
for e in range(1,100): #t.GetEntries()):
    t.GetEntry(e-1)
    setTitleAboveGraph = "Noise - Entry "+ str(e) # To be used later
    channelCounter = 0
    graphs_noise_multi = ROOT.TMultiGraph()
    
    # Loop over all channels
    for chan in [t.chan0, t.chan1, t.chan2, t.chan3, t.chan4, t.chan5, t.chan6, t.chan7]:
        chan_np = np.asarray(chan,'d')*1000 # Convert ROOT-array to numpy-array and set in mV
        plot_channel = [] # Points which are to be plotted

        # Exclude channels which appears to have a pulse, for now
        
        # abs(V) = 0.03 is set by me from reading off the graphs, can be improved when pedestal
        # and noise are extracted in a better way
        # if all(abs(chan_np) < 0.03): # Fix this to investigate the noise before the pulse, not delete the whole channel
     
        # Consider all points before the pulse, i.e below 30 mV. When reaching the pulse, skip resting information
        
        for point in chan_np:
            if abs(point) < 20:
                data[channelCounter] = np.append(data[channelCounter],point)
                plot_channel = np.append(plot_channel,point)
            else:
                break

        # Plot the noises
        
        # create a graph for this channel and set its colors
        graphs_noise[channelCounter] = ROOT.TGraph(len(plot_channel)) #check length of len(plot_channel)


        # loop over the sample points and fill the TGraph to see the oscilloscope waveform
        
        for i in range(0,len(plot_channel)):
            graphs_noise[channelCounter].SetPoint(i, i*dt, plot_channel[i])
        
        # Two problems:
        # 1. When the first channel is only 500 positions long, the graph won't extend to 100 ns on x-axis
        # 2. When the signal is detected in code, it for some reason draws back to the zero point.
        
        # Set TDraw options
        graphs_noise[channelCounter].SetLineColor(channelCounter+1)
        graphs_noise[channelCounter].SetMarkerColor(channelCounter+1)
        graphs_noise[channelCounter].GetYaxis().SetRangeUser(-300, 50)
        graphs_noise[channelCounter].GetXaxis().SetRangeUser(0, 120)
        graphs_noise[channelCounter].GetYaxis().SetTitle("Voltage (mV)")
        graphs_noise[channelCounter].GetXaxis().SetTitle("Time (ns)")
        graphs_noise[channelCounter].SetTitle(setTitleAboveGraph) # Title above graph
        
        # Create TMultiGraph to draw multiple graphs
        graphs_noise_multi.Add(graphs_noise[channelCounter])
        
        channelCounter += 1
    
#    graphs_noise_multi.Draw("AP")
#    c1.Update()
#    c1.Print("plot_noise/Noise_entry%d.pdf" % e)

# maybe remove some points before the pulse?

# are there channels which give two pulses?

# Test the first commit

# are there differences between the pulses 
channelCounter = 0
bins = 100 # Convention to see a better resolution
c2 = ROOT.TCanvas("Histograms", "Histograms") # Dictionary for drawing

for chan in data:
    if len(chan) != 0 :
        
        # Defining structure of histogram
        min1 = min(chan)*0.9
        max1 = max(chan)*1.1
        graphs_histogram[channelCounter] = ROOT.TH1D("Histograms","Histograms",bins,min1,max1)
        graphs_histogram[channelCounter].SetLineColor(1)
        graphs_histogram[channelCounter].SetMarkerColor(1)
        graphs_histogram[channelCounter].GetYaxis().SetTitle("Amount in each bin (N)")
        graphs_histogram[channelCounter].GetXaxis().SetTitle("Voltage (mV)")
        setTitleAboveGraph = "Histogram with fitted distribution, Channel "+ str(channelCounter)
        graphs_histogram[channelCounter].SetTitle(setTitleAboveGraph) # Title above graph
        
        # Sorting the channel-list to use the distribution function
        chan.sort()
        for i in chan:
            graphs_histogram[channelCounter].Fill(i)
    
        # Draw and fit a Gauss distribution function with <x> and sigma
        graphs_histogram[channelCounter].Draw()
        graphs_histogram[channelCounter].Fit("gaus") # Here one could take out standard deviation sigma
        
        # Export plot as .pdf
        file_name = "channels_histograms/histograms_channel_"+str(channelCounter) + ".pdf"
        c2.Update()
        c2.Print(file_name)

    channelCounter += 1
    
