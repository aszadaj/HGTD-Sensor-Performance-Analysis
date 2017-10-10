import ROOT
import numpy as np

#### OSCILLOSCOPE ANALYSIS ####
#
# Without plotting graphs
#
###############################

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

# loop over entries
for e in range(1,500): #t.GetEntries()
    
    data.append([])
    t.GetEntry(e-1)
    
    # Loop over all channels
    for chan in [t.chan0, t.chan1, t.chan2, t.chan3, t.chan4, t.chan5, t.chan6, t.chan7]:
        
        # Convert ROOT-array to numpy-array and set in mV
        chan_np = np.asarray(chan,'d')*1000
        
        # Selected points which fulfill condition
        points_condition = []
        
        # Put all points until the pulse, that is below 25 mV.
        for point in chan_np:
            if abs(point) < 25:
                points_condition = np.append(points_condition,point)
            else:
                data[e-1].append(points_condition[:-3])
                break

# maybe remove some points before the pulse?
# are there channels which give two pulses?
# are there differences between the pulses

pedestal = []
stddevs = []

bins = 100 # Convention to see a better resolution
c2 = ROOT.TCanvas("Histograms", "Histograms") # Dictionary for drawing
entry = 1
histogram = ""
for e in data:
    for chan in e:
        if len(chan)!=0:
            # Defining structure of histogram
            min1 = min(chan)*0.9
            max1 = max(chan)*1.1
            histogram = ROOT.TH1D("Histograms","Histograms",bins,min1,max1)
            
            # Sorting the channel-list to use the distribution function
            chan.sort()
            for i in chan:
                histogram.Fill(i)
        
            # Draw and fit a Gauss distribution function with <x> and sigma
            histogram.Draw()
            pedestal.append(histogram.GetMean())
            stddevs.append(histogram.GetStdDev())

    entry += 1


bins = 100 # Convention to see a better resolution
c = ROOT.TCanvas("Distributions", "Distributions") # Dictionary for drawing

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

# Sorting and fill the histogram
pedestal.sort()
for i in pedestal:
    histogram.Fill(i)

# Draw and fit a Gauss distribution function with <x> and sigma
histogram.Draw()
histogram.Fit("gaus")
pedestal_total = histogram.GetMean()
std_pedestal = histogram.GetStdDev()

print "\nThe pedestal value is " + str(pedestal_total) + " mV.\n"

print "\nThe STD value is " + str(std_pedestal) + " mV.\n"

# Export plot as .pdf
file_name = "distribution_pedestal.pdf"
c.Update()
c.Print(file_name)



    
