#!/usr/bin/env python3

import sys
import os
import glob

import pandas as pd
import numpy as np
import xlsxwriter
import pandas.io.formats.excel

pandas.io.formats.excel.ExcelFormatter.header_style = None


##### INPUT FILES #####
if len(sys.argv) >= 3:
    count_file = sys.argv[1]
    ra_file = sys.argv[2]
    output_excel = sys.argv[3]
    csv_file = sys.argv[4]
    version_file = sys.argv[5]
else:
    count_file = "data/emu-combined-species-counts.tsv"
    ra_file = "data/emu-combined-species.tsv"
    output_excel = "data/emu.xlsx"
    csv_file = "data/fasta.csv"
    version_file = "data/versions.csv"


##### READING #####


# Sort dataframe by sample columns and most abundant taxa
# Sample names should start with barcode no: 01, 02, 03..... or with barcode49, barcode27 etc.
def sort_samples(df, sortabund):
    header = df.columns.values.tolist()
    taxonomy = [
        name for name in header if not name[0].isdigit() if not "barcode" in name
    ]

    # sort sample columns by name, not taxonomy
    samples = np.sort(df.columns.difference(taxonomy)).tolist()
    # remove columns with threshold - duplicates
    samples = [sample for sample in samples if "threshold" not in sample]

    df = df.loc[:, taxonomy + samples].set_index(taxonomy)  # taxonomy as index columns

    if sortabund == "yes":
        # Remove and save unassigned row
        unassigned = df.iloc[-1, :]
        df = df.iloc[:-1, :]
        # Add temporary row sum column for sorting
        df = (
            df.assign(sum=df.sum(axis=1))
            .sort_values(by="sum", ascending=False)
            .drop(["sum"], axis=1)
        )

        # For qc sheet - number of assigned/unassigned reads per samples
        qc = df.sum(axis=0, numeric_only=True)
        qc = pd.DataFrame(qc, columns=["#assigned"])
        qc["#unassigned"] = unassigned

        df = df.append(
            unassigned
        )  # The frame.append method is deprecated and will be removed from pandas in a future version. Use pandas.concat instead.

        return (df, qc)

    else:
        return df


# COUNTS EMU - tsv
count_data = pd.read_csv(count_file, sep="\t", header=0)
count_data, qc = sort_samples(count_data, "yes")
count_header = count_data.columns.values.tolist()
df2 = count_data

# RELATIVE ABUNDANCE EMU - tsv
ra_data = pd.read_csv(ra_file, sep="\t", header=0)
ra_data = sort_samples(ra_data, "no")
ra_header = ra_data.columns.values.tolist()
ra_data = ra_data.reindex(count_data.index)  # same sorting as count sheet (abundance)
df3 = ra_data

# QC SHEET
# CSV file with information from fasta files
qc_csv = pd.read_csv(csv_file, sep=",", index_col=0, names=["#filtered"])
# Assigned/unassigned from count sheet
qc_csv = pd.concat([qc_csv, qc], axis=1).sort_index()
qc_csv["prop_assigned"] = qc_csv["#assigned"] / qc_csv["#filtered"]
# Report date
qc_csv["report_date"] = pd.Timestamp.today()
# Software versions
versions_csv = pd.read_csv(version_file, sep=",", header=None)
versions_csv = dict(versions_csv.to_numpy())
for software, version in versions_csv.items():
    qc_csv[software] = version
df1 = qc_csv


##### WRITING TO EXCEL FILE #####
writer = pd.ExcelWriter(output_excel)

df1.to_excel(writer, sheet_name="qc", index=True)
df2.to_excel(writer, sheet_name="emu_counts", index=True)
df3.to_excel(writer, sheet_name="emu_proportions", index=True)

workbook = writer.book


##### FORMATTING ####
# Left-adjust cells
align_cells = workbook.add_format()
align_cells.set_align("left")

# Set format of header and index
bold_format = workbook.add_format({"bold": "True"})

for worksheet in workbook.worksheets():
    worksheet.set_column("A:A", 25, bold_format)  # width of cell
    worksheet.set_row(0, 15, bold_format)  # default row height
    worksheet.freeze_panes(1, 1)

writer.save()  # writer.save() # Will be removed in a future version
