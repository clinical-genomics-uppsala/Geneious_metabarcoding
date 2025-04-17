# Geneious workflow for classification of nanopore metabarcoding data

[Geneious](https://www.geneious.com) workflow to analyze nanopore metabarcoding data. The workflow performs pre-processing and runs a wrapper plugin for [emu](https://github.com/treangenlab/emu) for taxonomic classification of sequences. Pre-processing includes length filtering, matching and trimming of primers. The workflow is currently adapted to 16S sequences using the emu standard database. The emu database is "a combination of rrnDB v5.6 and NCBI 16S RefSeq from 17 September, 2020. Taxonomy is also from NCBI on the same date. The resulting database contains 49,301 sequences from 17,555 unique bacterial and archaeal species". Post-processing includes Krona plots and a report in excel format.

Input: FASTQ files. Sample file names should preferably start with barcode no: 01, 02.. or with barcode49, barcode27. Sample names should not contain any spaces, dots or special characters (å/ä/ö etc).  
Main outputs: [Krona plots](data/test_report/krona.html) and [Excel report](data/test_report/emu.xlsx) for each run.

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

## Setup Geneious wrapper plugins

### 1. Create BBDuk_match_primers wrapper plugin 
Go to 'File' --> 'Create/Edit Wrapper Plugin..'. Press '+New'
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

### 2. Create Emu wrapper plugin
Go to 'File' --> 'Create/Edit Wrapper Plugin..'. Press '+New'
- Step 1: 
	- Fill in 'Plugin Name:' and 'Menu/Button Text:' of your choice. 
	- 'Plugin Type:' select 'General Operation'. 
	- 'Bundled Program Files (optional)' add:  
		`emu.py` under 'Linux' and 'Mac OSX'  
		`emu.bat` under 'Windows'  
	- 'Additional Bundled Files (optional)' add:
	 `emu.py` and `emu_report.py`
- Step 2: 
	- 'Sequence Type:' select 'Nucleotide only'.
	- 'Document Type:' select 'Unaligned Sequences (1+)'.
	- 'Command Line':
		`-o emu_output.tsv -g [inputFolderName] [otherOptions] 2>&1 > log.txt`
	- Under 'Output' 'File Name:' `log.txt` and select 'Format:' 'Text file (plain)'
- Step 3:  
	Press 'Add' to add two user options (in this order):
	- 'Command Line Switch': config_file, 'Option Label': Path to config file 
	- 'Command Line Switch': path_to_data, 'Option Label': Data path  
 
	Both 'Command Line Switch' and 'Option Label' should be filled in. Labels can be customized.

&nbsp;

## Setup Geneious workflows
1. Import `16SPrimers.geneious` (or add your own primers)
2. Import `16S_nanopore_pre-processing.geneiousWorkflow`
	- Add the BBDuk_match_primers plugin to the corresponding step. For Mac: under the option 'BBDuk_match_primers Program File' add the path to BBDuk plugin for example `/Users/xxxxx/bbmap/bbduk.sh`
	- Edit the two BBDuk steps. One step to trim primers from left end (27F and 1492R) and one for right end (27F_rev and 1492R_rev).
3. Import `16S_nanopore_pre-processing_Emu.geneiousWorkflow`
	- Add the `16S_nanopore_pre-processing.geneiousWorkflow` workflow to the corresponding step.
	- Add the Emu wrapper plugin to the corresponding step.
	- Edit the options for the Emu wrapper plugin. Add the path to the config file to be used and the folder where the output should be stored.  
	
	![Options for the Emu plugin](images/workflowOptions.png?raw=true)  

&nbsp;
&nbsp;

# Running the workflow

1. Adapt the [config file](emu_wrapper/config.ini), example:

```
[SOFTWARE]
path_to_docker = C:\Program Files\Docker\Docker\resources\bin\docker.exe
git_version = 1.0.0
krona_image = hydragenetics/krona:2025-04-09
emu_image = hydragenetics/emu:2025-04-15
```
Docker images are downloaded automatically but can also be downloaded from:  
`docker pull hydragenetics/emu:<tag>`  
`docker pull hydragenetics/krona:<tag>`  

| Geneious_metabarcoding | image |
| -------- | ------- |
| v1.0.0 | hydragenetics/emu:2025-04-15 |
| v1.0.0 | hydragenetics/krona:2025-04-09 | 


Parameters for emu, see the emu documentation for details.
```
[EMU]
seq_type = map-ont				# --type
database = 16S					# --db
min_abund = 0.0001				# --min-abundance
align_n = 50					# --N
batch_k = 500000000				# --K
no_threads = 8					# --threads
keep_counts = True				# --keep-counts
keep_files = True				# --keep-files
keep_read_assignments = True	# --keep-read-assignments
output_unclassified = True		# --output-unclassified
```
These parameters control formatting of the excel report:
```
[REPORT]
spike_taxa = "Imtechella halotolerans", "Allobacillus halotolerans", "Truepera radiovictrix"	# cells will be highlighted in orange in report
min_reads = 1000				# if the total number of reads in a sample is fewer than this value, sample total row => red
max_unassigned_prop = 0.9		# if the proportion of reads classified as "unassigned" is larger than this value, sample unassigned row => red
min_counts_taxa = 50			# if the number of reads is larger than this value for a taxon in a sample, the row => blue
min_abund_tot = 0.01			# if the proportion of reads for a taxon is larger than this value for a taxon in a sample, the row => blue
```

2. Import the FASTQ files to Geneious. Select the files and go to 'Workflows' --> 'Run Workflow' and select '16S nanopore: pre-processing + emu'.  
![Options when starting the workflow](images/startWorkflow.png?raw=true)  
 'Export to Folder' and 'Data path' must point to the same folder which should not contain any FASTA files (.fa/.fa.gz/.fasta/.fasta.gz) already. In Geneious, the output will be a log file. Full output will be saved to disk including all emu output files, a html file with krona plots and an excel report. See example output from a [small toy dataset](data/test_report).

 &nbsp;

 # Other

 ## Build docker images locally

If needed, docker images can be built locally from the docker files in this repo:  
`cd docker`  
`docker build -f emu.Dockerfile -t emu:<tag>> .`  
`docker build -f krona.Dockerfile -t krona:<tag>> .`

Transfer docker image to another computer:  
`docker save -o path/to/emu.tar emu:<tag>>`  
`docker load -i path/to/emu.tar` 