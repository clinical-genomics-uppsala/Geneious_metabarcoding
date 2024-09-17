# Geneious workflow for classification of nanopore metabarcoding data

[Geneious](https://www.geneious.com) workflow to analyze nanopore metabarcoding data. The workflow performs pre-processing and runs a wrapper plugin for [Emu](https://github.com/treangenlab/emu) for taxonomic classification of sequences. Pre-processing includes length filtering, matching and trimming of primers. The workflow is currently adapted to 16S sequences using the emu standard database. The emu database is "a combination of rrnDB v5.6 and NCBI 16S RefSeq from 17 September, 2020. Taxonomy is also from NCBI on the same date. The resulting database contains 49,301 sequences from 17,555 unique bacterial and archaeal species". Post-processing includes Krona plots and a report in excel format.

input: fastq files   
main outputs: [Krona plots](https://github.com/clinical-genomics-uppsala/Geneious_metabarcoding/tree/main/data/krona.html) and [Excel report](https://github.com/clinical-genomics-uppsala/Geneious_metabarcoding/tree/main/data/emu.xlsx) for each run.

## System requirements
The workflow is tested on Windows and Mac, but may work on Linux.
- Geneious
- Python 3
- Docker
- [Geneious Wrapper Plugin Creator](https://www.geneious.com/api-developers/)
- Geneious BBDuk plugin

&nbsp;
&nbsp;

# Installation

## Build docker images for emu and Krona  
`cd emu_wrapper`  
`docker build -f emu.Dockerfile -t emu:2024-05-13 .`  
`docker build -f krona.Dockerfile -t krona:2024-05-13 .`

Transfer docker image to another computer  
`docker save -o path/to/emu2024-05-13.tar emu:2024-05-13`  
`docker load -i path/to/emu2024-05-13.tar`  


## Setup Geneious wrapper plugins

1. Create BBDuk_match_primers wrapper plugin: Go to 'File' --> 'Create/Edit Wrapper Plugin..'. Press '+New'
- Step 1: 
	- Fill in 'Plugin Name:' and 'Menu/Button Text:' of your choice. 
	- 'Plugin Type:' select 'General Operation'.
	- 'Bundled Program Files (optional)' add:  
		path to powershell for example `C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe` under 'Windows'
		nothing under 'Mac OSX' or 'Linux'   
- Step 2: 
	- 'Sequence Type:' select 'Nucleotide only'.
	- 'Document Type:' select 'Unaligned Sequences (1+)'.
	- 'Format:' select 'FastQ (Sanger scores)'.
	- 'Command Line' (for Mac):  
		`-Xmx1g in=[inputFileNames] out=nomatch.fastq outm=match.fastq rcomp=t copyundefined=t k=19 hdist=3 literal=AGAGTTTGATCMTGGCTCAG,CGGTTACCTTGTTACGACTT ordered=t trd=t` 
	- 'Command Line' (example for Windows):  
	`C:\Program`` Files\Geneious`` Prime\jre\bin\java.exe -ea -Xmx1g -cp C:\Program`` Files\Geneious`` Prime\bundledPlugins\com.biomatters.plugins.bbtools.BBToolsPlugin\com\biomatters\plugins\bbtools\BBMap_38.84\bbmap\bbmap.jar jgi.BBDuk2 in=[inputFileNames] out=nomatch.fastq outm=match.fastq rcomp=t copyundefined=t k=19 hdist=3 literal=AGAGTTTGATCMTGGCTCAG,CGGTTACCTTGTTACGACTT ordered=t trd=t`
	- Under 'Output' 'File Name:' `match.fastq` and select 'Format:' 'Auto-detect' 
- Step 3:
	Press 'OK'

&nbsp;

2. Create Emu wrapper plugin: Go to 'File' --> 'Create/Edit Wrapper Plugin..'. Press '+New'
- Step 1: 
	- Fill in 'Plugin Name:' and 'Menu/Button Text:' of your choice. 
	- 'Plugin Type:' select 'General Operation'. 
	- 'Bundled Program Files (optional)' add:  
		`emu.py` under 'Linux' and 'Mac OSX'  
		`emu.bat` under 'Windows'  
	- 'Additional Bundled Files (optional)' add: `emu.py`
- Step 2: 
	- 'Sequence Type:' select 'Nucleotide only'.
	- 'Document Type:' select 'Unaligned Sequences (1+)'.
	- 'Command Line':
		`-o emu_output.tsv -g [inputFolderName] [otherOptions]`
	- Under 'Output' 'File Name:' `emu_output.tsv` and select 'Format:' 'Text file (plain)'
- Step 3:  
	Press 'Add' to add two user options (in this order):   
	- 'Command Line Switch': pathToDocker, 'Option Label': Docker path  
	- 'Command Line Switch': pathToData, 'Option Label': Data path  
	- 'Command Line Switch': kronaImage, 'Option Label': Krona docker image 
	- 'Command Line Switch': emuImage, 'Option Label': Emu docker image  
	- 'Command Line Switch': noThreads, 'Option Label': Threads
	
	Both 'Command Line Switch' and 'Option Label' should be filled in. Labels can be modified.

&nbsp;

## Setup Geneious workflows
1. Import `16SPrimers.geneious` (or add your own primers)
2. Import `16S_nanopore_pre-processing.geneiousWorkflow`
	- Add the BBDuk_match_primers plugin to the corresponding step. For Mac: under the option 'BBDuk_match_primers Program File' add the path to BBDuk plugin for example `/Users/xxxxx/bbmap/bbduk.sh`
	- Edit the two BBDuk steps. One step to trim primers from left end (27F and 1492R) and one for right end (27F_rev and 1492R_rev).
3. Import `16S_nanopore_pre-processing_Emu.geneiousWorkflow`
	- Add the `16S_nanopore_pre-processing.geneiousWorkflow` workflow to the corresponding step.
	- Add the Emu wrapper plugin to the corresponding step.
	- Edit the options for the Emu wrapper plugin. Add the path to docker on your system, the names of the docker images, and the number of threads to be used.  
	
	![Options for the Emu plugin](images/workflowOptions.png?raw=true)  

&nbsp;
&nbsp;

# Running the workflow

Import the fastq files to Geneious. Select the files and go to 'Workflows' --> 'Run Workflow' and select '16S nanopore: pre-processing + emu'.  
![Options when starting the workflow](images/startWorkflow.png?raw=true)  
 'Export to Folder' and 'Data path' must point to the same folder which should not contain any fasta files already. In Geneious, the output will be a frequency table (counts) combined for all samples, or for a single sample, a table with both relative abundance and counts. Full output will be saved to disk including all emu output files, a html file with krona plots and an excel report.