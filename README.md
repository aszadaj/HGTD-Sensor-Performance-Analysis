# HGTD Test Beam September 2017 Sensor Performance Analysis


# Overall info

The software package is a part of M.Sc. thesis done at KTH Royal Institute of Technology and CERN.

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

the latter three packages can be found in ```pip2``` by installing those

    pip2 install numpy
    pip2 install root_numpy
    pip2 install pathos


When the code is ready to run, run the code without any function. Then, folders with subfolders will be created in 
```../folder_sensor_perfomance_tb_sep17/```. 


The code needs oscilloscope files of the type ```data_'timestamp'.tree.root```-format placed in

    ../folder_sensor_perfomance_tb_sep17/oscilloscope_data_hgtd_tb_sep17/

The ```.root```files are converted with ```/supplements/convertOscRawToRootTree.C```. 


For the ```trackingPlots()```, tracking files are needed of the format ```tracking'timestamp'.root```. They need to be 
placed in the folder 

    ../folder_sensor_perfomance_tb_sep17/data_hgtd_tb_sep17/tracking/tracking/



# How to run


The code can be run in the terminal/console by providing

    $ python2 main.py

which creates all folder and subfolders from the file ```supplements/folderPaths.csv``` before the code can run. 


The code can be modified to choose which batches which each contain at least one run or multiple depending on batch. 
The information on the structure of which batches and runs is listed in

    run_list_tb_sep_2017.csv  


One can then select which methods to run by commenting out the functions in  ```main.py```.

The examples of choosing batches are

```batches = "all" ```              for all batches
```batches = [101] ```              batch 101 only (with 5 runs)
```batches = [102, 401] ```    and so on.

```batches_exclude = [501] ```  is used when multiple batches are used which can exclude the selected batch.


One can also choose which sensor to run with, 

```sensor = "W9-LGA35" ``` just one sensor
```sensor = "" ``` all sensors 

which produces plots for selected sensor. This is ignored (where all sensors are considered) for functions which produces 
data files, that is  ```pulseAnalysis()```.


The function ```pulseAnalysis()```  exports data files which are used by plot functions. Therefore to save time, one does 
not need to run them again.
One run file (MacBook Pro 2.8 GHz-i7 dual core 2013 four threads) takes approximatelly 8 mins and all 117 files about 
14 hours. The time can be shortened in pulseAnalysis by increasing the variable ```threads = 4``` in ```pulse_main.py```.



# pulseAnalysis() and pulsePlots()


```pulseAnalysis() - method```


This section receives an oscilloscope file and produces nine ROOT files placed in
```folder_sensor_perfomance_tb_sep17/data_ROOT/pulse``` . The categories are

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

The produced ROOT files are located in

    folder_sensor_perfomance_tb_sep17/data_ROOT/pulse


 ```pulsePlots() - method```
 
The function receives produced files from the   ```pulseAnalysis()``` and concatenates all runs within a batch and plots 
all the different properties. These are placed in

    folder_sensor_perfomance_tb_sep17/plots_sensors

which are subdivided into each sensor. Additionally ROOT files with histograms are produced with same folder structure in 

    folder_sensor_perfomance_tb_sep17/data_ROOT/histograms_data


```NOTE```: If the code gives error when calculating the pulses, that is
```results = Pool.map(lambda part: signalAnalysis(part, part + step), ranges)```  L.64 in ```pulse_main.py``` 
it is an error related to memory allocation when creating a Numpy-object for polynomial fit (appears on macOS 10.13 
High Sierra). It disappears when running the code again (or after multiple times).



# timingPlots()
  
  The function produces timing resolution plots of two kinds, using two different location of the pulses.
  It creates a timing resolution file, if there is no such produced already. The function produces plots with
  1. Timing resolution for time differences of SiPM and DUT, using location of the peak and using CFD (fraction 0.5) method
  2. Timing resolution for time differences between a combination of four connected sensors and solve a system of equations. 
      Uses both location   of the peak and using CFD (fraction 0.5) method.
  
  The produced ROOT files are located in
  
    folder_sensor_perfomance_tb_sep17/data_ROOT/pulse
  
  and the produced plots for each sensor are in
  
    folder_sensor_perfomance_tb_sep17/plots_sensors
  


# trackingPlots()

The function imports the exported files from the previous analyses together with provided tracking files.
The tracking file has trees 'X' and 'Y' for each event. The method imports files for each batch and 
produces plots for

1. Efficiency
2. Inefficiency
3. Gain (related to charge)
4. Rise time
5. Pulse mean amplitude
6. Timing resolution, CFD and peak time

and exports them into each sensor folder in 

    folder_sensor_perfomance_tb_sep17/plots_sensors


 There is a method ```calculateCenterOfSensorPerBatch()``` of calculating the center of the sensors which is 
 turned on by default. This can be done once for each group of batches, meaning the data is the same for batch 101 as for 108.



# resultsAnalysis()

From the previously exported files, this collectes all of them and plots them into

    folder_sensor_perfomance_tb_sep17/plots_sensors/results



# waveform_debug.py

There is an additional function aimed to analyze chosen event for a sensor. It requires an oscilloscope for a given run.
It is run independently of ```main.py``` in the console

    $ python2 waveform_debug.py
    




# Adaptation to other test beam campaigns

The code is suited to be adapted for other test beam campaigns. Some notes should be noted:

Timing resolution analysis:
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
5. Create one file, NTuples, which have the information for each event with a pulse (passing the threshold) with the charactertics 
    of the signal.
