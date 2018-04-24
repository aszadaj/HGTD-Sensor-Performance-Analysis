#############################################
#                                           #
#                                           #
#         HGTD EFFICIENCY ANALYSIS          #
#                                           #
#                                           #
#############################################

import noise
import noise_plot
import pulse
import pulse_plot
import tracking
import timing
import timing_plot
import metadata
import data_management
import results
import graph


def main():
    
    data_management.printTime()

    #### Settings used for debugging noise and pulse analysis ####
    metadata.setEntriesForQuickAnalysis(40000)
    #############################################################
    
    # Choose batch numbers to run
    metadata.setLimitRunNumbers(0)
    # Yellow marked batches
    # batch 306 mark 3796, noise and pulse
    #metadata.setBatchNumbers([201, 202, 203, 207, 301, 306, 402, 604, 701, 705, 706, 805])
    #metadata.setBatchNumbers([604, 701, 805])
    #metadata.setBatchNumbers([301, 501, 701])
    metadata.setBatchNumbers([102, 302, 502])


    ############## METHODS ###############
    
    
    ######## NOISE ##########
    
    #noise.noiseAnalysis()
    
    #########################

    
    ######## PULSE ##########
    
    pulse.pulseAnalysis()
    
    #########################

    
    ### TIMING RESOLUTION ###
    
    timing.timingAnalysis()
    
    #########################
    
    
    
    ###### TRACKING #########
    
    #tracking.trackingAnalysis()
    
    #########################
    
    
    ### PLOTS ###
    
    #noise_plot.noisePlots()
    pulse_plot.pulsePlots()
    timing_plot.timingPlots()

    ### RESULTS ###
    
    #results.produceResults()

   
    #######################################
   
    data_management.printTime()
    exit()




main()


