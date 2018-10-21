#include <TTree.h>
#include <TFile.h>
#include <TH2.h>
#include <TCanvas.h>
#include <TStyle.h>
#include <TSystem.h>

#include <algorithm>
#include <iostream>
#include "sdd_mmap.c"



int combinedNtuple(TString fname){
    std::vector<double> * vec_buf[8] = {0,0,0,0,0,0,0,0};
    float buf[8][NSMAX];  

    if (scope_data_init(gSystem->ExpandPathName(fname.Data())) != 0) return 1;
    TTree *tree = new TTree("oscilloscope", "HGTD oscilloscope tree");
    
    // Open ROOT file and create output tree
    TString filename(fname);
    filename.ReplaceAll(".txt", ".tree.root");
    
    // This line is added to export the converted .tree.root file to my /eos/ directory. Otherwise
    // it will export to /eos/(...)/testbeam/ where permission is denied.  /A.S (2018)
    filename.ReplaceAll("/eos/atlas/atlascerngroupdisk/det-hgtd/testbeam/September2017_A/RAW_oscilloscope/","/eos/user/a/aszadaj/SH203X/HGTD_material/oscilloscope_data_sep_2018/");
    
    TFile *ofile = TFile::Open(filename.Data(),"RECREATE");
  
    for ( int i = 0; i < nch[0]+nch[1]; i++ )
    {
	tree->Branch((std::string("chan")+std::to_string(i)).c_str(), &vec_buf[i] );
	vec_buf[i] = new std::vector<double>();
	vec_buf[i]->resize(NSMAX);
    }
    
    // For some files, it could be ok to comment this function to convert the .tree.root anyway
    // and then strip the number which are desynchronized at the end. But be warned! Check
    // the printout in the command line to see if there are unsynchronized events. /A.S (2018)
    
//    if ( nevt_tot[0] != nevt_tot[1] )
//    {
//    std::cout << "ERROR: Inconsistent number of events between oscilloscopes!" << std::endl;
//    return -1;
//    }
    
    for (unsigned int ientry = 0; ientry < nevt_tot[0]; ++ientry)
    {
	if ( ientry % 10000 == 0 ) 
	{
	    std::cout << "Processing event number: " << ientry << std::endl;
	    //tree->Write(0,TObject::kOverwrite);
	}
	
	// Load oscilloscope data for each channel
	if (getEvent(ientry))
	{
	    std::cerr << "Problem loading event " << ientry << " from oscilloscope data" << std::endl;
	    break;
	}
        
	for (int ichannel = 0; ichannel < nch[0]+nch[1]; ++ichannel)
	{
	    int nsamples  = getAdcData(ichannel, buf[ichannel], NSMAX);
	    vec_buf[ichannel]->assign(buf[ichannel], buf[ichannel]+nsamples);
	}
	tree->Fill(); // last entry
    }

    tree->Write(0,TObject::kOverwrite);

    ofile->Close();
    return 0;
}
