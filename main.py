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

import run_log_metadata as md
import data_management as dm
import time


def main():

    # Select how many runs, which batches and which sensors to be run
    number_of_runs = 0
    
    # batches must be list, or "all". Exclusion of batches also possible
    batches = [207, 301] #missing last
    batches_exclude = []
    
    # The sensor which is supposed to be analyzed, "" == all sensors
    sensor = ""
    
    md.setLimitRunNumbers(number_of_runs)
    md.setBatchNumbers(batches, batches_exclude)
    md.setSensor(sensor)
    dm.printTime()

    ############## METHODS ###############
    
    
    ############# NOISE ##############
    
    #noise_main.noiseAnalysis() # This is a long procedure function
    #noise_plot.noisePlots()
    
    ##################################

    
    ########### PULSE ################

    pulse_main.pulseAnalysis() # This is a long procedure function
    pulse_plot.pulsePlots()
    
    ##################################

    
    ####### TIMING RESOLUTION ########
    
    timing.timingAnalysis()
    timing_plot.timingPlots()
    
    ##################################

    
    ######### TRACKING  ##############
    
    #tracking.trackingAnalysis()
    
    ##################################


    ########### RESULTS ##############
    
    #results.produceResults()

   
    ######################################
   
    dm.printTime()
    exit()


main()


