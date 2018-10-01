# HGTD Sensor Perfomance analysis


# Overall info

The code analyzes properties of the sensors from data provided from the test beam measurement done in September 2017. 
Main focus are timing resolution of the sensors, efficiency, which is a ratio between a signal from the sensor with a recorded 
hit on the MIMOSA, that is the telescope.


# Prerequisites

To run the code, certain files are needed. The raw data format is on LXPLUS and needs to be converted into ```data_'timestamp'.tree.root```-format
This is done by using the  ```convertOscRawToRootTree.C``` which is in  ```folder_sensor_perfomance_tb_sep17/convertRawOscData/```. 
It uses ```combinedNtuple.C``` where one can specify which data files to convert.

Additionally tracking files are needed. The tracking files are in  ```folder_sensor_perfomance_tb_sep17/data_hgtd_tb_sep17/tracking/tracking/``` For this code, which is from the September 2017 test beam measurement the tracking files are provided. They are structured to have for each event positions for x and y in micrometers.



Furthermore the code needs packages to run with. These are

- python 2.7
- ROOT 6.10.06
- numpy 1.15.2
- root-numpy 4.7.3
- pathos multiprocessing (can be found in pip)

The code requires certain subfolders to be in correct place. The folder ```folder_sensor_perfomance_tb_sep17``` provides the structure
which the code can be run with. In the file ```data_management.py``` in the function ```defineDataFolderPath()```
this information can be modified.



# How to run


The code can be run in the terminal/console by providing

```python2 main.py```

where the order of the listed functions is important for the first time. The code can be modified to choose which batches which each
contain at least one run or multiple depending on batch. The information on the structure of which batches and runs is
listed in ```run_list_tb_sep_2017.csv```.  One can then select which methods to run by commenting out the functions in  ```python2 main.py```.

The examples of choosing batches are

```batches = "all" ``` takes all batches
```batches = [101] ``` uses batch 101 only (for example it has 5 run f)
```batches = [102, 401] ``` and so on.

```batches_exclude = [501] ``` is used when multiple matches are used which can exclude the listed batch.

```number_of_runs = 0 ``` considers all files within a batch to be calculated or a specific number. This only applies to ```pulseAnalysis()``` which can take shorter time to analyze.


One can also choose which sensor to run with, 

```sensor = "W9-LGA35" ``` just one sensor
```sensor = "" ``` all sensors 

which produces plots for selected sensor. This is ignored (where all sensors are considered) for functions which produces data files, that is  ```pulseAnalysis()``` and  ```timingAnalysis()```.



# pulseAnalysis() and pulsePlots()

```pulseAnalysis() - method```
This section receives an oscilloscope file and produces nine ROOT files placed in   ```folder_sensor_perfomance_tb_sep17/data_hgtd_tb_sep17/pulse``` . The categories are

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
 
The function receives produced files from the   ```pulseAnalysis()``` and concatenates all runs within a batch and plots all the different properties. These are placed in ```folder_sensor_perfomance_tb_sep17/plots_hgtd_tb_sep17``` which are subdivided into each sensor. Additionally ROOT files with histograms are produced with same folder structure in ```folder_sensor_perfomance_tb_sep17/data_hgtd_tb_sep17/histograms_root_data```. This function export the results all categories, except maximum sample, CFD and peak time. to ```folder_sensor_perfomance_tb_sep17/data_hgtd_tb_sep17/results``` for each sensor



# timingAnalysis() and timingPlots()

  ```timingAnalysis() - method```
  
This file imports ROOT files created with ```pulseAnalysis()``` with time location information. So both 'CFD' and 'peak time' are imported and then the time difference is calculated. There are two method of obtaining it,
  1. Linear - which is the time difference between the DUT and the SiPM
  2. System - which are time differences between each of the combinations within the first oscilloscope.
  
Additionally this is done for both 'CFD' and 'peak time'. The files are exported to ```folder_sensor_perfomance_tb_sep17/data_hgtd_tb_sep17/timing``` having the same kind of structure as ```pulseAnalysis()```.
  
```timingPlots() - method```

The function imports the files from previous function, concatenates all in the same batch, obtains the width and exports it to ```folder_sensor_perfomance_tb_sep17/data_hgtd_tb_sep17/results``` for each sensor.



# trackingAnalysis()

The function imports the exported files from the previous analyses together with provided tracking files placed in 
 ```folder_sensor_perfomance_tb_sep17/data_hgtd_tb_sep17/tracking/tracking```. There is a method
 of calculating the center of the sensors which is turned off by default. The method imports files for each batch and produces plots for
 1. Efficiency
 2. Inefficiency
 3. Gain (related to charge)
 4. Rise time
 5. Pulse mean amplitude
 6. Timing resolution, cfd and peak time
 
 
# resultsAnalysis()

From the previously exported files, this collectes all of them and plots them into  ```folder_sensor_perfomance_tb_sep17/results_plots_hgtd_tb_sep17/```
