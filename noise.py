import ROOT
import numpy as np

# Create TFile object from .root-file
# NB! Use the correct file-path
#f = ROOT.TFile("/eos/user/k/kastanas/TB/osci_conv/data_1504818689.tree.root")
f = ROOT.TFile("~/data_1504818689.tree.root")

# get the TTree from the TFile
t  = f.Get("oscilloscope")

# Sampling period of the scope
dt = 0.1

# Nested tuple, three dimensional
data = []

c1 = ROOT.TCanvas("Noises", "Noises")
graphs_noise = {}

# loop over entries
for e in range(1,t.GetEntries()): # Select specifically entries 6 and 7 for debugging reasons, normally until #t.GetEntries()
    
    data.append([])
    t.GetEntry(e-1)
    setTitleAboveGraph = "Noise - Entry "+ str(e) # To be used later
    channelNo = 0
    graphs_noise_multi = ROOT.TMultiGraph()
    
    # Loop over all channels
    for chan in [t.chan0, t.chan1, t.chan2, t.chan3, t.chan4, t.chan5, t.chan6, t.chan7]:
        
        # Convert ROOT-array to numpy-array and set in mV
        chan_np = np.asarray(chan,'d')*1000
        
        # Points which are to be plotted
        noise_data_points = []
        
        # Put all points until the pulse, that is below 25 mV.
        for point in chan_np:
            if abs(point) < 25:
                noise_data_points = np.append(noise_data_points,point)
            else:
                noise_data_points = noise_data_points[:-3]
                data[e-1].append(noise_data_points)
                break
    
        # Plot the noises #
        
        # create a graph for this channel and set its colors
        graphs_noise[channelNo] = ROOT.TGraph(len(noise_data_points))

        # loop over the sample points and fill the TGraph to see the oscilloscope waveform
        for i in range(0,len(noise_data_points)):
            graphs_noise[channelNo].SetPoint(i, i*dt, noise_data_points[i])
        
        # Set TDraw options
        graphs_noise[channelNo].SetLineColor(channelNo+1)
        graphs_noise[channelNo].SetMarkerColor(channelNo+1)
       
        # Create TMultiGraph to draw multiple graphs
        graphs_noise_multi.Add(graphs_noise[channelNo])
        
        channelNo += 1

#### PRINT FILE ####
#    graphs_noise_multi.Draw("ALP")
#
#    graphs_noise_multi.GetYaxis().SetRangeUser(-300, 50)
#    graphs_noise_multi.GetXaxis().SetRangeUser(0, 120)
#    graphs_noise_multi.SetTitle(setTitleAboveGraph)
#    graphs_noise_multi.GetYaxis().SetTitle("Voltage (mV)")
#    graphs_noise_multi.GetXaxis().SetTitle("Time (ns)")
#
#    c1.Update()
#    c1.Print("plot_noise/Noise_entry%d.pdf" % e)
######################

# maybe remove some points before the pulse?
# are there channels which give two pulses?
# are there differences between the pulses

pedestal = []
stddevs = []

bins = 100 # Convention to see a better resolution
c2 = ROOT.TCanvas("Histograms", "Histograms") # Dictionary for drawing
entry = 1

for e in data:
    channelNo = 1
    for chan in e:
        if len(chan)!=0:
            # Defining structure of histogram
            min1 = min(chan)*0.9
            max1 = max(chan)*1.1
            histogram = ROOT.TH1D("Histograms","Histograms",bins,min1,max1)
            histogram.SetLineColor(1)
            histogram.SetMarkerColor(1)
            histogram.GetYaxis().SetTitle("Amount in each bin (N)")
            histogram.GetXaxis().SetTitle("Voltage (mV)")
            setTitleAboveGraph = "Histogram with fitted distribution, Entry " + str(entry) +  ", Channel "+ str(channelNo)
            histogram.SetTitle(setTitleAboveGraph) # Title above graph
            
            # Sorting the channel-list to use the distribution function
            chan.sort()
            for i in chan:
                histogram.Fill(i)
        
            # Draw and fit a Gauss distribution function with <x> and sigma
            histogram.Draw()
            histogram.Fit("gaus") # Here one could take out standard deviation sigma
            pedestal.append(histogram.GetMean())
            stddevs.append(histogram.GetStdDev())
            #### PRINT FILE ####
            
#            # Export plot as .pdf
#            file_name = "histograms/entry"+str(entry)+"/histogram_entry"+str(entry)+"_channel"+str(channelNo)+".pdf"
#            c2.Update()
#            c2.Print(file_name)
            ######

        channelNo += 1
    entry += 1


bins = 100 # Convention to see a better resolution
c3 = ROOT.TCanvas("Distributions", "Distributions") # Dictionary for drawing
entry = 1

# Defining structure of histogram
min1 = min(pedestal)*0.9
max1 = max(pedestal)*1.1
histogram = ROOT.TH1D("Pedestal","Pedestal",bins,min1,max1)
histogram.SetLineColor(1)
histogram.SetMarkerColor(1)
histogram.GetYaxis().SetTitle("Amount in each bin (N)")
histogram.GetXaxis().SetTitle("Pedestal (mV)")
setTitleAboveGraph = "Pedestal distribution for all entries"
histogram.SetTitle(setTitleAboveGraph)

pedestal.sort()
for i in pedestal:
    histogram.Fill(i)

# Draw and fit a Gauss distribution function with <x> and sigma
histogram.Draw()
histogram.Fit("gaus") # Here one could take out standard deviation sigma
pedestal_total = histogram.GetMean()

print "\nThe pedestal value is " + str(pedestal_total) + " mV.\n"

# Export plot as .pdf
file_name = "distribution_pedestal.pdf"
c3.Update()
c3.Print(file_name)

entry += 1


    
