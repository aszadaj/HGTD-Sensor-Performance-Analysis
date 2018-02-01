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
import metadata

#md.setupATLAS()

def main():
    
    metadata.printTime()
    
    ######  NOISE, PULSE, TELESCOPE AND TIMING   ######
    
    metadata.setBatchNumbers([306, 507, 707])        # For now available 306, 507 and 707
    metadata.setLimitRunNumbers(3)              # Run numbers to be considered (0 = all)
    metadata.setEntriesForQuickAnalysis(0)    # Entries to be considered (0 = all)
    metadata.setSigma(5)                        # Define sigma variable
 
    
    # METHODS #
    
    noise.noiseAnalysis()
    noise_plot.noisePlots()
    
    pulse.pulseAnalysis()
    pulse_plot.pulsePlots()
    
    tracking.trackingAnalysis()
    
    timing.timingAnalysis()
    
    ###########
    
    metadata.printTime()
    exit()


main()

# Log 19.01.2018

# Noise and pulse analysis converted to receive and export original data
# Exported data are in V and "negative" values
# Conversion is made inside plot functions
# Continue with adapting timing functions
# Check why the noise and pedestal plot gives a not gaussian form
# Add fit functions to those plots
# Check if setupATLAS is ok or not



# Log1 09.12.2017
# redefined sigma value after check in the waveforms function
# Program is adapted to receive code in batches and exports them as pickle files
# amplitudes and rise time are large, but not too large.
# New file rise time half maximum is a reference point for

# Log2
# The lowered sigma gives more values but the SiPM have a higher noise and the sigma is
# too low. There fore testing with sigma = 6 for SiPM and sigma=5 for rest of the sensors

# log3
# Checked how many values are removed percentually and its about
#Fraction of removed amplitudes, due to critical value
#0.001 chan0
#0.001 chan1
#0.001 chan2
#0.001 chan3
#0.015 chan4
#0.009 chan5
#0.0135 chan6


# log

# improved the polyfit analysis, now check how the distributions look like

# Changed also the way of obtaining the first index when calculating a pulse. I removed earlier three points, now there is only one, deduced that from observing where the threshold is situated


# log 15122017 changed analysis of noise, noted that there is a problem with selecting the area
# and how the dataset is chosen
# noted that the fix will be better if condition set on len of data points which should be 1002.

# Available batch numbers:
# 101, 102, 103, 104, 105, 106, 107, 108
# 203, 204, 205, 206, 207,
# 301, 302, 303, 304, 305, 306,
# 401, 403, 404, 405, 406,
# 501, 502, 503, 504, 505, 506, 507,
# 701, 702, 703, 704, 705, 706, 707


