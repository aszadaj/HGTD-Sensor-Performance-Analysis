# HGTD TEST BEAM SEPTEMBER 2017 SENSOR PERFOMANCE ANALYSIS, (c) Antek Szadaj, KTH Royal Institute of Technology (2018).
#
# Software specifically created for analyzing sensor perfomance of data created during test beam measurement done at North Area in CERN in September 2017. This includes
# - pulse characteristics: noise, pedestal, pulse amplitude, charge/gain, rise time, and additional methods to determine threshold levels
#
# - timing resolution, using two different types of time locations and cfd0.5, i.e. 50% of the rising edge, (cfd0.5, recommended method) for two different types of methods. One uses linear time difference between DUTs and SiPM and the other solves a system of equations between a combination of time differences between sensors within the same oscilloscope (only the first one).
# - tracking which determines the position dependent signal for the pulse characteristics and time resolution (not the system of equations method).
# - results which takes the fitted values with its errors from earlier produced plots, and plots them for different types among different temperatures and bias voltages.
#
# - Generally one can choose which functions to run from the pulse, timing resolution, tracking and results sections.



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

    # Limit number of runs within a batch or consider "all" (works for pulse analysis).
    number_of_runs = "all"
    
    # Choose batches to run. "all" or e.g. [101, 102].
    batches = [102]
    batches_exclude = []
    
    # Choose sensor for which the plots are produced.
    sensor = ""
    
    md.defineSettings(batches, batches_exclude, number_of_runs, sensor)
    
    
    
    ########### PULSE ################
    

    pulse.pulseAnalysis() # Long procedure function ~5 min per run.
    pulse_plot.pulsePlots()

    
    
    ####### TIMING RESOLUTION ########
    
    
    timing.createTimingFiles() # Creates files for timingPlots() and trackingAnalysis()
    timing_plot.timingPlots()

    
    
    ######### TRACKING ###############
    
    
    tracking.trackingAnalysis() # Considers batches with > 4 runs.
    
    

    ########### RESULTS ##############
    
    
    results.produceResults()


    dm.printTime()


main()
exit()
