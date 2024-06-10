#!/usr/bin/env python3

import sys
import os
import subprocess
import shutil
import glob
import csv
import gzip

# Outfile to be imported to Geneious
outFile = sys.argv[2]

# Temporary Geneious folder. Example linux: /Users/user/Geneious 2022.1 Data/transient/1660719270002/x/8/
# Example windows: D:\Geneious 2021.1 Data\transient\1677846391422\x\120
pathToGeneiousData = sys.argv[4]

pathToDocker = sys.argv[6]

# In/out data folder selected by user
pathToData = sys.argv[8]
mountPath = os.path.join(pathToData, ":/geneious")

# Krona
kronaImage = sys.argv[10]
# Emu options
emuImage = sys.argv[12]  # database included in image
noThreads = sys.argv[14]


def count_fasta(fastafile):
    if fastafile.endswith(".gz"):
        with gzip.open(fastafile, "rt") as file:
            no_fasta = sum(1 for line in file.read() if line.startswith(">"))
    else:
        with open(fastafile, "r") as file:
            no_fasta = sum(1 for line in file if line.startswith(">"))
    return no_fasta


# List of fasta files in data folder, create csv
inFiles = []
for file in os.listdir(pathToData):
    if file.endswith((".fasta", ".fa", ".fasta.gz", ".fa.gz")):
        inFiles.append(
            "".join(["/geneious/", file])
        )  # Must be linux format also in windows

        # Create CSV file with number of reads per fasta-file
        with open(os.path.join(pathToData, "fasta.csv"), "a", newline="") as csvfile:
            rowToWrite = [
                file.rsplit(".", 1)[0],  # split on last . match emu behaviour = .gz files get .fasta/.fastq in headers
                count_fasta(os.path.join(pathToData, file)),
            ]
            writer = csv.writer(csvfile)
            writer.writerow(rowToWrite)

# Create CSV for software versions
with open(os.path.join(pathToData, "versions.csv"), "a", newline="") as csvfile:
    writer = csv.writer(csvfile)
    emuVersion = subprocess.run(
        [
            pathToDocker,
            "inspect",
            "--format",
            "'{{ index .Config.Labels \"version\"}}'",
            emuImage,
        ],
        capture_output=True,
        text=True,
    )
    kronaVersion = subprocess.run(
        [
            pathToDocker,
            "inspect",
            "--format",
            "'{{ index .Config.Labels \"version\"}}'",
            kronaImage,
        ],
        capture_output=True,
        text=True,
    )
    writer.writerow(["emu_image", emuImage])
    writer.writerow(["emu_version", emuVersion.stdout.replace("'", "").strip()])
    writer.writerow(["krona_image", kronaImage])
    writer.writerow(["krona_version", kronaVersion.stdout.replace("'", "").strip()])

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
    sys.exit("No fasta files in " + pathToData + " (.fa/.fasta/.fa.gz./fasta.gz)")


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
        kronaImage,
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
makeReport = "cd geneious; python ../emu_report.py emu-combined-species-counts.tsv emu-combined-species.tsv emu.xlsx fasta.csv versions.csv"
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
