#!/usr/bin/env python3

import os
import subprocess
import configparser
from datetime import datetime

report_date = datetime.today().strftime("%Y-%m-%d")

# Config
config = configparser.ConfigParser()
config.read("config.ini")

pathToDocker = config["DEFAULT"]["pathToDocker"]
emuImage = config["DEFAULT"]["emuImage"]
veganImage = config["DEFAULT"]["veganImage"]
pathToData = config["DEFAULT"]["pathToData"]

mountPath = os.path.join(pathToData, ":/usr/local/src/data")

# Run emu container combine-outputs
combineOutputs = "emu combine-outputs --counts /usr/local/src/data species"
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
rmarkdown = "rmarkdown::render(\"../rscripts/internal_control_log.Rmd\", output_file=\"/usr/local/src/data/" +str(report_date)+ "_16S_IK_logg.html\")"
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