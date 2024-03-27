# Geneious wrapper plugin for Emu

Under development

[Geneious](https://www.geneious.com) wrapper plugin to run [Emu](https://gitlab.com/treangenlab/emu) to classify 16S sequences from nanopore amplicon data.
The plugin runs an Emu docker container from Geneious. The Emu standard database is included in the docker image. The plugin is adapted to run in a workflow where the previous step exports the selected sequence files to a folder selected by the user.

- input: Geneious sequence documents/lists
- output Geneious: Emu table (counts) combined for all samples, or Emu table for single sample with relative abundance and counts
- output on disk: Emu output for each sample and combined

## System requirements
The plugin is adapted to both Windows, Mac and Linux
- Geneious
- Python 3
- Docker

## Plugin installation

1. Build docker image:
`docker build -f emu.Dockerfile -t emu:3.4.5 .`
2. Download and install [Geneious Wrapper Plugin Creator](https://www.geneious.com/api-developers/)
3. Create Emu wrapper plugin: Go to 'File' --> 'Create/Edit Wrapper Plugin..'. Press '+New'
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
	- 'Command Line Switch': emuImage, 'Option Label': Docker image  
	- 'Command Line Switch': noThreads, 'Option Label': Threads
	
	Both 'Command Line Switch' and 'Option Label' should be filled in. Labels can be modified.

## Workflow
`Emu.geneiousWorkflow`