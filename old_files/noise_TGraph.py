import ROOT
import numpy as np

# Create TFile object from .root-file
# NB! Use the correct file-path
#f = ROOT.TFile("/eos/user/k/kastanas/TB/osci_conv/data_1504818689.tree.root")
f = ROOT.TFile("~/data_1504818689.tree.root")

# Get TTree from TFile
t  = f.Get("oscilloscope")

# Create canvas to draw on
c = ROOT.TCanvas("Noise", "Noise") # this is what we draw on

# Sampling period of the scope
dt = 0.1

# Nested tuple, three dimensional
data = [[[] for _ in range(8)] for _ in range(t.GetEntries())]

# Loop over entries
for e in range(6, 8): # Select specifically entries 6 and 7 for debugging reasons, normally until #t.GetEntries()
    
    t.GetEntry(e)
    
    # Loop over the channels and draw them
    channelCounter = 0
    graphs = {}
    
    for chan in [t.chan0, t.chan1, t.chan2, t.chan3, t.chan4, t.chan5, t.chan6, t.chan7]:
        
        # Convert ROOT-array to numpy-array and set in mV
        chan_np = np.asarray(chan,'d')*1000
        
        noise_data_points = []
        
        # Put all points until the pulse, that is below 25 mV.
        for point in chan_np:
            if abs(point) < 25:
                noise_data_points = np.append(noise_data_points,point)
            else:
                noise_data_points = noise_data_points[:-3]
                break
    
        # Use those points for future analysis
        data[e][channelCounter] = noise_data_points
        
        # Create a graph for this channel and set its colors
        graphs[channelCounter] = ROOT.TGraph(1002)
        graphs[channelCounter].SetLineColor(channelCounter+1)
        graphs[channelCounter].SetMarkerColor(channelCounter+1)
       
        # Loop over the sample points and fill the TGraph to see the oscilloscope waveform
        for i in range(0,len(noise_data_points)):
            graphs[channelCounter].SetPoint(i, i*dt, noise_data_points[i])
        
        # Draw the graph with additional information
        drawOpt = "LP" # draw with Line and Points
        if channelCounter == 0:
            drawOpt += "A" # also draw Axes if first to be drawn

        # Set limits and labels on x and y-axis
        graphs[channelCounter].GetXaxis().SetRangeUser(0, 120)
        graphs[channelCounter].GetYaxis().SetRangeUser(-300, 50)
        graphs[channelCounter].GetYaxis().SetTitle("Voltage (mV)")
        graphs[channelCounter].GetXaxis().SetTitle("Time (ns)")
        graphs[channelCounter].Draw(drawOpt)
        graphs[channelCounter].GetXaxis().SetRangeUser(0, 120)
        graphs[channelCounter].GetYaxis().SetRangeUser(-300, 50)
        
        channelCounter += 1
    
    # Export as PDF
    c.Update()
    c.Print("noise/noise_entry%d.pdf" % e)

