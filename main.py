#############################################################
#                                                           #
#                                                           #
#         HGTD SEP 2017 SENSOR PERFOMANCE ANALYSIS          #
#                                                           #
#                                                           #
#############################################################

import noise_main
import noise_plot
import pulse_main
import pulse_plot
import tracking_main
import timing_main
import timing_plot
import results_main

import run_log_metadata
import data_management


def main():

    # Select how many runs, which batches and which sensors to be run, var batches must be a list
    number_of_runs = 0
    
    # batches must be list, of "all". One can add another
    batches = [102]
    batches_exclude = []
    
    # consider the group of batches (example 10X or 70X)
    first_number = False
    
    # The senso which is supposed to be analyzed, "" == all sensors
    sensor = "W9-LGA35"
    
    data_management.printTime()


    run_log_metadata.setLimitRunNumbers(number_of_runs)
    run_log_metadata.setBatchNumbers(batches, first_number, batches_exclude)
    run_log_metadata.setSensor(sensor)

    ############## METHODS ###############
    
    
    ######## NOISE ##########
    
    #noise_main.noiseAnalysis()
    
    #########################

    
    ######## PULSE ##########
    
    #pulse_main.pulseAnalysis()
    
    #########################

    
    ### TIMING RESOLUTION ###
    
    #timing_main.timingAnalysis()
    
    #########################
    
    
    
    ###### TRACKING #########
    
    tracking_main.trackingAnalysis()
    
    #########################
    
    
    ### PLOTS ###
    
    #noise_plot.noisePlots()
    #pulse_plot.pulsePlots()
    #timing_plot.timingPlots()

    ### RESULTS ###
    
    #results_main.produceResults()

   
    #######################################
   
    data_management.printTime()
    exit()




main()


