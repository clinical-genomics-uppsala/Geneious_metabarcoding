#!/usr/bin/env python3

import sys
import os
import subprocess
import shutil

# Geneious input/output and options
inFile = os.path.join("/geneious", sys.argv[2])
outFile = os.path.join("/geneious", sys.argv[4])

# Temporary Geneious folder. Example: /Users/user/Geneious 2022.1 Data/transient/1660719270002/x/8/
pathToGeneiousData = sys.argv[6]
mountPath = os.path.join(pathToGeneiousData, ":/geneious")

pathToDocker = sys.argv[8]
pathToOutData = sys.argv[10]

# Run emu docker container
subprocess.run( [pathToDocker, "run", "--rm", "-v", mountPath, "emu3.4.4_image", \
    "emu", "abundance", inFile, \
    "--db", "/tmp/geneious/emu-database", \
    "--keep-counts", "--keep-files", "--keep-read-assignments", "--output-unclassified", \
    "--output-dir", "/geneious"] )


# Copy outfiles to user selected folder
shutil.copytree(pathToGeneiousData, pathToOutData, ignore=shutil.ignore_patterns('*.fastq.gz'), dirs_exist_ok=True)

