#!/usr/bin/env python3

import sys
import os
import subprocess
import shutil
import glob

# Outfile to be imported to Geneious
outFile = sys.argv[2]

# Temporary Geneious folder. Example linux: /Users/user/Geneious 2022.1 Data/transient/1660719270002/x/8/
# Example windows: D:\Geneious 2021.1 Data\transient\1677846391422\x\120
pathToGeneiousData = sys.argv[4]

pathToDocker = sys.argv[6]

# In/out data folder selected by user
pathToData = sys.argv[8]
mountPath = os.path.join(pathToData, ":/geneious")

# Emu options
emuImage = sys.argv[10]  # database included in image
noThreads = sys.argv[12]


# List of fasta files in data folder
inFiles = []
for file in os.listdir(pathToData):
    if file.endswith(".fasta"):
        inFiles.append(
            "".join(["/geneious/", file])
        )  # Must be linux format also in windows

# Run emu abundance for each sample
if len(inFiles) > 0:
    for inFile in inFiles:
        subprocess.run(
            [
                pathToDocker,
                "run",
                "--rm",
                "-v",
                mountPath,
                emuImage,
                "emu",
                "abundance",
                inFile,
                "--keep-counts",
                "--keep-files",
                "--keep-read-assignments",
                "--output-unclassified",
                "--threads",
                noThreads,
                "--output-dir",
                "/geneious",
            ]
        )
else:
    sys.exit("No fasta files in " + pathToData)


# Krona plot
kronaCmd = (
    "ktImportTaxonomy -t 1 -m 14 -o /geneious/krona.html /geneious/*_rel-abundance.tsv"
)
subprocess.run(
    [
        pathToDocker,
        "run",
        "--rm",
        "-v",
        mountPath,
        "krona:2.8",
        "/bin/bash",
        "-c",
        kronaCmd,
    ]
)

# Combine output and import in Geneious
# Run emu combine-outputs for selected folder - both relative abundance and counts
combineOutputs = "emu combine-outputs /geneious species; emu combine-outputs --counts /geneious species"
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
        combineOutputs,
    ]
)


# Excel report
makeReport = "cd geneious; python ../emu_report.py emu-combined-species-counts.tsv emu-combined-species.tsv emu.xlsx"
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
        makeReport,
    ]
)

# Copy combined output file to Geneious tmp folder
for file in os.listdir(pathToData):
    if file.endswith("emu-combined-species-counts.tsv"):
        multiSampleOutput = file

        shutil.copyfile(
            os.path.join(pathToData, multiSampleOutput),
            os.path.join(pathToGeneiousData, outFile),
        )
