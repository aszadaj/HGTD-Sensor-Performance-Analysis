# HGTD Efficiency Analysis



# Overall info

This code analyses properties of the oscilloscope files given in data_XXXXX.tree.root format
from the TB SEP 17 measurement. The main focus of this code is structured in groups of 'noise', 'pulse', 'timing' and tracking.

 ```Data information```
 
The code's input is an oscilloscope file for a given run, structured as a 3-dim array with "channels", "events", and "data points". There
are 8 channels (chan0, chan1, chan2, ..., chan7), approximatelly 200000 events and 1002 data points. The data points lists voltages for
which the pulses are negative and the time separation between the points is defined to be 0.1 ns.

 ```Resources - resources/run_list_tb_sep_2017```
 
 In the resources file, there is a run log  ```run_list_tb_sep_2017.csv``` which is copied form the oficial run list with modifications.
 These modifications are in form of removed run numbers which were either corrupted (the oscilloscope files) are not relevant to be
 used. 88 files out of 130 are considered from the original one.
 
```Produced data location - HGTD_material/oscilloscope_data_sep_2017```

The location of oscilloscope files, not provided.

```Produced data location - HGTD_material/tracking_data_sep_2017```

Here are the telescope files. For the telescope files there are only for batches 306, 507 and 607
 
```Produced plots location - HGTD_material/plots_hgtd_efficiency_sep_2017```

Here are all produced plots from each of the sections listed below. In the folder there are different sensors listed and withing there are
different folders marking which analysis has been performed.

```Produced data location - HGTD_material/data_hgtd_efficiency_sep_2017```

Here are all produced ROOT files from each section.



# How to run

For this code the following packages has been used:
- python 2.7
- ROOT 6.10.06
- numpy 1.13.3
- root-numpy 4.7.3

The code can be run in the terminal/console by providing

```python2 main.py```

Before that, a list of functions can be choosed, these are:

- noise.noiseAnalysis() - oscilloscope files needed!
- pulse.pulseAnalysis() - oscilloscope files needed!

- timing.timingAnalysis()
- tracking.trackingAnalysis()

- noise_plot.noisePlots()
- pulse_plot.pulsePlots()
- timing_plot.timingPlots()

The first two functions needs oscilloscope files to run with. In general they do not to be run, since all files have been already created and exported. These are in ```HGTD_material/data_hgtd_efficiency_sep_2017``` folder.
The methods are chosen by commenting out those which are of interest.

##CHOOSING BATCHES

The function
metadata.setBatchNumbers([306])

Can be used to choose batches and the simplest way is to choose 306. There can be more chosen, for example

metadata.setBatchNumbers([306, 504])
 
or considering all batches
 
metadata.setBatchNumbers("all"). I suggest to use this only for producing plots, that is using the functions
which are related for producing plots.


# Noise analysis

  ```noiseAnalysis() - method```
This section receives an oscilloscope file and produces a two ROOT files, with run number XXXX:
1. noise_noise_XXXX.root
2. noise_pedestal_XXXX.root

1. Gets from each event the standard deviation of the noise before a pulse is found in this event. The results are then collected in a structured array with "channels" and "events".

2. Gets from each event the mean value of the noise before the pulse is found. The structure is the same.

 ```noisePlots() - method```
Given the produced noise-files, it concatenates all run numbers for each batch listed in the run log and produces two different plots,
one for each kind. These plots are then sorted in to sensor of interest.


# Pulse analysis

  ```pulseAnalysis() - method```
This section receives an oscilloscope file and produces a three ROOT files, with run number XXXX:
1. pulse_peak_time_XXXX.root
2. pulse_peak_value_XXXX.root
3. pulse_rise_time.XXXX.root

1. Gets information about the pulse and at which time in that event it happens.
2. Gets the maximal amplitude value of the same pulse
3. Gets the rise time, which is defined to be 10%-90% of the pulse.

 ```pulsePlots() - method```
Given the produced pulse-files, it concatenates all run numbers for each batch listed in the run log and produces three different plots
for each kind obtained in the analysis. These plots are then sorted in to sensor of interest.


# Timing resolution analysis

   ```timingAnalysis() - method```
 The method calculates the time difference for each event the peak location of the sensor of interest (DUT) and the SiPM (the reference
 sensor). This is then exported to a ROOT file with the same structure as a ROOT file
 
1. timing_XXXX.root

 ```timingPlots() - method```
 Given the exported file, it produces four kind of plots:
 1. timing_2d
 2. timing_2d_diff_event
 3. timing_2d_diff_lgad
 4. timing_2d_diff_sipm
 5. timing_distribution
 
 1. 2D plot of time location of the sensor vs the time difference
 2. 2D plot of event number of the calculated time difference vs the time difference
 3. 2D plot of maximal amplitude of the sensor of interest (DUT) vs the time difference
 4. 2D plot of maximal amplitude of the reference sensor (SiPM) vs the time difference
 5. 1D histogram of the time difference distribution
 
 

# Tracking - combined analysis

```trackingAnalysis() - method```
The methods concatenates the tracking data file listed in folder  ```tracking_data_sep_2017``` together with produced amplitude
values produced from pulse analysis. Together with those, it produces three different 2D plots. The tracking file is used to give
information on where on the sensors a hit has been recorded.

1. 2D mean value graph, where each bin is a mean value of the filled amplitude value
2. 2D efficiency graph which shows the fraction of noted hits from the sensor of interest and a noted hit from the tracking information (for each event)
3. Same as 2. but plotted as an inefficiency.

These plots are then sorted in to respective folder sensor.



