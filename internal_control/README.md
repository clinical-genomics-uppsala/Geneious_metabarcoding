# Internal control log

This internal control log is meant to monitor a multispecies positive control over multiple sequencing runs. The python script takes output files from [Emu](https://github.com/treangenlab/emu) and makes PCA plots using the R package [vegan](https://cran.r-project.org/web/packages/vegan/index.html). When more than 20 samples are included, 2 and 3 standard deviations are plotted using a custom version of the vegan ordiellipse function. Emu and vegan are run in docker containers and the output is an html report.

Important - samples should be named with dates to ensure the newest samples are highlighted in the plots.

## Setup

Docker images: 
- Build the docker image for vegan, for example:
`docker build -f vegan.Dockerfile -t vegan:2024-12-12 .`  
- The emu image for the Geneious metabarcoding workflow is also needed, if not already available, see instructions [here](https://github.com/clinical-genomics-uppsala/Geneious_metabarcoding#build-docker-images-for-emu-and-krona) .

## Usage

- Collect all `_rel-abundance.tsv` files from emu to be included in a folder.
- Adapt the `config.ini` file, example:
```[DEFAULT]
pathToDocker = C:\Program Files\Docker\Docker\resources\bin\docker.exe
emuImage = emu:2024-12-16
veganImage = vegan:2024-12-12
pathToData = X:\path\to\folder\with\emu\files
```  
- Start the python script in the terminal or by double-clicking on it (Windows).
