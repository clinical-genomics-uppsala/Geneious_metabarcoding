# Geneious wrapper plugin for Emu

Under development

[Geneious](https://www.geneious.com) wrapper plugin to run [Emu](https://gitlab.com/treangenlab/emu) to classify 16S sequences from nanopore amplicon data.
The plugin runs an Emu docker container from Geneious. The plugin is adapted to run in a workflow where the previous step exports the selected files to a folder selected by the user.

- input: Geneious sequence documents/lists
- output Geneious: Emu table (counts) combined for all samples
- output on disk: Emu output for each sample and combined

## System requirements
- Mac/linux
- Geneious
- Python 3
- Docker

## Plugin installation

1. Build docker image:
`docker build -f emu.Dockerfile -t emu3.4.4_image .`
2. Download and install [Geneious Wrapper Plugin Creator](https://www.geneious.com/api-developers/)
3. Create Emu wrapper plugin: Go to 'File' --> 'Create/Edit Wrapper Plugin..'. Press '+New'
- Step 1: 
	- Fill in 'Plugin Name:' and 'Menu/Button Text:' of your choice. 
	- 'Plugin Type:' select 'General Operation'. 
	- 'Bundled Program Files (optional)': add `emu_linux_mac.py` under 'Linux' or 'Mac OSX' respectively.
- Step 2: 
	- 'Sequence Type:' select 'Nucleotide only'.
	- 'Document Type:' select 'Unaligned Sequences (1+)'.
	- 'Command Line':
		`-o emu-combined-species-counts.tsv -g [inputFolderName] [otherOptions]`
	- Under 'Output' 'File Name:' `emu-combined-species-counts.tsv` and select 'Format:' 'Text file (plain)'
- Step 3:
	- Press 'Add' to add Docker path and path to user data as options (in this order).

## Workflow
`Emu.geneiousWorkflow`