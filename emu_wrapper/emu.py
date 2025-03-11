#!/usr/bin/env python3

import sys
import os
import subprocess
import shutil
import csv
import gzip
import configparser

# Outfile to be imported to Geneious
outFile = sys.argv[2]

# Temporary Geneious folder. Example linux: /Users/user/Geneious 2022.1 Data/transient/1660719270002/x/8/
# Example windows: D:\Geneious 2021.1 Data\transient\1677846391422\x\120
pathToGeneiousData = sys.argv[4]

# Config
config = configparser.ConfigParser()
config.read(sys.argv[6])
pathToDocker = config["SOFTWARE"]["pathToDocker"]

# In/out data folder selected by user
pathToData = sys.argv[8]
mountPath = os.path.join(pathToData, ":/geneious")

# Github version
gitVersion = config["SOFTWARE"]["gitVersion"]
# Docker images
kronaImage = config["SOFTWARE"]["kronaImage"]
emuImage = config["SOFTWARE"]["emuImage"]  # database included in image

# Build Emu command
seqType = config["EMU"]["seqType"]
dataBase = os.path.join("/emu_database", config["EMU"]["dataBase"])
minAbund = config["EMU"]["minAbund"]
alignN = config["EMU"]["alignN"]
batchK = config["EMU"]["batchK"]
noThreads = config["EMU"]["noThreads"]
emuBooleans = []
if config.getboolean("EMU", "keepCounts"):
    emuBooleans.append("--keep-counts")
if config.getboolean("EMU", "keepFiles"):
    emuBooleans.append("--keep-files")
if config.getboolean("EMU", "keepReadAssignments"):
    emuBooleans.append("--keep-read-assignments")
if config.getboolean("EMU", "outputUnclassified"):
    emuBooleans.append("--output-unclassified")

# Report
spikeTaxa = config["REPORT"]["spikeTaxa"]
minReads = config["REPORT"]["minReads"]
maxUnassignedProp = config["REPORT"]["maxUnassignedProp"]
minCountsTaxa = config["REPORT"]["minCountsTaxa"]
minAbundTot = config["REPORT"]["minAbundTot"]


def count_fasta(fastafile):
    if fastafile.endswith(".gz"):
        with gzip.open(fastafile, "rt") as file:
            no_fasta = sum(1 for line in file.read() if line.startswith(">"))
    else:
        with open(fastafile, "r") as file:
            no_fasta = sum(1 for line in file if line.startswith(">"))
    return no_fasta


# List of fasta files in data folder, create csv
inFiles = {}
for file in os.listdir(pathToData):
    if file.endswith((".fasta", ".fa", ".fasta.gz", ".fa.gz")):
        inFiles[file.split(".")[0]] = "".join(["/geneious/", file])
        # Must be linux format also in windows

        # Create CSV file with number of reads per fasta-file
        with open(os.path.join(pathToData, "fasta.csv"), "a", newline="") as csvfile:
            rowToWrite = [
                file.split(".")[0],  # basename
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

    # Add config params
    for section in config:
        confdict = dict(config[section])
        for param, value in confdict.items():
            writer.writerow([param, value])

    # Add data from containers
    writer.writerow(["emu_version", emuVersion.stdout.replace("'", "").strip()])
    writer.writerow(["krona_version", kronaVersion.stdout.replace("'", "").strip()])


# Run emu abundance for each sample
if len(inFiles) > 0:
    for sample, inFile in inFiles.items():
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
                "--type",
                seqType,
                "--db",
                dataBase,
                "--min-abundance",
                minAbund,
                "--N",
                alignN,
                "--K",
                batchK,
                "--threads",
                noThreads,
                "--output-dir",
                "/geneious",
                "--output-basename",
                sample,
            ]
            + emuBooleans
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

# Handle output files
for file in os.listdir(pathToData):
    # Compress intermediate files
    if file.endswith((".sam", ".fa", ".fasta")):
        with open(os.path.join(pathToData, file), "rb") as f_in:
            with gzip.open(str(os.path.join(pathToData, file) + ".gz"), "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
                f_in.close()
                f_out.close()
                os.remove(os.path.join(pathToData, file))

    # Copy combined output file to Geneious tmp folder
    if file.endswith("emu-combined-species-counts.tsv"):
        multiSampleOutput = file

        shutil.copyfile(
            os.path.join(pathToData, multiSampleOutput),
            os.path.join(pathToGeneiousData, outFile),
        )
