# Noise analysis from oscilloscope data

 ```noise.py```
The input file is a ROOT file with a chosen timestamp for a specific run in TB 2017. The code translates theo scilloscope data,
to obtain noise and analyse impulses. To do so, the code calculates the distributions in each channel for all entries.
The data points are selected in such way to have information only until each pulse for each entry. The output of this code is
in form of plots for each channel (all entries) with a histogram for mean values from each entry, to see how they change
over each entry and have value for each channel's pedestal. This also creates distribution plots of mean noise value for all entries in the file as well as creating a distribution plot for standard deviation values (here noise).

Reads a ROOT file organized in TTree with leafs with 8 channels, labeled tchan0, tchan 1,...,tchan7

# Pulse analysis

 ```pulse.py```

Analysing the same input file, using the information produced from the noise analysis, it analyses maximal amplitude values and rise times and creates distribution plots for both amplitude values and rise times for physical values.


# Telescope analysis

The file here which is tested is  ```data_1504818689.tree.root``` and is for run number  ```3656```.


# File under test

The file here which is tested is  ```data_1504818689.tree.root``` and is for run number  ```3656```.

