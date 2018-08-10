#####################################################
#                                                   #
#                                                   #
#         HGTD SENSOR PERFOMANCE ANALYSIS           #
#                                                   #
#                                                   #
#####################################################

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

    # Select how many runs, which batches and which sensors to be run
    number_of_runs = 0
    batches = 401
    sensor = ""
    
    data_management.printTime()


    run_log_metadata.setLimitRunNumbers(number_of_runs)
    run_log_metadata.setBatchNumbers(batches)
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
    
    #tracking_main.trackingAnalysis()
    
    #########################
    
    
    ### PLOTS ###
    
    #noise_plot.noisePlots()
    #pulse_plot.pulsePlots()
    #timing_plot.timingPlots()

    ### RESULTS ###
    
    results_main.produceResults()

   
    #######################################
   
    data_management.printTime()
    exit()




main()


