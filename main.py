# HGTD SEP 2017 SENSOR PERFOMANCE ANALYSIS, Antek Szadaj, KTH Royal Institute och Technology (2018)
#
# Software specifically created for analyzing sensor perfomance of data created during test beam measurement done at North Area in CERN in September 2017. This includes
# - pulse characteristics: noise, pedestal, pulse amplitude, charge/gain, rise time, and additional methods to determine
# threhsold levels
# - timing resolution, using two different types of time locations (at the peak of the pulse, which turns out to be useless, but whatever :) and cfd0.5, i.e. 50% of the rising edge, (recommended method)) for two different types of methods. One uses linear time difference between DUTs and SiPM and the other solves a system of equations between a combination of time differences between sensors within the same oscilloscope (only the first!)
# - tracking which determines the position dependent signal for the pulse characteristics and time resolution (not the system of equations method).
# - results which takes the fitted values with its errors and plots them for different types among different temperatures and bias voltages



##########################################################################
#                                                                        #
#                                                                        #
#         HGTD TEST BEAM SEPTEMBER 2017 SENSOR PERFOMANCE ANALYSIS       #
#                                                                        #
#                                                                        #
##########################################################################

import pulse_main
import pulse_plot
import tracking_main as tracking
import timing_main as timing
import timing_plot
import results_main as results

import run_log_metadata as md
import data_management as dm
import time


def main():

    # Select how many runs, which batches and which sensors to be run
    number_of_runs = 0
    
    # batches must be list, or "all". Exclusion of batches also possible
    batches = "all"
    batches_exclude = []
    
    # The sensor which is supposed to be analyzed, "" == all sensors
    # Works only for the functions which produces plots!
    sensor = ""
    
    md.setLimitRunNumbers(number_of_runs)
    md.setBatchNumbers(batches, batches_exclude)
    md.setSensor(sensor)
    dm.printTime()

    ############## METHODS ###############
    
    
    ########### PULSE ################

    #pulse_main.pulseAnalysis() # This is a long procedure function
    #pulse_plot.pulsePlots()
    
    ##################################

    
    ####### TIMING RESOLUTION ########
    
    #timing.timingAnalysis()
    #timing_plot.timingPlots()
    
    ##################################

    
    ######### TRACKING  ##############
    
    tracking.trackingAnalysis() # requires works only for batches with > 4 runs.
    
    ##################################


    ########### RESULTS ##############
    
    #results.produceResults()

   
    ######################################
   
    dm.printTime()
    exit()


main()


