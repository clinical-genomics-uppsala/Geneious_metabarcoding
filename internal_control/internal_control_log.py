#!/usr/bin/env python3

import os
import subprocess
import configparser
from datetime import datetime

# Config
config = configparser.ConfigParser()
config.read("config.ini")

pathToDocker = config["DEFAULT"]["pathToDocker"]
emuImage = config["DEFAULT"]["emuImage"]
veganImage = config["DEFAULT"]["veganImage"]
pathToData = config["DEFAULT"]["pathToData"]

mountPath = os.path.join(pathToData, f':{pathToData}')

emu_file_path = os.path.join(pathToData, 'emu-combined-species-counts.tsv')
report_name = str(datetime.today().strftime("%Y-%m-%d")) + "_16S_IK_logg.html"

# Used to check if report name is unique
def unique_filename(path):
    filename, extension = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = filename + "_" + str(counter) + extension
        counter += 1
    return path

# Run emu container combine-outputs
combineOutputs = f'emu combine-outputs --counts {pathToData} species'
subprocess.run(
   [
       pathToDocker,
       "run",
       "--rm",
       "-v",
       mountPath,
       emuImage,
       "/bin/bash",
       "-c",
       combineOutputs
   ]
)

# Run vegan container
unique_name_path = unique_filename(os.path.join(pathToData, report_name))
rmarkdown = f"rmarkdown::render(\'/usr/local/src/rscripts/internal_control_log.Rmd\', params=list(args='{emu_file_path}'), output_file='{unique_name_path}')"
subprocess.run(
    [
        pathToDocker,
        "run",
        "--rm",
        "-v",
        mountPath,
        veganImage,
        "Rscript",
        "-e",
        rmarkdown
    ]
)
