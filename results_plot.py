import ROOT

import run_log_metadata as md
import data_management as dm
import results_main as rm


def addValuesToGraph(variables):
    
    [sensor_data, category, legend_graph, graph, category_graph] = [i for i in variables]
    
    for DUT_pos in md.availableDUTPositions(rm.processed_sensor):

        if DUT_pos in ["3_0", "3_1", "3_3", "8_1", "7_2", "7_3"]:
            continue

        for temperature in md.availableTemperatures():

            sensor_data[temperature][DUT_pos].sort()
            
            i = 0
            for data in sensor_data[temperature][DUT_pos]:
                
                constant = 1
                if category == "charge":
                    constant = 1./(0.46) # Divide by MIP charge = Gain
            
                graph[rm.processed_sensor][temperature][DUT_pos].SetPoint(i, data[0], data[1][0] * constant)
                graph[rm.processed_sensor][temperature][DUT_pos].SetPointError(i, 0, data[1][1])
                
                i += 1
            
            if graph[rm.processed_sensor][temperature][DUT_pos].GetN() != 0:
                category_graph.Add(graph[rm.processed_sensor][temperature][DUT_pos])

                if rm.oneSensorInLegend:
                    legend_graph.AddEntry(graph[rm.processed_sensor][temperature][DUT_pos], rm.processed_sensor, "p")
                
                rm.oneSensorInLegend = False



def drawAndExportResults(category, category_graph, legend_graph):

    category_graph.Draw("APL")
    setGraphAttributes(category_graph, category)
    rm.canvas.Update()
    legend_graph.Draw()
    
    if category == "charge":
        charge_mip = 0.46
        xmin = 0
        xmax = rm.bias_voltage_max
        ymin = 0.01
        ymax = category_graph.GetXaxis().GetXmax()
        new_axis = ROOT.TGaxis(xmax,ymin,xmax,ymax,ymin,int(ymax*charge_mip),510,"+L")
        new_axis.SetTitle("Charge [fC]")
        new_axis.SetLabelFont(42)
        new_axis.SetTitleFont(42)
        new_axis.SetLabelSize(0.035)
        new_axis.SetTitleSize(0.035)
        new_axis.Draw()
    
    # Draw extra legend with information about the coloring
    legend_text = ROOT.TLatex()
    legend_text.SetTextSize(0.035)
    legend_text.SetNDC(True)
    legend_text.DrawLatex(.7, .55, "Marker color")
    legend_text.DrawLatex(.7, .5, "#color[2]{Red}    = 22\circC")
    legend_text.DrawLatex(.7, .45, "#color[4]{Blue}   = -30\circC")
    legend_text.DrawLatex(.7, .4, "#color[3]{Green} = -40\circC")
    

    
    fileName = dm.getSourceFolderPath() + "results_hgtd_efficiency_sep_2017/" + "/" + category + "_results.pdf"
    rm.canvas.Print(fileName)


def setGraphAttributes(category_graph, category):

    # Define titles, head and axes
    if category == "noise":
        titleGraph = "Noise values per bias voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Noise [mV]"
        y_lim = [0, 10]
    
    elif category == "pedestal":
        titleGraph = "Pedestal values per bias voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Pedestal [mV]"
        y_lim = [-10, 10]

    elif category == "peak_value":
    
        titleGraph = "Pulse amplitude values per voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Pulse amplitude [mV]"
        y_lim = [0, 300]

    elif category == "charge":
    
        titleGraph = "Gain and charge values per voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Gain"
        y_lim = [0, 500]

    elif category == "rise_time":
        
        titleGraph = "Rise time values per voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Rise time [ps]"
        y_lim = [0, 1000]

    elif category == "timing_normal_peak":
    
        titleGraph = "Time resolution values per voltage (peak)"
        xTitle = "Bias voltage [V]"
        yTitle = "Time resolution [ps]"
        y_lim = [0, 300]


    elif category == "timing_normal_cfd05":
    
        titleGraph = "Time resolution values per voltage (cfd05)"
        xTitle = "Bias voltage [V]"
        yTitle = "Time resolution [ps]"
        y_lim = [0, 300]

    elif category == "timing_system_peak":
    
        titleGraph = "Time resolution values per voltage (system, peak)"
        xTitle = "Bias voltage [V]"
        yTitle = "Time resolution [ps]"
        y_lim = [0, 300]

    elif category == "timing_system_cfd05":
    
        titleGraph = "Time resolution values per voltage (system, cfd05)"
        xTitle = "Bias voltage [V]"
        yTitle = "Time resolution [ps]"
        y_lim = [0, 300]


    category_graph.SetTitle(titleGraph)
    category_graph.GetXaxis().SetTitle(xTitle)
    category_graph.GetYaxis().SetTitle(yTitle)

    category_graph.GetXaxis().SetLimits(0, rm.bias_voltage_max)
    category_graph.SetMinimum(y_lim[0])
    category_graph.SetMaximum(y_lim[1])


def setMarkerType(graph, pos, temperature):

    sensor = rm.processed_sensor
    
    size = 1
    
    # Red 22 deg C
    if temperature == "22":
        color = 2
    
    # Blue -30 deg C
    elif temperature == "-30":
        color = 4

    # Green -40 deg C
    else:
        color = 8

    if sensor == "W9-LGA35":
        marker = 20

    elif sensor == "W4-S203":
        marker = 21

    elif sensor == "W4-S215":
        marker = 22
        
        if pos == "3_0":
            size = 1.2
        
        elif pos == "3_1":
             size = 1.4
        
        elif pos == "3_2":
             size = 1.6

        elif pos == "3_3":
             size = 1.8

    elif sensor == "50D-GBGR2":
        marker = 23

    elif sensor == "W4-LG07":
        marker = 24

    elif sensor == "W4-LG12":
        marker = 25

    elif sensor == "W4-S1061":
        marker = 26

    elif sensor == "W4-S1022":
        marker = 27

    elif sensor == "W4-S204_6e14":
        marker = 28
        if pos == "7_0":
            size = 1.2
        
        elif pos == "7_2":
            size = 1.4
        
        elif pos == "7_3":
            size = 1.8


    elif sensor == "W4-RD01":
        marker = 29
        if pos == "7_0":
            size = 1.2
        
        elif pos == "7_2":
            size = 1.4


    graph.SetMarkerColor(color)
    graph.SetMarkerStyle(marker)
    graph.SetMarkerSize(size)

