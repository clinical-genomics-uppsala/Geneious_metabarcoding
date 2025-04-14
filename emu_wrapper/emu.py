#!/usr/bin/env python3

import sys
import os
import subprocess
import shutil
import csv
import gzip
import configparser
import datetime
import posixpath

start_time = datetime.datetime.now()
error_counter = 0

# Outfile to be imported to Geneious
outfile = sys.argv[2]

# Temporary Geneious folder. Example linux: /Users/user/Geneious 2022.1 Data/transient/1660719270002/x/8/
# Example windows: D:\Geneious 2021.1 Data\transient\1677846391422\x\120
path_to_geneious_data = sys.argv[4]

# Config
config = configparser.ConfigParser()
config.read(sys.argv[6])
config_dict = {s: dict(config.items(s)) for s in config.sections()}

path_to_docker = config["SOFTWARE"]["path_to_docker"]

# In/out data folder selected by user
path_to_data = sys.argv[8]
mount_path = os.path.join(path_to_data, ":/geneious")

# Docker images
krona_image = config["SOFTWARE"]["krona_image"]
emu_image = config["SOFTWARE"]["emu_image"]  # database included in image

# Build Emu command
seq_type = config["EMU"]["seq_type"]
database = posixpath.join("/emu_database", config["EMU"]["database"])
min_abund = config["EMU"]["min_abund"]
align_n = config["EMU"]["align_n"]
batch_k = config["EMU"]["batch_k"]
no_threads = config["EMU"]["no_threads"]
emu_booleans = []
if config.getboolean("EMU", "keep_counts"):
    emu_booleans.append("--keep-counts")
if config.getboolean("EMU", "keep_files"):
    emu_booleans.append("--keep-files")
if config.getboolean("EMU", "keep_read_assignments"):
    emu_booleans.append("--keep-read-assignments")
if config.getboolean("EMU", "output_unclassified"):
    emu_booleans.append("--output-unclassified")


def run_subprocess(command, name):
    """Run subprocess command, print stdout, stderr, process name and exit status"""
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (output, error) = p.communicate()
    p_status = p.wait()
    print(output.decode())
    print(f"{name} exit status: {p_status} \n")
    return output, p_status


def get_version(dockerpath, image, label, name):
    """Get version from label in docker container, print stderr, process name and exit status"""
    command = [
        dockerpath,
        "inspect",
        "--format",
        f"'{{{{ index .Config.Labels \"{label}\"}}}}'",
        image,
    ]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (output, error) = p.communicate()
    p_status = p.wait()
    print(error.decode())
    print(f"{name} exit status: {p_status} \n")
    version = [name, output.decode().strip().replace('\'','')]
    return version, p_status


def count_fasta(fastafile):
    """Return the number of sequences in a (compresesed) fasta file"""
    if fastafile.endswith(".gz"):
        with gzip.open(fastafile, "rt") as file:
            no_fasta = sum(1 for line in file.read() if line.startswith(">"))
    else:
        with open(fastafile, "r") as file:
            no_fasta = sum(1 for line in file if line.startswith(">"))
    return no_fasta


# List fasta files in data folder, create fasta.csv
infiles = {}
with open(os.path.join(path_to_data, "fasta.csv"), "a", newline="") as csvfile:
    for file in os.listdir(path_to_data):
        if file.endswith((".fasta", ".fa", ".fasta.gz", ".fa.gz")):
            infiles[file.split(".")[0]] = "".join(["/geneious/", file])
            # Must be linux format also in windows

            # Write CSV file with number of reads per fasta file
            row_to_write = [
                file.split(".")[0],
                count_fasta(os.path.join(path_to_data, file)),
            ]
            writer = csv.writer(csvfile)
            writer.writerow(row_to_write)


# Run emu abundance for each sample
if len(infiles) > 0:
    for sample, infile in infiles.items():
        emu_abundance = [
            path_to_docker,
            "run",
            "--rm",
            "-v",
            mount_path,
            emu_image,
            "emu",
            "abundance",
            infile,
            "--type",
            seq_type,
            "--db",
            database,
            "--min-abundance",
            min_abund,
            "--N",
            align_n,
            "--K",
            batch_k,
            "--threads",
            no_threads,
            "--output-dir",
            "/geneious",
            "--output-basename",
            sample,
        ]
        emu_abundance.extend(emu_booleans)
        if run_subprocess(emu_abundance, "emu_abundance")[1] != 0:
            error_counter += 1
else:
    sys.exit("No fasta files in " + path_to_data + " (.fa/.fasta/.fa.gz./fasta.gz)")

# Krona plot
krona_import_taxonomy = (
    "ktImportTaxonomy -t 1 -m 14 -o /geneious/krona.html /geneious/*_rel-abundance.tsv"
)
krona_subprocess = [
    path_to_docker,
    "run",
    "--rm",
    "-v",
    mount_path,
    krona_image,
    "/bin/bash",
    "-c",
    krona_import_taxonomy,
]
if run_subprocess(krona_subprocess, "krona")[1] != 0:
    error_counter += 1

# Combine output and import in Geneious
# Run emu combine-outputs for selected folder - both relative abundance and counts
emu_combine_outputs = "emu combine-outputs /geneious species; emu combine-outputs --counts /geneious species"
combine_outputs_subprocess = [
    path_to_docker,
    "run",
    "--rm",
    "-v",
    mount_path,
    emu_image,
    "/bin/bash",
    "-c",
    emu_combine_outputs,
]
if run_subprocess(combine_outputs_subprocess, "combine_outputs")[1] != 0:
    error_counter += 1


# Get software versions
emu_version = get_version(path_to_docker, emu_image, "emu", "emu_version")
if emu_version[1] != 0:
    error_counter += 1

krona_version = get_version(path_to_docker, krona_image, "krona", "krona_version")
if krona_version[1] != 0:
    error_counter += 1

# Write versions.csv
with open(os.path.join(path_to_data, "versions.csv"), "a", newline="") as csvfile:
    writer = csv.writer(csvfile)

    # Add config params
    for section, params in config_dict.items():
        for param, value in params.items():
            writer.writerow([param, value])

    # Add data from containers
    writer.writerow(emu_version[0])
    writer.writerow(krona_version[0])


# Excel report
make_report = "cd geneious; python ../emu_report.py emu-combined-species-counts.tsv emu-combined-species.tsv emu.xlsx fasta.csv versions.csv"
report_subprocess = [
    path_to_docker,
    "run",
    "--rm",
    "-v",
    mount_path,
    emu_image,
    "/bin/bash",
    "-c",
    make_report,
]
if run_subprocess(report_subprocess, "report")[1] != 0:
    error_counter += 1

# Handle output files
for file in os.listdir(path_to_data):
    # Compress intermediate files
    if file.endswith((".sam", ".fa", ".fasta")):
        with open(os.path.join(path_to_data, file), "rb") as f_in:
            with gzip.open(
                str(os.path.join(path_to_data, file) + ".gz"), "wb"
            ) as f_out:
                shutil.copyfileobj(f_in, f_out)
                f_in.close()
                f_out.close()
                os.remove(os.path.join(path_to_data, file))

    # Copy combined output file to Geneious tmp folder
    if file.endswith("emu-combined-species-counts.tsv"):
        multi_sample_output = file

        shutil.copyfile(
            os.path.join(path_to_data, multi_sample_output),
            os.path.join(path_to_geneious_data, outfile),
        )

stop_time = datetime.datetime.now()
print(
    f"Geneious_metabarcoding completed {stop_time.strftime('%Y-%m-%d %H:%M:%S')} taking {stop_time - start_time}. Processed {len(infiles)} samples."
)
print(f"There were {error_counter} errors")
