#!/usr/bin/env python3

import sys
import os
import subprocess
import shutil
import glob

# Geneious input/output and options
inFile = os.path.join("/geneious", sys.argv[2])
outFile = os.path.join("/geneious", sys.argv[4])

# Temporary Geneious folder. Example: /Users/user/Geneious 2022.1 Data/transient/1660719270002/x/8/
pathToGeneiousData = sys.argv[6]
mountPath = os.path.join(pathToGeneiousData, ":/geneious")

pathToDocker = sys.argv[8]
pathToOutData = sys.argv[10]

# Sample path
pathToSample = sys.argv[12]

# Run emu docker container
subprocess.run( [pathToDocker, "run", "--rm", "-v", mountPath, "emu3.4.4_image", \
    "emu", "abundance", inFile, \
    "--db", "/tmp/geneious/emu-database", \
    "--keep-counts", "--keep-files", "--keep-read-assignments", "--output-unclassified", \
    "--output-dir", "/geneious"] )


# Get sample name & clean sample dir
for f in os.listdir(pathToSample):
    if ".sample" in f:
        sample_name = f
        os.remove(os.path.join(pathToSample,f))


# Rename files - replace "input." with sample name
for file_name in os.listdir(pathToGeneiousData):
    if ".fastq.gz" not in file_name:
        if "input." in file_name:
            new_name = sample_name + "_" + file_name.split("input.")[1]
            shutil.copyfile(file_name, os.path.join(pathToOutData, new_name))