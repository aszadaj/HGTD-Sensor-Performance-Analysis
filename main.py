#   HGTD TEST BEAM SEPTEMBER 2017 SENSOR PERFOMANCE ANALYSIS (v.1.0.0)
#   (c) Antek Szadaj (antek@kth.se) 2018
#   KTH Royal Institute of Technology, Stockholm
#
#   SHORT INFO:
#   Software for analyzing sensor perfomance for data taken during HGTD Test Beam
#   measurement September 2017 in North Area at CERN.
#
#   The software reconstructs the data and analyzes:
#
# - Pulse characteristics: noise, pedestal, pulse amplitude, charge/gain, rise time,
#   and additional methods to determine other signal characteristics.
#
# - Timing resolution: using two different types of time locations and cfd0.5, i.e. 50%
#   of the rising edge, (cfd0.5, recommended method) for two different types of methods.
#   One uses linear time difference between DUTs and SiPM and the other solves a system
#   of equations between a combination of time differences between sensors within the
#   same oscilloscope (only the first one).
#
# - Tracking: determines the position dependent signal for the pulse characteristics
#   and time resolution (not the system of equations method).
#
# - Results: takes the fitted values with its errors from earlier produced plots, and
#   plots them for different types among different temperatures and bias voltages.
#   Also gain dependence is included.
#
#
#
#   HOW TO START:
#
#   * Update the run log accordingly to the current test beam campaign. The run log is at
#
#       supplements/run_list_tb_sep_2017.csv
#
#   * Run the code without any functions ($ python2 main.py), to create the main folder.
#
#   * Place the oscilloscope files in
#
#      ../folder_sensor_perfomance_tb_sep17/oscilloscope_data_hgtd_tb_sep17/
#
#   * Place the tracking files in
#
#      ../folder_sensor_perfomance_tb_sep17/data_hgtd_tb_sep17/tracking/tracking/
#
#   * Select batch
#
#       batches = [102]
#
#   * Choose sensor
#
#       sensor = "W9-LGA35"
#
#   * Choose which function to run by changing from 0 to 1.
#
#   * Run the code in the console
#
#       $ python2 main.py
#


##########################################################################
#                                                                        #
#                                                                        #
#         HGTD TEST BEAM SEPTEMBER 2017 SENSOR PERFOMANCE ANALYSIS       #
#                                                                        #
#                                                                        #
##########################################################################


import run_log_metadata as md


def main():
    
    # Choose batches to run, by [101] or multiple [203, 304] or all batches with "all"
    batches = [306]
    batches_exclude = []
    
    # Choose which sensor to produce plots for, e.g. "W9-LGA35", or all with ""
    sensor = "W9-LGA35"
    
    # Choose which function to run (0 or 1)
    pulseAnalysis   = 0
    pulsePlots      = 0
    timingPlots     = 0
    trackingPlots   = 1
    produceResults  = 0
    
    
    functions = [pulseAnalysis, pulsePlots, timingPlots, trackingPlots, produceResults]
    
    md.runAnalysis(batches, batches_exclude, sensor, functions)


main()
exit()
