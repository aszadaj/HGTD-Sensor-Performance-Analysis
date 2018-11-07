# HGTD Sensor Perfomance analysis


# Overall info

The code analyzes properties of the sensors from data provided from the test beam measurement done in September 2017. 
Main focus are timing resolution of the sensors, efficiency, which is a ratio between a signal from the sensor with a recorded 
hit on the MIMOSA, that is the telescope.


# Prerequisites

Furthermore the code needs packages to run with. These are

- python 2.7.10
- ROOT 6.12.04
- numpy 1.15.2
- root-numpy 4.7.3
- pathos 0.2.2.1

The latter three packages can be found in ```pip2``` by installing those

```pip2 install numpy```
```pip2 install root_numpy```
```pip2 install pathos```

When the code is ready to run, folders with subfolders are created in ```../folder_sensor_perfomance_tb_sep17/```. The code needs files of the type ```data_'timestamp'.tree.root```-format placed in ```../folder_sensor_perfomance_tb_sep17/oscilloscope_data_hgtd_tb_sep17/```. The ```.root```files are converted with  ```convertOscRawToRootTree.C``` which is in the folder  ```/supplements/```. 

For the ```trackingAnalysis()```, tracking files are needed of the format ```tracking'timestamp'.root```. They need to be placed in the folder 

```../folder_sensor_perfomance_tb_sep17/data_hgtd_tb_sep17/tracking/tracking/```



# How to run


The code can be run in the terminal/console by providing

```python2 main.py```

which creates all folder and subfolders from the file ```supplements/folderPaths.csv``` before the code can run. 

The code can be modified to choose which batches which each
contain at least one run or multiple depending on batch. The information on the structure of which batches and runs is
listed in

```run_list_tb_sep_2017.csv```.  

One can then select which methods to run by commenting out the functions in  ```main.py```.

The examples of choosing batches are

```batches = "all" ``` takes all batches
```batches = [101] ``` uses batch 101 only (with 5 runs)
```batches = [102, 401] ``` and so on.

```batches_exclude = [501] ``` is used when multiple matches are used which can exclude the listed batch.

```number_of_runs = "all" ``` considers all files within a batch to be calculated or a specific number. "all" is a default value selecting all runs. This only applies to ```pulseAnalysis()``` which can take shorter time to analyze.


One can also choose which sensor to run with, 

```sensor = "W9-LGA35" ``` just one sensor
```sensor = "" ``` all sensors 

which produces plots for selected sensor. This is ignored (where all sensors are considered) for functions which produces data files, that is  ```pulseAnalysis()``` and  ```timingAnalysis()```.

Generally functions ```pulseAnalysis()``` and  ```createTimingFiles()``` exports data files which are used by plot functions and ```trackingAnalysis()```. Therefore to save time, one does not need to run them again.
One run file (MacBook Pro 2.8 GHz-i7 dual core 2013 four threads) takes approximatelly 5 mins and all 117 files about 10 hours. The time can be shortened in pulseAnalysis by increasing the variable ```threads = 4``` in ```pulse_main.py```.


# pulseAnalysis() and pulsePlots()

```pulseAnalysis() - method```

This section receives an oscilloscope file and produces nine ROOT files placed in   ```folder_sensor_perfomance_tb_sep17/data_ROOT/pulse``` . The categories are

1. CFD = time location at half of the rising edge of the pulse
2. Charge = pulse integral over the pulse divided by the sensors resistivity
3. Max sample = maximum sample above the threshold
4. Noise = standard deviation of the backround signal, selection before a signal
5. Peak time = time location at maximum value of the pulse
6. Peak value = Pulse amplitude value using fits and corrections
7. Pedestal = averaged value of the background signal, selection before a signal
8. Rise time = rise time defined between 10% and 90% of the rising edge of the pulse

The files are exported per run number, where each run number contains around 200k events, which are subdivided
into channels ('chan0', 'chan1', etc) depending on the run, where each entry contains either a 0 (not calculated) or a value.
Time dimension = [ns], voltage dimension = [-V]

 ```pulsePlots() - method```
 
The function receives produced files from the   ```pulseAnalysis()``` and concatenates all runs within a batch and plots all the different properties. These are placed in ```folder_sensor_perfomance_tb_sep17/plots_sensors``` which are subdivided into each sensor. Additionally ROOT files with histograms are produced with same folder structure in ```folder_sensor_perfomance_tb_sep17/data_ROOT/histograms_data```. 

NOTE: If the code gives error when calculating the pulses, that is ```results = Pool.map(lambda part: signalAnalysis(part, part + step), ranges)``` L.64 in ```pulse_main.py``` it is an error related to memory allocation (appears on macOS 10.13 High Sierra). It disappears when running the code again (or after multiple times).



# createTimingFiles() and timingPlots()

  ```createTimingFiles() - method```
  
This file imports ROOT files created with ```pulseAnalysis()``` with time location information. So both 'CFD' and 'peak time' are imported and then the time difference is calculated. There are two method of obtaining it,
  1. Linear - which is the time difference between the DUT and the SiPM
  2. System - which are time differences between each of the combinations within the first oscilloscope.
  
Additionally this is done for both 'CFD' and 'peak time'. The files are exported to ```folder_sensor_perfomance_tb_sep17/data_ROOT/timing``` having the same kind of structure as ```pulseAnalysis()```.

  ```timingPlots() - method```



# trackingAnalysis()

The function imports the exported files from the previous analyses together with provided tracking files placed in 
 ```folder_sensor_perfomance_tb_sep17/data_hgtd_tb_sep17/tracking/tracking```. There is a method
 
 ```calculateCenterOfSensorPerBatch()``` 
 
 of calculating the center of the sensors which is turned on by default. This can be done once for each group of batches, meaning the data is the same for batch 101 as for 108.
 The method imports files for each batch and produces plots for
 1. Efficiency
 2. Inefficiency
 3. Gain (related to charge)
 4. Rise time
 5. Pulse mean amplitude
 6. Timing resolution, CFD and peak time
 
 The tracking file has trees 'X' and 'Y' for each event. 
 
 
# resultsAnalysis()

From the previously exported files, this collectes all of them and plots them into  ```folder_sensor_perfomance_tb_sep17/plots_sensors/results```



# Adaptation to other test beam campaigns

The code is suited to be adapted for other test beam campaigns. Some notes should be noted:

Timing resolution Analysis:
1. The code handles only one SiPM named "SiPM-AFP".
2. The system of equations is restricted to the first oscilloscope.

Tracking Analysis
1. The tracking-code is adapted to rotate and center for TB Sep 2017.

Other
1. The run log needs to be in the same structure as ```run_list_tb_sep_2017.csv```.  


# What can be improved with the software

1. ```pulseAnalysis()``` creates 8 types of different .root files, which could be stripped into one (optional).
2. ```resultsAnalysis()``` contains hard-coded functions which could be improved. 
3. Remove the dependence using time location at the peak of the pulse.
4. Implement ```convertOscRawToRootTree.C``` to automatically convert missing files which imports it from lxplus.
