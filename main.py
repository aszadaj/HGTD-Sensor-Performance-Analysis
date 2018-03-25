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


#metadata.setupATLAS()

def main():
    
    data_management.printTime()
    
    # This is only used for me, for storing the oscilloscope on an external drive
    data_management.setIfOnHDD(False)
    data_management.setIfOnHITACHI(False)
    
    #### Settings used for debugging noise and pulse analysis ####
    metadata.setLimitRunNumbers(1)
    metadata.setEntriesForQuickAnalysis(0)
    #############################################################
    
    
    # Choose batch numbers to run
    metadata.setBatchNumbers([507])
    #metadata.setBatchNumbers([101, 108, 207, 306, 401, 507, 707]) # all for tracking




    ############## METHODS ###############
    
    
    ######## NOISE ##########
    
    #noise.noiseAnalysis()
    
    #########################

    
    ######## PULSE ##########
    
    #pulse.pulseAnalysis()
    
    #########################

    
    ###### TRACKING #########
    
    tracking.trackingAnalysis()
    
    #########################
    
    
    ### TIMING RESOLUTION ###
    
    #timing.timingAnalysis()
    
    #########################
    
    
    ### PLOTS ###
    
    #noise_plot.noisePlots()
    #pulse_plot.pulsePlots()
    #timing_plot.timingPlots()
    
   
    #######################################
   
    data_management.printTime()
    exit()




main()






















