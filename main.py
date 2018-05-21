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


def main():
    
    data_management.printTime()

    # Choose batch numbers to run
    metadata.setEntriesForQuickAnalysis(0)
    metadata.setLimitRunNumbers(0)
    metadata.setBatchNumbers([101])

    ############## METHODS ###############
    
    
    ######## NOISE ##########
    
    #noise.noiseAnalysis()
    
    #########################

    
    ######## PULSE ##########
    
    #pulse.pulseAnalysis()
    
    #########################

    
    ### TIMING RESOLUTION ###
    
    #timing.timingAnalysis()
    
    #########################
    
    
    
    ###### TRACKING #########
    
    tracking.trackingAnalysis()
    
    #########################
    
    
    ### PLOTS ###
    
    #noise_plot.noisePlots()
    #pulse_plot.pulsePlots()
    #timing_plot.timingPlots()

    ### RESULTS ###
    
    #results.produceResults()

   
    #######################################
   
    data_management.printTime()
    exit()




main()


