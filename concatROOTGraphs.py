import ROOT
import numpy as np
import root_numpy as rnm

import metadata as md
import data_management as dm
import pulse_calculations as p_calc

ROOT.gROOT.SetBatch(True)
ROOT.gStyle.SetPalette(1)
ROOT.gStyle.SetNumberContours(100)


# Start analysis of selected run numbers
def concatenateROOTFiles():

    canvas = ROOT.TCanvas("Test", "Test")

    fileDirectory1 = "/Users/aszadaj/cernbox/SH203X/HGTD_material/plots_data_hgtd_efficiency_sep_2017/W4-S215/tracking/mean_value/tracking_mean_value_101_chan4_W4-S215.root"
    
    fileDirectory2 = "/Users/aszadaj/cernbox/SH203X/HGTD_material/plots_data_hgtd_efficiency_sep_2017/W4-S215/tracking/mean_value/tracking_mean_value_101_chan5_W4-S215.root"
    
    fileDirectory3 = "/Users/aszadaj/cernbox/SH203X/HGTD_material/plots_data_hgtd_efficiency_sep_2017/W4-S215/tracking/mean_value/tracking_mean_value_101_chan6_W4-S215.root"
    
    fileDirectory4 = "/Users/aszadaj/cernbox/SH203X/HGTD_material/plots_data_hgtd_efficiency_sep_2017/W4-S215/tracking/mean_value/tracking_mean_value_101_chan7_W4-S215.root"

    rootTFileObject1 = ROOT.TFile.Open(fileDirectory1)
    rootTFileObject2 = ROOT.TFile.Open(fileDirectory2)
    rootTFileObject3 = ROOT.TFile.Open(fileDirectory3)
    rootTFileObject4 = ROOT.TFile.Open(fileDirectory4)
    
    histObject1 = rootTFileObject1.Get("Mean value chan4")
    histObject2 = rootTFileObject2.Get("Mean value chan5")
    histObject3 = rootTFileObject3.Get("Mean value chan6")
    histObject4 = rootTFileObject4.Get("Mean value chan7")
    
    x = [histObject1.GetMean(1), histObject2.GetMean(1), histObject3.GetMean(1), histObject4.GetMean(1)]
    
    y = [histObject1.GetMean(2), histObject2.GetMean(2), histObject3.GetMean(2), histObject4.GetMean(2)]
    
    xmin = min(x)-1
    ymin = min(y)-0.7
    xmax = max(x)+1
    ymax = max(y)+0.7
    
    canvas.DrawFrame(xmin, ymin, xmax, ymax )

    histObject1.Draw("SAME COLZ")
    histObject2.Draw("SAME COL")
    histObject3.Draw("SAME COL")
    histObject4.Draw("SAME COL")
    
#    histObject1.SetAxisRange(xmin, xmax, "X")
#    histObject1.SetAxisRange(ymin, ymax, "Y")

    canvas.Update()
    
    canvas.Print("test.pdf")


    


concatenateROOTFiles()

