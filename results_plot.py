import ROOT

import run_log_metadata as md
import data_management as dm
import results_calculations as r_calc


def addValuesToGraph(variables):
    
    [sensor_data, category, legend_graph, graph, category_graph] = [i for i in variables]
    
    for DUT_pos in r_calc.availableDUTPositions(r_calc.processed_sensor):
        
        if DUT_pos in ["3_0", "3_1", "3_3", "8_1", "7_2", "7_3"]:
            continue
    
        
        for temperature in md.getAvailableTemperatures():

            sensor_data[temperature][DUT_pos].sort()
            
            i = 0
            for data in sensor_data[temperature][DUT_pos]:
                
                constant = 1
                if category == "charge":
                    constant = 1./(0.46) # Divide by MIP charge = Gain
            
                graph[r_calc.processed_sensor][temperature][DUT_pos].SetPoint(i, data[0], data[1][0] * constant)
                graph[r_calc.processed_sensor][temperature][DUT_pos].SetPointError(i, 0, data[1][1] * constant)
                
                i += 1
            
            if graph[r_calc.processed_sensor][temperature][DUT_pos].GetN() != 0:
                category_graph.Add(graph[r_calc.processed_sensor][temperature][DUT_pos])

                if r_calc.oneSensorInLegend:
                    legend_graph.AddEntry(graph[r_calc.processed_sensor][temperature][DUT_pos], r_calc.processed_sensor, "p")
                
                r_calc.oneSensorInLegend = False


def drawAndExportResults(category, category_graph, legend_graph, zoom):

    # The zoom option creates plots for the region \sigma < 100 ps and gain < 100. Also
    # put in a separate folder
    
    drawOpt = "AP"
    
    if category.find("gain") == -1:
        drawOpt += "L"
    
    
    category_graph.Draw(drawOpt)
    positions_latex = setGraphAttributes(category_graph, category, zoom)
    r_calc.canvas.Update()
    legend_graph.Draw()
    
    if category == "charge":
        charge_mip = 0.46
        xmin = 0
        xmax = r_calc.bias_voltage_max
        ymin = 0.01
        ymax = category_graph.GetHistogram().GetMaximum()
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
    legend_text.DrawLatex(positions_latex[0][0], positions_latex[0][1] , "Marker color")
    legend_text.DrawLatex(positions_latex[1][0], positions_latex[1][1], "#color[3]{Green}  = 22 \circC")
    legend_text.DrawLatex(positions_latex[2][0], positions_latex[2][1], "#color[4]{Blue}    = -30 \circC")
    legend_text.DrawLatex(positions_latex[3][0], positions_latex[3][1], "#color[6]{Purple} = -40 \circC")

    
    if category.find("gain") != -1:
        if zoom:
            fileName = dm.getSourceFolderPath() + dm.getResultsPlotSourceDataPath() + "/timing_vs_gain_zoom/" + category + "_results.pdf"
        else:
            fileName = dm.getSourceFolderPath() + dm.getResultsPlotSourceDataPath() + "/timing_vs_gain/" + category + "_results.pdf"
    else:
        fileName = dm.getSourceFolderPath() + dm.getResultsPlotSourceDataPath() +"/" + category + "_results.pdf"
    
    r_calc.canvas.Print(fileName)


def setGraphAttributes(category_graph, category, zoom):

    timing_res_max = 600
    
    # Define titles, head and axes
    if category == "noise":
        titleGraph = "Noise per bias voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Noise [mV]"
        y_lim = [0, 6]
    
    elif category == "pedestal":
        titleGraph = "Pedestal per bias voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Pedestal [mV]"
        y_lim = [-3, 3]

    elif category == "peak_value":
    
        titleGraph = "Pulse amplitude per bias voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Pulse amplitude [mV]"
        y_lim = [0, 300]

    elif category == "charge":
    
        titleGraph = "Gain/charge per bias voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Gain"
        y_lim = [0, 500]

    elif category == "rise_time":
        
        titleGraph = "Rise time per bias voltage"
        xTitle = "Bias voltage [V]"
        yTitle = "Rise time [ps]"
        y_lim = [0, 2000]

    elif category == "linear":
    
        titleGraph = "Timing resolution per bias voltage (peak)"
        xTitle = "Bias voltage [V]"
        yTitle = "Time resolution [ps]"


    elif category == "linear_cfd":
    
        titleGraph = "Timing resolution per bias voltage (CFD)"
        xTitle = "Bias voltage [V]"
        yTitle = "Time resolution [ps]"

    elif category == "system":
    
        titleGraph = "Timing resolution per bias voltage (sys of eqs, peak)"
        xTitle = "Bias voltage [V]"
        yTitle = "Time resolution [ps]"

    elif category == "system_cfd":
    
        titleGraph = "Timing resolution per bias voltage (sys of eqs, CFD)"
        xTitle = "Bias voltage [V]"
        yTitle = "Time resolution [ps]"
    
    
    
    if category == "linear_gain":
        
        titleGraph = "Timing resolution per gain (peak)"
        xTitle = "Gain"
        yTitle = "Time resolution [ps]"
    
    
    elif category == "linear_cfd_gain":
    
        titleGraph = "Timing resolution per gain (cfd)"
        xTitle = "Gain"
        yTitle = "Time resolution [ps]"

    elif category == "system_gain":
    
        titleGraph = "Timing resolution per gain (system, peak)"
        xTitle = "Gain"
        yTitle = "Time resolution [ps]"

    elif category == "system_cfd_gain":
   
        titleGraph = "Timing resolution per gain (system, cfd)"
        xTitle = "Gain"
        yTitle = "Time resolution [ps]"
        

    if category.find("gain") != -1:
        r_calc.bias_voltage_max = 500
    
        if zoom:
            timing_res_max = 100
            r_calc.bias_voltage_max = 100


    if category.find("linear") != -1 or category.find("system") != -1:
        #positions_latex = [[.5, .76], [.5, .71], [.5, .66], [.5, .61]]
        positions_latex = [[.7, .55], [.7, .5], [.7, .45], [.7, .4]]
        y_lim = [0, timing_res_max]

    elif category.find("noise") != -1:
        r_calc.bias_voltage_max = 500
        positions_latex = [[.7, .55], [.7, .5], [.7, .45], [.7, .4]]

    elif category.find("peak_value") != -1:
        positions_latex = [[.5, .76], [.5, .71], [.5, .66], [.5, .61]]


    else:
        positions_latex = [[.7, .55], [.7, .5], [.7, .45], [.7, .4]]



    category_graph.SetTitle(titleGraph)
    category_graph.GetXaxis().SetTitle(xTitle)
    category_graph.GetYaxis().SetTitle(yTitle)

    category_graph.GetXaxis().SetLimits(0, r_calc.bias_voltage_max)
    category_graph.SetMinimum(y_lim[0])
    category_graph.SetMaximum(y_lim[1])

    r_calc.bias_voltage_max = 350

    return positions_latex


def setMarkerType(graph, pos, temperature):

    sensor = r_calc.processed_sensor
    
    size = 1
    
    # Red 22 deg C
    if temperature == "22":
        color = 3
    
    # Blue -30 deg C
    elif temperature == "-30":
        color = 4

    # Purple -40 deg C
    else:
        color = 6


    if sensor == "50D-GBGR2":
        marker = 24

    elif sensor == "W4-LG12":
        marker = 27

    elif sensor == "W4-RD01":
        marker = 46

    elif sensor == "W4-S203":
        marker = 25

    elif sensor == "W4-S215":
        marker = 26

    elif sensor == "W4-S1022":
        marker = 28

    elif sensor == "W4-S1061":
        marker = 30

    elif sensor == "W9-LGA35":
        marker = 32

    # the omitted sensor
    elif sensor == "W4-S204_6e14":
        marker = 20



    graph.SetMarkerColor(color)
    graph.SetMarkerStyle(marker)
    graph.SetMarkerSize(size)

