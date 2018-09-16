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
import tracking_main as tracking
import timing_main as timing
import timing_plot
import results_main as results

import run_log_metadata
import data_management
import time


def main():

    # Select how many runs, which batches and which sensors to be run
    number_of_runs = 0
    
    # batches must be list, or "all". Exclusion of batches also possible
    batches = "all"
    batches_exclude = []
    
    # consider the group of batches (example 10X or 70X)
    first_number = False
    
    # The sensor which is supposed to be analyzed, "" == all sensors
    sensor = ""
    

    run_log_metadata.setLimitRunNumbers(number_of_runs)
    run_log_metadata.setBatchNumbers(batches, first_number, batches_exclude)
    run_log_metadata.setSensor(sensor)
    data_management.printTime()

    ############## METHODS ###############
    
    
    ############# NOISE ##############
    
    #noise_main.noiseAnalysis()
    #noise_plot.noisePlots()
    
    ##################################

    
    ########### PULSE ################

    #pulse_main.pulseAnalysis()
    #pulse_plot.pulsePlots()
    
    ##################################

    
    ####### TIMING RESOLUTION ########
    
    #timing.timingAnalysis()
    #timing_plot.timingPlots()
    
    ##################################

    
    ######### TRACKING  ##############
    
    #tracking.trackingAnalysis()
    
    ##################################


    ########### RESULTS ##############
    
    #results.produceResults()

   
    ######################################
   
    data_management.printTime()
    exit()




main()


