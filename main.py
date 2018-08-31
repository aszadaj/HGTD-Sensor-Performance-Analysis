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
import time


def main():

#    count = 0
#    time_tot = 2*60
#    remaining = time_tot
#    bool = True
#    while bool:
#        print time_tot-count, "minutes left"
#        time.sleep(60)
#        count += 1
#        if count == time_tot:
#            bool = False
#    print "Start"

    # Select how many runs, which batches and which sensors to be run
    number_of_runs = 0
    
    # batches must be list, or "all". Exclusion of batches also possible
    batches = "all"
    batches_exclude = [101, 102, 103, 104, 105, 106, 107, 108, 201, 202, 203, 204, 205, 206, 207, 301, 302, 303, 304, 305]
    
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
    
    ##################################

    
    ########### PULSE ################

    pulse_main.pulseAnalysis()
    
    ##################################

    
    ####### TIMING RESOLUTION ########
    
    #timing_main.timingAnalysis()
    
    ##################################

    
    
    ######## TRACKING AND PLOTS ######
    
    #tracking_main.trackingAnalysis()
    
    ##################################
    
    
    ### PLOTS ###
    
    #noise_plot.noisePlots()
    #pulse_plot.pulsePlots()
    #timing_plot.timingPlots()

    ########### RESULTS ##############
    
    #results_main.produceResults()

   
    ######################################
   
    data_management.printTime()
    exit()




main()


