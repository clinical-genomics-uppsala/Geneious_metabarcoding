# Internal control log

This internal control log is meant to monitor a multispecies positive control over multiple sequencing runs. The python script takes output files from [emu](https://github.com/treangenlab/emu) and makes PCA plots using the R package [vegan](https://cran.r-project.org/web/packages/vegan/index.html). When enough samples to calculate the standard deviation are included (set by stdev_no in the config file), 2 and 3 standard deviations are plotted using a custom version of the vegan ordiellipse function. 

In addition, the relative abundance of each positive control species are plotted over time, set by mock_spp in the config file.

Emu and vegan are run in docker containers and the output is an html report.


## Setup

Docker images: 
- Build the docker image for vegan, for example:
`docker build -f vegan.Dockerfile -t vegan:<label> .`  
- The emu image for the Geneious metabarcoding workflow is also needed, currently `hydragenetics/emu:3.5.4`.

## Usage

- Collect all `_rel-abundance.tsv` files from emu to be included in a folder (path_to_data). Important - samples should be named with dates to ensure the newest samples are highlighted in the plots.
- Adapt the `config.ini` file, example for Windows:
```[DEFAULT]
github = Geneious_metabarcoding version
path_to_docker = C:\Program Files\Docker\Docker\resources\bin\docker.exe
emu_image = hydragenetics/emu:<label>
vegan_image = vegan:<label>
rscript = internal_control_log.Rmd
path_to_data = /path/to/data
stdev_no = 20
mock_spp = ["Staphylococcus saprophyticus", "Cutibacterium avidum", "Streptococcus equi", "Imtechella halotolerans", "Allobacillus halotolerans", "Truepera radiovictrix"]
```  
- Start the `internal_control_log.py` script in the terminal or by double-clicking on it (Windows). The `config.ini` and `internal_control_log.Rmd` files must be located in the same folder as the python script.
