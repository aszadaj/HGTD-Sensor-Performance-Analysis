#   HGTD TEST BEAM SEPTEMBER 2017 SENSOR PERFOMANCE ANALYSIS (v.1.0.0)
#   (c) Antek Szadaj (antek@kth.se)
#   KTH Royal Institute of Technology, Stockholm
#
#   SHORT INFO:
#   Software for analyzing sensor perfomance for data taken during HGTD test beam
#   measurement September 2017 in North Area at CERN.
#
#   The software reconstructs the data and analyzes:
#
# - Pulse characteristics: noise, pedestal, pulse amplitude, charge/gain, rise time,
#   and additional methods to determine threshold levels.
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
# - Generally one can choose which functions to run from the pulse, timing resolution,
#   tracking and results sections.



##########################################################################
#                                                                        #
#                                                                        #
#         HGTD TEST BEAM SEPTEMBER 2017 SENSOR PERFOMANCE ANALYSIS       #
#                                                                        #
#                                                                        #
##########################################################################


import pulse_main as pulse
import pulse_plot
import timing_calculations as timing
import timing_plot
import tracking_plot as tracking
import results_calculations as results
import run_log_metadata as md
import data_management as dm


def main():
    
    # Choose batches to run, "all" or e.g. [101, 102].
    batches = [101]
    batches_exclude = []
    
    # Choose which sensor to produce plots for, e.g. "W9-LGA35"
    sensor = ""
    
    # Define settings and create folder, if needed.
    md.defineSettings(batches, batches_exclude, sensor)
    
    
    ########### PULSE ################
    

    pulse.pulseAnalysis()   # Takes ~8 min for each run file.
    pulse_plot.pulsePlots()

    
    ####### TIMING RESOLUTION ########
    

    timing_plot.timingPlots()

    
    ######### TRACKING ###############
    
    
    tracking.trackingPlots() # Considers batches with > 4 runs.
    

    ########### RESULTS ##############
    
    
    results.produceResults()


    dm.printTime()


main()
exit()
