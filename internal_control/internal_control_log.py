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
path_to_docker = config["DEFAULT"]["path_to_docker"]
emu_image = config["DEFAULT"]["emu_image"]
vegan_image = config["DEFAULT"]["vegan_image"]
rscript = config["DEFAULT"]["rscript"]
path_to_data = config["DEFAULT"]["path_to_data"]
stdev_no = config["DEFAULT"]["stdev_no"]
mock_spp = config["DEFAULT"]["mock_spp"]

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
        container_path = path_to_data.replace("\\","/").split(":")[1] 
    except IndexError:
        container_path = path_to_data.replace("\\","/")
else:
    container_path = path_to_data

# Paths
plugin_path = os.path.dirname(__file__)
mount_path = os.path.join(path_to_data, f':{container_path}')
emu_file_path = posixpath.join(container_path, 'emu-combined-species-counts.tsv')
report_path = unique_filename(posixpath.join(container_path, str(datetime.today().strftime("%Y-%m-%d")) + "_16S_IK_logg.html"))

# Run emu container combine-outputs
combine_outputs = f'emu combine-outputs --counts {container_path} species'
subprocess.run(
   [
       path_to_docker,
       "run",
       "--rm",
       "-v",
       mount_path,
       emu_image,
       "/bin/bash",
       "-c",
       combine_outputs
   ]
)

# Run vegan container
rscript_path = posixpath.join("/scripts", rscript)
rmarkdown = f"rmarkdown::render(\'{rscript_path}\', params=list(emu='{emu_file_path}', github='{github}', STDEV_NO='{stdev_no}', MOCK_SPP='{mock_spp}'), output_file='{report_path}')"
subprocess.run(
    [
        path_to_docker,
        "run",
        "--rm",
        "-v",
        mount_path,
        "-v",
        os.path.join(plugin_path,":/scripts"),
        vegan_image,
        "Rscript",
        "-e",
        rmarkdown
    ]
)
