#!/usr/bin/env python3

import os
import posixpath
import subprocess
import configparser
from datetime import datetime

# Config
config = configparser.ConfigParser()
config.read("config.ini")

github = config["DEFAULT"]["github"]
pathToDocker = config["DEFAULT"]["pathToDocker"]
emuImage = config["DEFAULT"]["emuImage"]
veganImage = config["DEFAULT"]["veganImage"]
pathToData = config["DEFAULT"]["pathToData"]

# Used to check if report name is unique
def unique_filename(path):
    filename, extension = os.path.splitext(path)
    counter = 1
    while os.path.exists(path):
        path = filename + "_" + str(counter) + extension
        counter += 1
    return path

# Convert windows paths docker & R compatible paths
if os.name == "nt":
    try:
        containerPath = pathToData.replace("\\","/").split(":")[1] 
    except IndexError:
        containerPath = pathToData.replace("\\","/")
else:
    containerPath = pathToData

# Paths
mountPath = os.path.join(pathToData, f':{containerPath}')
emu_file_path = posixpath.join(containerPath, 'emu-combined-species-counts.tsv')
report_path = unique_filename(posixpath.join(containerPath, str(datetime.today().strftime("%Y-%m-%d")) + "_16S_IK_logg.html"))

# Run emu container combine-outputs
combineOutputs = f'emu combine-outputs --counts {containerPath} species'
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
rmarkdown = f"rmarkdown::render(\'/usr/local/src/rscripts/internal_control_log.Rmd\', params=list(emu='{emu_file_path}',github='{github}'), output_file='{report_path}')"
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
