# Noise analysis from oscilloscope data

 ```noise.py```
The input file is a ROOT file with a chosen timestamp for a specific run in TB 2017. The code translates  oscilloscope data, to obtain noise and analyse impulses. To do so, the code calculates the distributions in each channel for all entries. The data points are selected in such way to have information only until each pulse for each entry. The output of this code is in form of plots for each channel (all entries) with a histogram for mean values from each entry, to see how they change over each entry and have value for each channel's pedestal.


Before running ```noise.py``` check inside the file which file it is referencing. The code will give outputs in form of distribution plots inside folder ```pedestal_channel```.

Reads a ROOT file organized in TTree with leafs with 8 channels, labeled tchan0, tchan 1,...,tchan7

# Pulse analysis

 ```pulse.py```

The idea is to analyse risetime, amplitude, amplitude to ratio and other information related to how the pulses behave, depending on the channel. Code not ready.


# File under test

The file here which is tested is  ```data_1504818689.tree.root``` and is for run number  ```3656```.

