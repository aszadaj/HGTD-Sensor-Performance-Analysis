// This is a code which converts the RAW oscilloscope data into .tree.root file to be
// used for the analysis code. Is uses sdd_mmap.c (no idea where it actually comes from, Nikola M. probably)

// this has to be run in LXPLUS with the command

// >> root -L convertOscRawToRootTree.C+

// Change the input variable for the function combinedNtuple to match the correct directory
// in combinedNtuple.C, a line has been commented out, check for further details

// Additionally, to run this code, lxplus has to be setup to run with
//
// root 5.34.25-x86_64-slc6-gcc48-opt with the command
//
// >> setupATLAS
// >> localSetupROOT 5.34.25-x86_64-slc6-gcc48-opt
//
// For me, I had to configure this twice to make it work, be sure to not have any errors when
// configuring this.

{
    
  gROOT->ProcessLine(".L combinedNtuple.C++");
  std::cout << "DONE!" << std::endl;
  
    combinedNtuple("/eos/atlas/atlascerngroupdisk/det-hgtd/testbeam/September2017_A/RAW_oscilloscope/data_1504864077.txt");

}
